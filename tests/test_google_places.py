"""
Simple test script for Google Places API tools.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools import google_places_geocode_tool, google_places_nearby_tool
from dotenv import load_dotenv

load_dotenv()


def test_geocode():
    """Test geocoding"""
    print("\n=== TEST: Geocoding ===")
    address = "Ikeja City Mall, Lagos, Nigeria"
    print(f"Address: {address}")
    
    result = google_places_geocode_tool.invoke({"address": address, "country": "NG"})
    
    if result.get("success"):
        print(f"✓ Success")
        print(f"  Lat/Lng: ({result['latitude']}, {result['longitude']})")
        print(f"  Formatted: {result['formatted_address']}")
        return result["latitude"], result["longitude"]
    else:
        print(f"✗ Failed: {result.get('error')}")
        return None, None


def test_nearby():
    """Test nearby search"""
    print("\n=== TEST: Nearby Search ===")
    
    # Use Ikeja coordinates
    lat, lng = 6.6018, 3.3515
    print(f"Location: ({lat}, {lng})")
    print(f"Category: restaurant")
    
    pois = google_places_nearby_tool.invoke({
        "latitude": lat,
        "longitude": lng,
        "category": "restaurant",
        "radius_meters": 3000,
        "limit": 5
    })
    
    print(f"✓ Found {len(pois)} places:")
    for poi in pois[:3]:
        distance_km = poi["distance_meters"] / 1000
        rating = poi.get("rating", "N/A")
        print(f"  - {poi['name']} ({distance_km:.2f}km, rating: {rating})")


def main():
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("✗ ERROR: GOOGLE_MAPS_API_KEY not set in .env file")
        return
    
    print("GOOGLE PLACES API TOOLS TEST")
    test_geocode()
    test_nearby()
    print("\n✓ Tests complete\n")


if __name__ == "__main__":
    main()
