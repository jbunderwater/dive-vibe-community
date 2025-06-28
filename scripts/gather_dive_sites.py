import requests
import json
import sys
import time
import os

def get_bounding_box_google(destination):
    """
    Use Google Maps Geocoding API to get the bounding box for a destination.
    Returns (south, west, north, east) as floats.
    """
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY environment variable not set")
        print("Please set your Google Maps API key: export GOOGLE_MAPS_API_KEY='your_api_key_here'")
        return None
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": destination,
        "key": api_key
    }
    
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("status") != "OK":
            print(f"Google Maps API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            return None
            
        if not data.get("results"):
            print(f"No results found for '{destination}'")
            return None
            
        # Get the first result
        result = data["results"][0]
        
        # Extract bounding box from viewport
        viewport = result.get("geometry", {}).get("viewport", {})
        if not viewport:
            print(f"No viewport found for '{destination}'")
            return None
            
        southwest = viewport.get("southwest", {})
        northeast = viewport.get("northeast", {})
        
        if not southwest or not northeast:
            print(f"Incomplete viewport data for '{destination}'")
            return None
            
        # Return (south, west, north, east)
        bbox = (
            southwest.get("lat"),
            southwest.get("lng"), 
            northeast.get("lat"),
            northeast.get("lng")
        )
        
        print(f"Google Maps bounding box for '{destination}': {bbox}")
        return bbox
        
    except Exception as e:
        print(f"Error fetching bounding box from Google Maps: {e}")
        return None

def query_dive_sites(bbox):
    """
    Query Overpass API for dive sites within the bounding box.
    Returns a list of site dicts.
    """
    south, west, north, east = bbox
    # Simple Overpass QL query for debugging
    query = f"""
    [out:json][timeout:60];
    (
      node["sport"="scuba_diving"]({south},{west},{north},{east});
      node["scuba_diving"="site"]({south},{west},{north},{east});
      node["dive_site"="yes"]({south},{west},{north},{east});
      way["sport"="scuba_diving"]({south},{west},{north},{east});
      way["scuba_diving"="site"]({south},{west},{north},{east});
      way["dive_site"="yes"]({south},{west},{north},{east});
    );
    out center tags;
    """
    
    # Print the query for debugging
    print("\n" + "="*60)
    print("OVERPASS QUERY:")
    print("="*60)
    print(query)
    print("="*60)
    
    url = "https://overpass-api.de/api/interpreter"
    try:
        print(f"Querying Overpass API with bounding box: south={south}, west={west}, north={north}, east={east}")
        resp = requests.post(url, data=query, headers={"User-Agent": "DiveVibe/1.0"})
        resp.raise_for_status()
        data = resp.json()
        elements = data.get("elements", [])
        print(f"Overpass API response: {len(elements)} elements")
        return elements
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error querying Overpass API: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")
        return []
    except Exception as e:
        print(f"Error querying Overpass API: {e}")
        return []

def extract_site_info(element):
    """
    Extract relevant info from an Overpass element.
    """
    tags = element.get("tags", {})
    name = tags.get("name")
    if not name:
        return None
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    if lat is None or lon is None:
        return None
    return {
        "name": name,
        "country": tags.get("addr:country"),
        "region": tags.get("addr:region") or tags.get("is_in:state"),
        "lat": lat,
        "lon": lon,
        "osm_id": element.get("id"),
        "tags": tags
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python gather_dive_sites.py <destination>")
        print("Note: Set GOOGLE_MAPS_API_KEY environment variable first")
        sys.exit(1)
    destination = " ".join(sys.argv[1:])
    print(f"Looking up bounding box for: {destination}")
    bbox = get_bounding_box_google(destination)
    if not bbox:
        sys.exit(1)
    print(f"Bounding box: {bbox}")
    print("Querying Overpass API for dive sites...")
    elements = query_dive_sites(bbox)
    print(f"Found {len(elements)} elements. Extracting site info...")
    sites = []
    for el in elements:
        info = extract_site_info(el)
        if info:
            sites.append(info)
    print(f"Collected {len(sites)} dive sites with names and coordinates.")
    out_file = f"dive_sites_{destination.replace(' ', '_').lower()}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2)
    print(f"Saved results to {out_file}")

if __name__ == "__main__":
    main() 