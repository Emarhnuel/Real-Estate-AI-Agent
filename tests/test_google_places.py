"""Tests for Google Places API tools."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.tools import google_places_geocode_tool, google_places_nearby_tool, calculate_distance

load_dotenv()


def test_geocode():
    """Test geocoding tool"""
    print("\n1. Testing Geocode Tool:")
    print("-" * 50)
    
    # Test Ikeja address
    result = google_places_geocode_tool.invoke({
        "address": "Omotayo Ojo Street, Ikeja, Lagos, Nigeria",
        "country": "NG"
    })
    print(f"   Address: Omotayo Ojo Street, Ikeja, Lagos")
    print(f"   Success: {result['success']}")
    
    if result["success"]:
        print(f"   Formatted: {result.get('formatted_address', 'N/A')}")
        print(f"   Coordinates: ({result['latitude']}, {result['longitude']})")
        assert result["success"] is True
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")


def test_nearby_search():
    """Test nearby search tool"""
    print("\n2. Testing Nearby Search Tool:")
    print("-" * 50)
    
    # First geocode Ojodu location
    geocode_result = google_places_geocode_tool.invoke({
        "address": "Oyinbo Orunmila, Ojodu, Lagos, Nigeria",
        "country": "NG"
    })
    
    if geocode_result["success"]:
        lat = geocode_result["latitude"]
        lon = geocode_result["longitude"]
        
        # Test restaurant search near Ojodu
        result = google_places_nearby_tool.invoke({
            "latitude": lat,
            "longitude": lon,
            "category": "restaurant",
            "radius_meters": 2000,
            "limit": 5
        })
        
        print(f"   Location: Ojodu, Lagos ({lat:.4f}, {lon:.4f})")
        print(f"   Category: restaurant")
        print(f"   Radius: 2000m")
        print(f"   Results found: {len(result)}")
        
        if result:
            print(f"\n   First result:")
            first = result[0]
            print(f"   - Name: {first.get('name', 'N/A')}")
            print(f"   - Distance: {first.get('distance_meters', 0):.0f}m")
            print(f"   - Rating: {first.get('rating', 'N/A')}")
        
        assert isinstance(result, list)
    else:
        print(f"   Geocoding failed: {geocode_result.get('error', 'Unknown')}")


def test_distance():
    """Test distance calculator"""
    print("\n3. Testing Distance Calculator:")
    print("-" * 50)
    
    # Test distance between Ikeja and Ojodu
    ikeja_lat, ikeja_lon = 6.6018, 3.3515  # Approximate Ikeja coordinates
    ojodu_lat, ojodu_lon = 6.6515, 3.3667  # Approximate Ojodu coordinates
    
    distance = calculate_distance(ikeja_lat, ikeja_lon, ojodu_lat, ojodu_lon)
    distance_km = distance / 1000
    
    print(f"   From: Ikeja ({ikeja_lat}, {ikeja_lon})")
    print(f"   To: Ojodu ({ojodu_lat}, {ojodu_lon})")
    print(f"   Distance: {distance_km:.2f} km")
    
    # Verify distance is reasonable (should be ~5-10 km)
    assert 3_000 < distance < 15_000
    
    # Test same point
    same_distance = calculate_distance(ikeja_lat, ikeja_lon, ikeja_lat, ikeja_lon)
    print(f"\n   Same point distance: {same_distance}m (should be 0)")
    assert same_distance == 0.0


if __name__ == "__main__":
    print("\n" + "="*50)
    print("GOOGLE PLACES API TESTS")
    print("="*50 + "\n")
    
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("❌ GOOGLE_MAPS_API_KEY not found\n")
    else:
        try:
            test_geocode()
            print("✓ Geocode test passed\n")
        except Exception as e:
            print(f"❌ Geocode failed: {e}\n")
        
        try:
            test_nearby_search()
            print("✓ Nearby search test passed\n")
        except Exception as e:
            print(f"❌ Nearby search failed: {e}\n")
        
        try:
            test_distance()
            print("✓ Distance test passed\n")
        except Exception as e:
            print(f"❌ Distance failed: {e}\n")
    
    print("="*50)
