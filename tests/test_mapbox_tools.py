"""
Test script for Mapbox tools and distance calculation.
Run this to verify that mapbox_geocode_tool, mapbox_nearby_tool, and calculate_distance are working.
"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools import mapbox_geocode_tool, mapbox_nearby_tool, calculate_distance
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_geocode():
    """Test geocoding a nigerian address"""
    print("\n" + "="*60)
    print("TEST 1: Geocoding Address")
    print("="*60)
    
    address = "Ikeja city mall, ikeja, Lagos Nigeria"
    print(f"Address: {address}")
    
    try:
        # Use country code for better accuracy
        result = mapbox_geocode_tool.invoke({"address": address, "country": "NG"})
        
        if result.get("success"):
            print(f"✓ Geocoding successful!")
            print(f"  Latitude: {result['latitude']}")
            print(f"  Longitude: {result['longitude']}")
            print(f"  Formatted: {result['formatted_address']}")
            return result['latitude'], result['longitude']
        else:
            print(f"✗ Geocoding failed: {result.get('error')}")
            return None, None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None, None


def test_nearby_pois(latitude, longitude):
    """Test finding nearby points of interest"""
    print("\n" + "="*60)
    print("TEST 2: Finding Nearby POIs")
    print("="*60)
    
    if not latitude or not longitude:
        print("✗ Skipping - no coordinates from geocoding")
        return
    
    # Use categories that work with Mapbox Search Box API
    categories = ["shopping", "restaurant", "coffee", "school"]
    
    for category in categories:
        print(f"\nSearching for nearby {category}...")
        
        try:
            pois = mapbox_nearby_tool.invoke({
                "latitude": latitude,
                "longitude": longitude,
                "category": category,
                "radius_meters": 5000,
                "limit": 5
            })
            
            print(f"✓ Found {len(pois)} {category} locations:")
            for poi in pois[:3]:  # Show first 3
                distance_km = poi['distance_meters'] / 1000
                print(f"  - {poi['name']} ({distance_km:.2f}km away)")
                
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
        result = mapbox_geocode_tool.invoke({"address": reference_address, "country": "NG"})
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
    print("MAPBOX TOOLS TEST SUITE")
    print("="*60)
    
    # Check if API key is set
    if not os.getenv("MAPBOX_API_KEY"):
        print("\n✗ ERROR: MAPBOX_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return
    
    print("✓ MAPBOX_API_KEY found")
    
    # Run tests - all using coordinates from the main address
    lat, lon = test_geocode()
    test_nearby_pois(lat, lon)
    test_distance_calculation(lat, lon)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
