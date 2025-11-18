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


# Mapbox API configuration
MAPBOX_BASE_URL = "https://api.mapbox.com"


@tool(parse_docstring=True)
def mapbox_geocode_tool(address: str, country: str = None) -> Dict[str, Any]:
    """Convert address to coordinates using Mapbox Geocoding API v6.
    
    Args:
        address: Property address to geocode (can be address, landmark, or place name)
        country: Optional ISO 3166 alpha-2 country code (e.g., 'NG' for Nigeria, 'US' for USA)
    """
    api_key = os.getenv("MAPBOX_API_KEY")
    if not api_key:
        raise ValueError("MAPBOX_API_KEY environment variable is not set")
    
    try:
        url = f"{MAPBOX_BASE_URL}/search/geocode/v6/forward"
        params = {
            "q": address,
            "access_token": api_key,
            "limit": 1,
            "autocomplete": "false"
        }
        
        if country:
            params["country"] = country.upper()
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("features"):
            return {
                "success": False,
                "error": "Address not found"
            }
        
        feature = data["features"][0]
        coordinates = feature["geometry"]["coordinates"]
        properties = feature.get("properties", {})
        
        return {
            "success": True,
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "formatted_address": properties.get("full_address") or properties.get("place_formatted", address),
            "name": properties.get("name", ""),
            "context": properties.get("context", {})
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": "Address not found"}
        raise Exception(f"Mapbox geocoding API error: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Mapbox geocoding request failed: {str(e)}")


@tool(parse_docstring=True)
def mapbox_nearby_tool(
    latitude: float,
    longitude: float,
    category: str,
    radius_meters: int = 5000,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Find nearby points of interest using Mapbox Search Box API.
    
    Args:
        latitude: Property latitude
        longitude: Property longitude
        category: POI category (e.g., "restaurant", "cafe", "coffee", "park", "shopping", "school", "hospital", "gym")
        radius_meters: Search radius in meters (default 5000m = 5km) - used to filter results after retrieval
        limit: Maximum number of results (max 25)
    """
    api_key = os.getenv("MAPBOX_API_KEY")
    if not api_key:
        raise ValueError("MAPBOX_API_KEY environment variable is not set")
    
    try:
        url = f"{MAPBOX_BASE_URL}/search/searchbox/v1/category/{category}"
        
        # Calculate generous bounding box (1.5x radius to avoid edge exclusions)
        # 1 degree latitude ≈ 111km, longitude varies by latitude
        bbox_radius = radius_meters * 1.5
        lat_offset = (bbox_radius / 1000) / 111.0
        lon_offset = (bbox_radius / 1000) / (111.0 * abs(cos(radians(latitude))))
        
        bbox = f"{longitude - lon_offset},{latitude - lat_offset},{longitude + lon_offset},{latitude + lat_offset}"
        
        params = {
            "access_token": api_key,
            "proximity": f"{longitude},{latitude}",
            "bbox": bbox,
            "limit": min(limit, 25),
            "language": "en"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pois = []
        for feature in data.get("features", []):
            poi_coords = feature["geometry"]["coordinates"]
            props = feature.get("properties", {})
            
            distance = calculate_distance(
                latitude, longitude,
                poi_coords[1], poi_coords[0]
            )
            
            if distance <= radius_meters:
                pois.append({
                    "name": props.get("name", "Unknown"),
                    "category": category,
                    "distance_meters": round(distance, 2),
                    "latitude": poi_coords[1],
                    "longitude": poi_coords[0],
                    "address": props.get("full_address") or props.get("place_formatted", ""),
                    "maki_icon": props.get("maki", ""),
                    "poi_categories": props.get("poi_category", [])
                })
        
        return pois
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return []
        raise Exception(f"Mapbox nearby search API error: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Mapbox nearby search request failed: {str(e)}")


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