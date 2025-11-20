"""
Tools for AI Real Estate Co-Pilot.

This module provides external API integrations including Tavily search
for property listings and Mapbox for location services.
"""

import os
import requests
from typing import Dict, Any, List
from math import radians, sin, cos, sqrt, atan2
from tavily import TavilyClient
from langchain_core.tools import tool
from langchain_tavily import TavilyExtract 
from langchain_tavily import TavilySearch


# Import the Pydantic models needed for tool schemas
from src.models import PropertyForReview, PropertyReport



@tool(parse_docstring=True)
def tavily_search_tool(
    query: str,
    max_results: int = 5
) -> Dict[str, Any]:
    """Search for property listings using Tavily API to find URLs of individual properties.
    
    Args:
        query: Search query for property listings.
        max_results: Maximum number of result URLs to return.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )
        return response
    except Exception as e:
        raise Exception(f"Tavily search failed: {str(e)}")


@tool(parse_docstring=True)
def tavily_extract_tool(urls: List[str]) -> Dict[str, Any]:
    """Extract detailed content and images from a list of property URLs using Tavily API.
    
    Args:
        urls: A list of URLs to extract content from.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
        
    try:
        # Instantiate the extractor tool with advanced depth
        extractor = TavilyExtract(
            api_key=api_key, 
            include_images=True, 
            extract_depth="advanced"
        )
        # Invoke it with the provided URLs
        response = extractor.invoke({"urls": urls})
        return response
    except Exception as e:
        raise Exception(f"Tavily extraction failed: {str(e)}")


# Google Places API configuration
GOOGLE_PLACES_BASE_URL = "https://places.googleapis.com/v1"


@tool(parse_docstring=True)
def google_places_geocode_tool(address: str, country: str = None) -> Dict[str, Any]:
    """Convert address to coordinates using Google Places Text Search API.
    
    Args:
        address: Property address to geocode (can be address, landmark, or place name)
        country: Optional ISO 3166 alpha-2 country code (e.g., 'NG' for Nigeria, 'US' for USA)
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
    
    try:
        url = f"{GOOGLE_PLACES_BASE_URL}/places:searchText"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location"
        }
        
        body = {
            "textQuery": address
        }
        
        if country:
            body["regionCode"] = country.upper()
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("places") or len(data["places"]) == 0:
            return {
                "success": False,
                "error": "Address not found"
            }
        
        place = data["places"][0]
        location = place.get("location", {})
        
        return {
            "success": True,
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "formatted_address": place.get("formattedAddress", address),
            "name": place.get("displayName", {}).get("text", ""),
            "place_id": place.get("id", "")
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": "Address not found"}
        raise Exception(f"Google Places geocoding API error: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Google Places geocoding request failed: {str(e)}")


@tool(parse_docstring=True)
def google_places_nearby_tool(
    latitude: float,
    longitude: float,
    category: str,
    radius_meters: int = 5000,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Find nearby points of interest using Google Places Nearby Search API.
    
    Args:
        latitude: Property latitude
        longitude: Property longitude
        category: POI category (e.g., "restaurant", "cafe", "park", "school", "hospital", "gym", "shopping_mall", "transit_station")
        radius_meters: Search radius in meters (default 5000m = 5km, max 50000m)
        limit: Maximum number of results (max 20)
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
    
    try:
        url = f"{GOOGLE_PLACES_BASE_URL}/places:searchNearby"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount"
        }
        
        body = {
            "includedTypes": [category],
            "maxResultCount": min(limit, 20),
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": min(radius_meters, 50000.0)
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pois = []
        for place in data.get("places", []):
            place_location = place.get("location", {})
            place_lat = place_location.get("latitude")
            place_lon = place_location.get("longitude")
            
            if place_lat is None or place_lon is None:
                continue
            
            distance = calculate_distance(
                latitude, longitude,
                place_lat, place_lon
            )
            
            pois.append({
                "name": place.get("displayName", {}).get("text", "Unknown"),
                "category": category,
                "distance_meters": round(distance, 2),
                "latitude": place_lat,
                "longitude": place_lon,
                "address": place.get("formattedAddress", ""),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("userRatingCount", 0),
                "place_id": place.get("id", "")
            })
        
        return pois
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return []
        raise Exception(f"Google Places nearby search API error: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Google Places nearby search request failed: {str(e)}")


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Distance in meters
    """
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    # Haversine formula
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    
    return distance



@tool(parse_docstring=True)
def present_properties_for_review_tool(properties: List[PropertyForReview]) -> dict:
    """Present properties to user for review and approval.
    
    This tool triggers a human-in-the-loop interrupt by using LangGraph's interrupt() function.
    The user will see each property with yes/no options to approve or reject.
    
    Args:
        properties: List of property objects with keys: id, address, price, bedrooms, bathrooms, image_urls
    """
    from langgraph.types import interrupt
    
    # Trigger interrupt with property data
    # Frontend will receive this in __interrupt__ field
    user_decisions = interrupt({
        "type": "property_review",
        "properties": [p.dict() for p in properties], # Convert Pydantic models to dicts for the interrupt
        "message": "Please review each property and select Yes or No"
    })
    
    # When resumed with Command(resume=...), user_decisions will contain the response
    # Expected format: {"approved": ["prop_001", "prop_002"], "rejected": ["prop_003"]}
    return user_decisions


@tool
def submit_final_report_tool(report: PropertyReport) -> str:
    """
    Submit the final, comprehensive property report once all research and analysis is complete.
    This should be the last action taken by the agent.
    
    Args:
        report: The complete PropertyReport object containing all gathered data.
    """
    # In a real application, this might save the report to a database or file.
    # For the agent's purpose, just confirming submission is enough.
    return "Final report submitted successfully. The user can now view the results."