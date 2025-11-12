"""
Tools for AI Real Estate Co-Pilot.

This module provides external API integrations including Tavily search
for property listings and Mapbox for location services.
"""

import os
import requests
from typing import Dict, Any, List, Tuple
from math import radians, sin, cos, sqrt, atan2
from tavily import TavilyClient


def tavily_search_tool(
    query: str,
    max_results: int = 10,
    search_depth: str = "advanced",
    include_images: bool = True
) -> Dict[str, Any]:
    """
    Search for property listings using Tavily API.
    
    Args:
        query: Search query for property listings
        max_results: Maximum number of results to return
        search_depth: Search depth - "basic" or "advanced"
        include_images: Include image URLs from results
        
    Returns:
        Dictionary with search results including images
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_images=include_images
        )
        return response
    except Exception as e:
        raise Exception(f"Tavily search failed: {str(e)}")


# Mapbox API configuration
MAPBOX_BASE_URL = "https://api.mapbox.com"


def mapbox_geocode_tool(address: str) -> Dict[str, Any]:
    """
    Convert address to coordinates using Mapbox Geocoding API.
    
    Args:
        address: Property address to geocode
        
    Returns:
        Dictionary with coordinates and formatted address
    """
    api_key = os.getenv("MAPBOX_API_KEY")
    if not api_key:
        raise ValueError("MAPBOX_API_KEY environment variable is not set")
    
    try:
        # Mapbox Geocoding API endpoint
        url = f"{MAPBOX_BASE_URL}/geocoding/v5/mapbox.places/{requests.utils.quote(address)}.json"
        params = {
            "access_token": api_key,
            "limit": 1
        }
        
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
        
        return {
            "success": True,
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "formatted_address": feature.get("place_name", address),
            "context": feature.get("context", [])
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Mapbox geocoding failed: {str(e)}")


def mapbox_nearby_tool(
    latitude: float,
    longitude: float,
    category: str,
    radius: int = 5000,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find nearby points of interest using Mapbox Search Box API.
    
    Args:
        latitude: Property latitude
        longitude: Property longitude
        category: POI category (e.g., "restaurant", "cafe", "park", "shopping", "transit")
        radius: Search radius in meters (default 5000m = 5km)
        limit: Maximum number of results
        
    Returns:
        List of nearby POIs with name, category, distance, and coordinates
    """
    api_key = os.getenv("MAPBOX_API_KEY")
    if not api_key:
        raise ValueError("MAPBOX_API_KEY environment variable is not set")
    
    try:
        # Mapbox Search Box API endpoint for category search
        url = f"{MAPBOX_BASE_URL}/search/searchbox/v1/category/{category}"
        params = {
            "access_token": api_key,
            "proximity": f"{longitude},{latitude}",
            "limit": limit,
            "language": "en"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pois = []
        for feature in data.get("features", []):
            poi_coords = feature["geometry"]["coordinates"]
            distance = calculate_distance(
                latitude, longitude,
                poi_coords[1], poi_coords[0]
            )
            
            # Filter by radius
            if distance <= radius:
                pois.append({
                    "name": feature["properties"].get("name", "Unknown"),
                    "category": category,
                    "distance_meters": round(distance, 2),
                    "latitude": poi_coords[1],
                    "longitude": poi_coords[0],
                    "address": feature["properties"].get("full_address", ""),
                    "maki_icon": feature["properties"].get("maki", "")
                })
        
        return pois
    except requests.exceptions.RequestException as e:
        raise Exception(f"Mapbox nearby search failed: {str(e)}")


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
