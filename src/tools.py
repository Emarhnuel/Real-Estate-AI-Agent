"""
Tools for AI Real Estate Co-Pilot.

This module provides external API integrations including Tavily search
for property listings, Google Places for location services, and Gemini for interior decorations.
"""

import os
import asyncio
import requests
from typing import Dict, Any, List
from math import radians, sin, cos, sqrt, atan2
from tavily import TavilyClient
from browser_use import Agent, Browser
from browser_use.llm import ChatAnthropicBedrock
from langchain_core.tools import tool
from langchain_tavily import TavilyExtract 
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv(override=True)




# Import the Pydantic models needed for tool schemas
from src.models import PropertyForReview, PropertyReport

# Shared disk directory for all agents
AGENT_DATA_DIR = os.path.abspath("./agent_data")



@tool(parse_docstring=True)
def browser_use_extract_tool(url: str, extraction_prompt: str) -> str:
    """Use a stealth cloud browser to visit a URL and extract specific property information.
    
    Useful for scraping real estate listings that have anti-bot protections.
    
    Args:
        url: The property URL to visit and extract data from.
        extraction_prompt: Specific instructions on what to extract from the page (e.g., 'Extract price, bedrooms, and description').
    """
    api_key = os.getenv("BROWSER_USE_API_KEY")
    if not api_key:
        return "Error: BROWSER_USE_API_KEY environment variable is not set"
    
    # Advanced Prompting Strategy based on official docs
    task = (
        f"1. Go to the URL: {url}\n"
        f"2. {extraction_prompt}\n"
        "3. Wait up to 3 seconds for the page to load. If not loaded, refresh ONCE.\n"
        "4. Extract up to 2 properties that match the user's search criteria from this page.\n"
        "5. For EACH property, you MUST extract: price, bedrooms, bathrooms, address, property URL, description, and at least 3 image URLs.\n"
        "6. If images are not visible, scroll down ONCE to trigger lazy-loading. Do NOT scroll more than once per property.\n"
        "7. If a modal or pop-up appears, close it and continue.\n"
        "8. As soon as you have extracted 2 matching properties with all required fields, use the 'done' action IMMEDIATELY to return the JSON array. Do NOT continue browsing.\n"
        "9. If after reasonable effort you can only find 1 matching property, return that 1 property. Do NOT keep searching endlessly.\n"
    )
    
    async def run_extraction():
        # use_cloud=True enables stealth and anti-bot bypass
        # cloud_proxy_country_code='us' uses a US residential proxy to further bypass Zillow blocks
        # cloud_timeout=30 gives the CDP protocol up to 30 mins to serialize large DOM trees without TimeoutErrors
        browser = Browser(
            use_cloud=True,
            cloud_proxy_country_code='us',
            cloud_timeout=30
        )
        # Using AWS Bedrock Anthropic model directly
        llm = ChatAnthropicBedrock(
            model="us.anthropic.claude-opus-4-6-v1", 
            aws_region=os.getenv("AWS_REGION", "us-east-1") 
        )
        
        # Max failures set to 3 for resilience as per browser-use docs
        agent = Agent(
            task=task, 
            browser=browser, 
            llm=llm,
            max_failures=3,
            use_vision=True # Allows the LLM to visually see the property listing layout
        )
        
        history = await agent.run(max_steps=15)
        return history.final_result()

    try:
        return asyncio.run(run_extraction())
    except Exception as e:
        return f"Extraction failed: {str(e)}"


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
    
    client = TavilyClient(api_key=api_key)
    processed_results = []
    failed_urls = []
    
    # Process URLs individually with retry logic
    for url in urls:
        for attempt in range(3):  # 3 attempts with increasing timeout
            try:
                timeout = 60 + (attempt * 30)  # 60s, 90s, 120s
                response = client.extract(
                    urls=[url],
                    include_images=True,
                    extract_depth="advanced",
                    timeout=timeout
                )
                for result in response.get('results', []):
                    processed_results.append({
                        "url": result.get("url", ""),
                        "raw_content": result.get("raw_content", ""),
                        "images": result.get("images", []),
                    })
                break  # Success, move to next URL
            except Exception as e:
                if attempt == 2:  # Final attempt failed
                    failed_urls.append({"url": url, "error": str(e)})
    
    return {
        "results": processed_results,
        "failed_results": failed_urls,
        "message": f"Extracted {len(processed_results)} URLs, {len(failed_urls)} failed"
    }


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
        
        if country and len(country.strip()) == 2:
            body["regionCode"] = country.strip().upper()
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        
        if not response.ok:
            error_msg = f"Google API Error {response.status_code}"
            try:
                error_msg += f": {response.json()}"
            except:
                error_msg += f": {response.text}"
            
            if response.status_code == 404:
                return {"success": False, "error": "Address not found"}
            raise Exception(error_msg)
            
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



# Interior Decorator Tools

