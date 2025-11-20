"""
Test script for Google Places API tools and distance calculation.
Run this to verify that google_places_geocode_tool, google_places_nearby_tool, and calculate_distance are working.
"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools import google_places_geocode_tool, google_places_nearby_tool, calculate_distance
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_geocode():
    """Test geocoding a Nigerian address"""
    print("\n" + "="*60)
    print("TEST 1: Geocoding Street Address")
    print("="*60)
    
    address = "12 omotayo ojo street ikeja, Lagos Nigeria"
    print(f"Address: {address}")
    
    try:
        result = google_places_geocode_tool.invoke({"address": address, "country": "NG"})
        
        if result.get("success"):
            print(f"✓ Geocoding successful!")
            print(f"  Latitude: {result['latitude']}")
            print(f"  Longitude: {result['longitude']}")
            print(f"  Formatted: {result['formatted_address']}")
            print(f"  Place ID: {result.get('place_id', 'N/A')}")
            return result['latitude'], result['longitude']
        else:
            print(f"✗ Geocoding failed: {result.get('error')}")
            return None, None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None, None


def test_geocode_landmark():
    """Test geocoding a landmark/POI"""
    print("\n" + "="*60)
    print("TEST 1B: Geocoding Landmark (POI)")
    print("="*60)
    
    address = "Ikeja City Mall, Lagos, Nigeria"
    print(f"Landmark: {address}")
    
    try:
        result = google_places_geocode_tool.invoke({"address": address, "country": "NG"})
        
        if result.get("success"):
            print(f"✓ Geocoding successful!")
            print(f"  Latitude: {result['latitude']}")
            print(f"  Longitude: {result['longitude']}")
            print(f"  Formatted: {result['formatted_address']}")
            print(f"  Name: {result.get('name', 'N/A')}")
            print(f"  Place ID: {result.get('place_id', 'N/A')}")
            return result['latitude'], result['longitude']
        else:
            print(f"✗ Geocoding failed: {result.get('error')}")
            print(f"  Note: Some landmarks may not be in Google Places database")
            return None, None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None, None


def test_nearby_pois_debug(latitude, longitude):
    """Debug test to see raw API response"""
    print("\n" + "="*60)
    print("DEBUG: Raw API Response Test")
    print("="*60)
    
    if not latitude or not longitude:
        print("✗ Skipping - no coordinates from geocoding")
        return
    
    import requests
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    category = "restaurant"
    radius_meters = 5000
    
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating"
    }
    
    body = {
        "includedTypes": [category],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius_meters
            }
        }
    }
    
    print(f"URL: {url}")
    print(f"Center: ({latitude}, {longitude})")
    print(f"Radius: {radius_meters}m")
    print(f"Category: {category}")
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            places = data.get("places", [])
            print(f"Places returned: {len(places)}")
            
            if len(places) > 0:
                print("\nFirst place:")
                print(f"  Name: {places[0].get('displayName', {}).get('text')}")
                print(f"  Address: {places[0].get('formattedAddress')}")
                print(f"  Rating: {places[0].get('rating', 'N/A')}")
            else:
                print("\n⚠ API returned 0 places")
        else:
            print(f"Error response: {response.text[:500]}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def test_nearby_pois(latitude, longitude):
    """Test finding nearby points of interest"""
    print("\n" + "="*60)
    print("TEST 2: Finding Nearby POIs")
    print("="*60)
    
    if not latitude or not longitude:
        print("✗ Skipping - no coordinates from geocoding")
        return
    
    print(f"Searching around coordinates: ({latitude:.4f}, {longitude:.4f})")
    
    # Use categories that work with Google Places API
    categories = ["restaurant", "cafe", "shopping_mall", "school", "park", "hospital"]
    
    for category in categories:
        print(f"\nSearching for nearby {category}...")
        
        try:
            pois = google_places_nearby_tool.invoke({
                "latitude": latitude,
                "longitude": longitude,
                "category": category,
                "radius_meters": 5000,
                "limit": 10
            })
            
            if len(pois) > 0:
                print(f"✓ Found {len(pois)} {category} locations:")
                for poi in pois[:3]:  # Show first 3
                    distance_km = poi['distance_meters'] / 1000
                    rating = poi.get('rating', 'N/A')
                    print(f"  - {poi['name']} ({distance_km:.2f}km away, rating: {rating})")
            else:
                print(f"⚠ Found 0 {category} locations")
                
        except Exception as e:
            print(f"✗ Error searching {category}: {str(e)}")


def test_distance_calculation(latitude, longitude):
    """Test distance calculation from main address to a reference point"""
    print("\n" + "="*60)
    print("TEST 3: Distance Calculation")
    print("="*60)
    
    if not latitude or not longitude:
        print("✗ Skipping - no coordinates from geocoding")
        return
    
    # Reference location for distance comparison
    reference_address = "Lekki Phase 1, Lagos, Nigeria"
    
    print(f"Calculating distance from main address to: {reference_address}")
    
    try:
        # Geocode reference address
        result = google_places_geocode_tool.invoke({"address": reference_address, "country": "NG"})
        if not result.get("success"):
            print(f"✗ Failed to geocode reference address: {result.get('error')}")
            return
        
        ref_lat, ref_lon = result['latitude'], result['longitude']
        print(f"  Reference point: ({ref_lat:.4f}, {ref_lon:.4f})")
        
        # Calculate distance
        distance = calculate_distance(latitude, longitude, ref_lat, ref_lon)
        distance_km = distance / 1000
        print(f"\n✓ Distance: {distance:.2f} meters ({distance_km:.2f} km)")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def main():
    print("\n" + "="*60)
    print("GOOGLE PLACES API TOOLS TEST SUITE")
    print("="*60)
    
    # Check if API key is set
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("\n✗ ERROR: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return
    
    print("✓ GOOGLE_MAPS_API_KEY found")
    
    # Run tests
    lat, lon = test_geocode()
    test_geocode_landmark()
    test_nearby_pois_debug(lat, lon)  # Debug test first
    test_nearby_pois(lat, lon)
    test_distance_calculation(lat, lon)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
