"""
Tools for AI Real Estate Co-Pilot.

This module provides external API integrations including Tavily search
for property listings, Google Places for location services, and Gemini for Halloween decorations.
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
    
    Uses advanced extraction depth for better image and content retrieval from property sites.
    Images are returned in the 'images' field of each result.
    
    Args:
        urls: A list of URLs to extract content from.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
        
    try:
        client = TavilyClient(api_key=api_key)
        
        # Use the native Tavily client extract method with advanced depth
        # This provides better image extraction than the LangChain wrapper
        response = client.extract(
            urls=urls,
            include_images=True,
            extract_depth="advanced"
        )
        
        # Process results to ensure images are properly extracted
        processed_results = []
        for result in response.get('results', []):
            processed_result = {
                "url": result.get("url", ""),
                "raw_content": result.get("raw_content", ""),
                "images": result.get("images", []),
            }
            processed_results.append(processed_result)
        
        return {
            "results": processed_results,
            "failed_results": response.get("failed_results", [])
        }
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


# Halloween Decorator Tools

@tool(parse_docstring=True)
def analyze_property_images_tool(image_url: str) -> Dict[str, Any]:
    """Analyze property images using Gemini Vision to identify rooms and decoration opportunities.
    
    Args:
        image_url: URL of the property image to analyze
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(response.content))
        
        prompt = """Analyze this property image for Halloween decoration opportunities.
        
        Identify:
        1. Room type (living room, bedroom, porch, entryway, etc.)
        2. Available spaces for decorations (walls, corners, windows, doorways)
        3. Existing furniture and layout
        4. Style and color scheme
        5. Specific decoration suggestions (where to place items)
        
        Return a JSON object with: room_type, decoration_spaces, style_notes, suggestions"""
        
        response = model.generate_content([prompt, image])
        
        return {
            "success": True,
            "analysis": response.text,
            "image_url": image_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Image analysis failed: {str(e)}"
        }


@tool(parse_docstring=True)
def generate_decorated_image_tool(
    image_url: str,
    decoration_description: str
) -> Dict[str, Any]:
    """Generate decorated version of property image using Gemini Image Generation (Nano Banana).
    
    Args:
        image_url: URL of the original property image
        decoration_description: Description of Halloween decorations to add
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    try:
        import google.generativeai as genai
        import base64
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-image')
        
        # Download original image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(response.content))
        
        # Create prompt for image editing
        prompt = f"""Using the provided property image, add tasteful Halloween decorations to create a spooky but elegant atmosphere.
        
        Add these decorations: {decoration_description}
        
        Make sure the decorations:
        - Look realistic and naturally placed
        - Match the room's style and lighting
        - Are festive but not overwhelming
        - Enhance the property's appeal
        
        Keep the original room structure and furniture unchanged."""
        
        response = model.generate_content([prompt, image])
        
        # Extract generated image
        decorated_image_base64 = None
        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                decorated_image_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                break
        
        return {
            "success": True,
            "decorated_image_base64": decorated_image_base64,
            "original_image_url": image_url,
            "decorations_added": decoration_description
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Image generation failed: {str(e)}"
        }



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
def submit_final_report_tool(report: PropertyReport) -> dict:
    """
    Submit the final, comprehensive property report once all research and analysis is complete.
    This should be the last action taken by the agent.
    
    Returns both structured JSON data and a markdown-formatted report for display.
    
    Args:
        report: The complete PropertyReport object containing all gathered data.
    """
    report_dict = report.dict()
    
    # Generate markdown version for display
    md_lines = [
        f"# Property Search Report",
        f"",
        f"**Generated:** {report.generated_at.strftime('%B %d, %Y at %I:%M %p') if report.generated_at else 'N/A'}",
        f"",
        f"## Summary",
        f"{report.summary}",
        f"",
        f"---",
        f""
    ]
    
    for i, prop in enumerate(report.properties, 1):
        md_lines.append(f"## Property {i}: {prop.address}")
        md_lines.append(f"**Location:** {prop.city}, {prop.state} {prop.zip_code}")
        md_lines.append(f"**Price:** ₦{prop.price:,.0f}" if prop.price else "**Price:** N/A")
        md_lines.append(f"**Bedrooms:** {prop.bedrooms} | **Bathrooms:** {prop.bathrooms} | **Size:** {prop.square_feet:,} sq ft" if prop.square_feet else "")
        md_lines.append(f"**Type:** {prop.property_type}")
        md_lines.append(f"")
        md_lines.append(f"**Description:** {prop.description[:300]}..." if len(prop.description) > 300 else f"**Description:** {prop.description}")
        md_lines.append(f"")
        md_lines.append(f"[View Listing]({prop.listing_url})")
        md_lines.append(f"")
        
        # Location analysis
        loc = report.location_analyses.get(prop.id)
        if loc:
            md_lines.append(f"### Location Analysis")
            if loc.pros:
                md_lines.append(f"**Pros:**")
                for pro in loc.pros:
                    md_lines.append(f"- ✅ {pro}")
            if loc.cons:
                md_lines.append(f"**Cons:**")
                for con in loc.cons:
                    md_lines.append(f"- ⚠️ {con}")
            md_lines.append(f"")
        
        md_lines.append(f"---")
        md_lines.append(f"")
    
    return {
        "status": "success",
        "message": "Final report submitted successfully",
        "report": report_dict,
        "markdown_report": "\n".join(md_lines)
    }