@tool(parse_docstring=True)
def analyze_property_images_tool(image_url: str) -> Dict[str, Any]:
    """Analyze property images using Gemini Vision to identify rooms and decoration opportunities.
    
    Args:
        image_url: URL of the property image to analyze
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    
    try:
        from langchain_openrouter import ChatOpenRouter
        from langchain_core.messages import HumanMessage
        import base64
        
        model = ChatOpenRouter(
            model="google/gemini-2.5-flash",
            api_key=api_key
        )
        
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        image_bytes = response.content
        
        # Convert image bytes to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = """Analyze this property image for interior decoration opportunities.
        
        Identify:
        1. Room type (living room, bedroom, porch, entryway, etc.)
        2. Available spaces for decorations (walls, corners, windows, doorways)
        3. Existing furniture and layout
        4. Style and color scheme
        5. Specific decoration suggestions (furniture, lighting, plants, art)
        
        Return a JSON object with: room_type, decoration_spaces, style_notes, suggestions"""
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        )
        
        response = model.invoke([message])
        
        return {
            "success": True,
            "analysis": response.content,
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
    decoration_description: str,
    property_id: str
) -> Dict[str, Any]:
    """Generate decorated version of property image using Gemini Image Generation.
    
    This tool generates the image AND saves it to disk automatically.
    Returns only metadata - the base64 is saved to a file, not returned.
    
    Args:
        image_url: URL of the original property image
        decoration_description: Description of interior decorations to add
        property_id: Property ID used for naming the output file (e.g., "prop1")
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    
    try:
        from langchain_openrouter import ChatOpenRouter
        from langchain_core.messages import HumanMessage
        import base64
        import json
        import re
        from pathlib import Path
        
        model = ChatOpenRouter(
            model="google/gemini-3.1-flash-image-preview",
            api_key=api_key
        )
        
        # Download original image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Convert image bytes to base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        
        # Create prompt for image editing
        prompt = f"""Using the provided property image, add tasteful interior decorations to create a beautiful and inviting atmosphere.
        
        Add these decorations: {decoration_description}
        
        Make sure the decorations:
        - Look realistic and naturally placed
        - Match the room's style and lighting
        - Enhance the property's appeal
        
        Keep the original room structure unchanged."""
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        )
        
        llm_response = model.invoke([message])
        
        # Extract base64 image from markdown response
        # OpenRouter models often return images in format: ![image](data:image/png;base64,iVBORw0KG...)
        decorated_image_base64 = None
        
        # Look for data URI pattern
        match = re.search(r'data:image/[^;]+;base64,([a-zA-Z0-9+/=]+)', llm_response.content)
        if match:
            decorated_image_base64 = match.group(1)
        else:
            # Fallback if bare base64 string is returned
            pure_b64 = re.sub(r'[^a-zA-Z0-9+/=]', '', llm_response.content)
            if len(pure_b64) > 1000: # Heuristic to check if it's a large block string
                decorated_image_base64 = pure_b64
        
        if not decorated_image_base64:
            return {
                "success": False,
                "error": "No image was generated by the model"
            }
        
        # Save the decorated image to disk (outside agent context)
        output_dir = Path("decorated_images")
        output_dir.mkdir(exist_ok=True)
        
        # Save as JSON with all metadata including base64
        output_file = output_dir / f"{property_id}_decorated.json"
        decoration_data = {
            "property_id": property_id,
            "original_image_url": image_url,
            "decorated_image_base64": decorated_image_base64,
            "decorations_added": decoration_description
        }
        with open(output_file, "w") as f:
            json.dump(decoration_data, f)
        
        # Return only metadata - NOT the base64 (prevents context overflow)
        return {
            "success": True,
            "property_id": property_id,
            "original_image_url": image_url,
            "decorations_added": decoration_description,
            "saved_to_disk": str(output_file),
            "message": f"Decorated image generated and saved to {output_file}. Do NOT try to read this file."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Image generation failed: {str(e)}"
        }



@tool(parse_docstring=True)
def present_properties_for_review_tool(properties: List[Dict[str, Any]]) -> dict:
    """Present properties to user for review and approval.
    
    This tool is configured with interrupt_on in the agent, so it will automatically
    pause execution before running. The user can approve, edit, or reject the tool call.
    When approved or edited, this tool returns the approved property IDs for the next step.
    
    Args:
        properties: List of property dicts containing at minimum an id field.
    """
    # Extract property IDs from the input
    # Handle both full property objects and simplified ID-only objects
    approved_ids = []
    for p in properties:
        if isinstance(p, dict):
            if "id" in p:
                approved_ids.append(p["id"])
        elif hasattr(p, "id"):
            approved_ids.append(p.id)
    
    return {
        "status": "approved",
        "approved_property_ids": approved_ids,
        "count": len(approved_ids),
        "message": f"User approved {len(approved_ids)} properties for analysis"
    }


@tool(parse_docstring=True)
def submit_final_report_tool(
    summary: str,
    property_ids: List[str],
    location: str,
    max_price: float,
    min_bedrooms: int,
    min_bathrooms: float,
    property_types: List[str]
) -> dict:
    """Submit the final property report. Call this as the LAST action after all analysis is complete.
    
    Args:
        summary: A comprehensive and detailed executive summary of findings for all properties found.
        property_ids: List of approved property IDs (e.g., ["property_001", "property_002"])
        location: Search location from user's original request
        max_price: Maximum budget from user's request
        min_bedrooms: Minimum bedrooms from user's request
        min_bathrooms: Minimum bathrooms from user's request
        property_types: Property types searched (e.g., ["apartment", "flat", "duplex"])
    """
    return {
        "status": "success",
        "message": "Final report submitted successfully",
        "summary": summary,
        "property_ids": property_ids,
        "search_criteria": {
            "location": location,
            "max_price": max_price,
            "min_bedrooms": min_bedrooms,
            "min_bathrooms": min_bathrooms,
            "property_types": property_types
        }
    }