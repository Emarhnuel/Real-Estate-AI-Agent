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
    """Test geocoding a Nigerian address"""
    print("\n" + "="*60)
    print("TEST 1: Geocoding Street Address")
    print("="*60)
    
    address = "12 omotayo ojo street ikeja, Lagos Nigeria"
    print(f"Address: {address}")
    
    try:
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


def test_geocode_landmark():
    """Test geocoding a landmark/POI"""
    print("\n" + "="*60)
    print("TEST 1B: Geocoding Landmark (POI)")
    print("="*60)
    
    address = "Ikeja City Mall, Lagos, Nigeria"
    print(f"Landmark: {address}")
    
    try:
        result = mapbox_geocode_tool.invoke({"address": address, "country": "NG"})
        
        if result.get("success"):
            print(f"✓ Geocoding successful!")
            print(f"  Latitude: {result['latitude']}")
            print(f"  Longitude: {result['longitude']}")
            print(f"  Formatted: {result['formatted_address']}")
            print(f"  Name: {result.get('name', 'N/A')}")
            return result['latitude'], result['longitude']
        else:
            print(f"✗ Geocoding failed: {result.get('error')}")
            print(f"  Note: Some landmarks may not be in Mapbox database")
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
    from math import radians, cos
    
    api_key = os.getenv("MAPBOX_API_KEY")
    category = "restaurant"
    
    # Calculate bbox
    radius_meters = 10000
    bbox_radius = radius_meters * 1.5
    lat_offset = (bbox_radius / 1000) / 111.0
    lon_offset = (bbox_radius / 1000) / (111.0 * abs(cos(radians(latitude))))
    bbox = f"{longitude - lon_offset},{latitude - lat_offset},{longitude + lon_offset},{latitude + lat_offset}"
    
    url = f"https://api.mapbox.com/search/searchbox/v1/category/{category}"
    params = {
        "access_token": api_key,
        "proximity": f"{longitude},{latitude}",
        "bbox": bbox,
        "limit": 10,
        "language": "en"
    }
    
    print(f"URL: {url}")
    print(f"Proximity: {longitude},{latitude}")
    print(f"Bbox: {bbox}")
    print(f"Radius: {radius_meters}m")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            print(f"Features returned: {len(features)}")
            
            if len(features) > 0:
                print("\nFirst feature:")
                print(f"  Name: {features[0]['properties'].get('name')}")
                print(f"  Coords: {features[0]['geometry']['coordinates']}")
                print(f"  Address: {features[0]['properties'].get('full_address')}")
            else:
                print("\n⚠ API returned 0 features")
                print("This suggests limited POI coverage in this geographic area")
        else:
            print(f"Error response: {response.text[:200]}")
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
    
    # Use categories that work with Mapbox Search Box API
    categories = ["restaurant", "shopping", "cafe", "school"]
    
    for category in categories:
        print(f"\nSearching for nearby {category}...")
        
        try:
            pois = mapbox_nearby_tool.invoke({
                "latitude": latitude,
                "longitude": longitude,
                "category": category,
                "radius_meters": 10000,  # Increased to 10km for testing
                "limit": 10
            })
            
            if len(pois) > 0:
                print(f"✓ Found {len(pois)} {category} locations:")
                for poi in pois[:3]:  # Show first 3
                    distance_km = poi['distance_meters'] / 1000
                    print(f"  - {poi['name']} ({distance_km:.2f}km away)")
            else:
                print(f"⚠ Found 0 {category} locations")
                print(f"  Note: Search Box API may have limited POI coverage in this area")
                
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
