#!/usr/bin/env python3
"""
OpenStreetMap Overpass API script to collect dive sites for a destination
Uses Google Maps for geocoding and OSM Overpass API for dive site data
"""

import requests
import json
import sys
import time
import os
import csv
from pathlib import Path

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

def is_near_water(lat, lon, api_key):
    """
    Use Google Maps Places API to check if coordinates are near water.
    Returns True if the location is near water (within 100 meters), False otherwise.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": 100,  # 100 meters radius
        "type": "natural_feature",  # Look for natural features
        "key": api_key
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)  # Add 10 second timeout
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("status") != "OK" and data.get("status") != "ZERO_RESULTS":
            print(f"Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            return True  # Default to True to avoid excluding valid sites due to API errors
        
        results = data.get("results", [])
        
        # Check if any nearby places are water-related
        water_keywords = [
            "beach", "ocean", "sea", "lake", "river", "bay", "cove", "harbor", "harbour", 
            "marina", "pier", "dock", "wharf", "shore", "coast", "waterfront", "lagoon",
            "reef", "coral", "underwater", "quarry"
        ]
        
        for place in results:
            name = place.get("name", "").lower()
            types = place.get("types", [])
            
            # Check if place name contains water keywords
            if any(keyword in name for keyword in water_keywords):
                return True
            
            # Check if place types indicate water proximity
            water_types = [
                "natural_feature", "establishment", "point_of_interest", "tourist_attraction"
            ]
            if any(water_type in types for water_type in water_types):
                # Additional check for water-related establishment
                if "beach" in name or "marina" in name or "pier" in name:
                    return True
        
        # If no water-related places found within 100m, it's likely inland
        return False
        
    except Exception as e:
        print(f"Error checking water proximity: {e}")
        return True  # Default to True to avoid excluding valid sites due to API errors

def query_dive_sites_osm(bbox):
    """
    Query Overpass API for dive sites within the bounding box.
    Returns a list of site dicts.
    """
    south, west, north, east = bbox
    
    # Comprehensive Overpass QL query for dive sites, excluding businesses
    query = f"""
    [out:json][timeout:120];
    (
      // Dive sites with various tags (excluding businesses)
      node["sport"="scuba_diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      node["scuba_diving"="site"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      node["dive_site"="yes"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      node["leisure"="diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      node["tourism"="diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      
      // Ways (areas) with dive site tags (excluding businesses)
      way["sport"="scuba_diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      way["scuba_diving"="site"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      way["dive_site"="yes"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      way["leisure"="diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      way["tourism"="diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      
      // Relations with dive site tags (excluding businesses)
      relation["sport"="scuba_diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      relation["scuba_diving"="site"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      relation["dive_site"="yes"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      relation["leisure"="diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
      relation["tourism"="diving"]["shop"!="yes"]["tourism"!="hotel"]["tourism"!="resort"]["amenity"!="diving_centre"]({south},{west},{north},{east});
    );
    out center tags;
    """
    
    # Use the private.coffee Overpass instance
    url = "https://overpass.private.coffee/api/interpreter"
    
    try:
        print(f"Querying OSM Overpass API with bounding box: south={south}, west={west}, north={north}, east={east}")
        resp = requests.post(url, data=query, headers={"User-Agent": "DiveVibe/1.0"}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        elements = data.get("elements", [])
        print(f"OSM Overpass API response: {len(elements)} elements")
        return elements
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error querying OSM Overpass API: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")
        return []
    except Exception as e:
        print(f"Error querying OSM Overpass API: {e}")
        return []

def extract_site_info(element):
    """
    Extract relevant info from an Overpass element.
    """
    tags = element.get("tags", {})
    name = tags.get("name")
    if not name:
        return None
    
    # Extract contact information first to check for businesses
    phone = tags.get("phone") or tags.get("contact:phone") or ""
    email = tags.get("email") or tags.get("contact:email") or ""
    
    # Skip if it has contact information (likely a business)
    if phone or email:
        return None
    
    # Filter out business-related sites
    shop = tags.get("shop")
    tourism = tags.get("tourism")
    amenity = tags.get("amenity")
    
    # Skip if it's clearly a business
    if shop or tourism in ["hotel", "resort", "guest_house"] or amenity in ["diving_centre", "dive_centre", "shop"]:
        return None
    
    # Skip if name contains business keywords
    name_lower = name.lower()
    business_keywords = [
        "dive center", "dive_centre", "diving center", "diving centre",
        "dive shop", "diving shop", "scuba shop", "dive store",
        "resort", "hotel", "lodge", "inn", "guesthouse", "hostel",
        "dive school", "diving school", "scuba school",
        "dive club", "diving club", "scuba club",
        "dive operator", "diving operator", "tour operator",
        "dive company", "diving company", "building",
        "centre", "safari", "dive safari"
    ]
    
    if any(keyword in name_lower for keyword in business_keywords):
        return None
    
    # Get coordinates
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    if lat is None or lon is None:
        return None
    
    # Extract additional information
    description = tags.get("description") or tags.get("note") or ""
    website = tags.get("website") or tags.get("url") or ""
    
    # Get dive-specific information
    difficulty = tags.get("difficulty") or ""
    max_depth = tags.get("max_depth") or tags.get("depth") or ""
    entry_type = tags.get("entry_type") or ""
    site_type = tags.get("site_type") or tags.get("type") or ""
    
    # Skip if site_type is dive_centre (business)
    if site_type.lower() == "dive_centre":
        return None
    
    return {
        "name": name,
        "description": description,
        "lat": lat,
        "lon": lon,
        "country": tags.get("addr:country") or tags.get("country"),
        "region": tags.get("addr:region") or tags.get("is_in:state") or tags.get("state"),
        "city": tags.get("addr:city") or tags.get("city"),
        "website": website,
        "phone": phone,
        "email": email,
        "difficulty": difficulty,
        "max_depth": max_depth,
        "entry_type": entry_type,
        "site_type": site_type,
        "osm_id": element.get("id"),
        "osm_type": element.get("type"),
        "tags": json.dumps(tags)  # Store all tags as JSON string
    }

def save_to_csv(sites, destination):
    """
    Save dive sites to CSV file
    """
    if not sites:
        print("No dive sites found to save.")
        return None
    
    filename = f"{destination.replace(' ', '_').lower()}_divesites_osm.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'name', 'description', 'lat', 'lon', 'country', 'region', 'city',
            'website', 'phone', 'email', 'difficulty', 'max_depth', 'entry_type',
            'site_type', 'osm_id', 'osm_type', 'tags'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for site in sites:
            writer.writerow(site)
    
    print(f"Saved {len(sites)} dive sites to {filename}")
    return filename

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python osm_dive_sites.py <destination>")
        sys.exit(1)
    
    destination = " ".join(sys.argv[1:])
    
    print(f"🌊 OSM Dive Site Collector")
    print(f"Destination: {destination}")
    print("=" * 50)
    
    # Get bounding box from Google Maps
    print(f"Getting bounding box for: {destination}")
    bbox = get_bounding_box_google(destination)
    if not bbox:
        print("Failed to get bounding box. Exiting.")
        sys.exit(1)
    
    # Query OSM for dive sites
    print("Querying OSM Overpass API for dive sites...")
    elements = query_dive_sites_osm(bbox)
    
    if not elements:
        print("No dive site elements found in OSM.")
        sys.exit(0)
    
    # Extract site information with progress indicator
    print(f"Extracting site information from {len(elements)} elements...")
    print("=" * 50)
    
    sites = []
    
    for i, el in enumerate(elements, 1):
        # Progress indicator every 100 elements
        if i % 100 == 0 or i == len(elements):
            print(f"Processing element {i}/{len(elements)} ({i/len(elements)*100:.1f}%) - Found {len(sites)} sites so far")
        
        info = extract_site_info(el)
        if info:
            sites.append(info)
    
    print(f"\nExtraction complete!")
    print(f"Found {len(sites)} valid dive sites out of {len(elements)} elements")
    
    if sites:
        print(f"\nSample dive sites found:")
        for i, site in enumerate(sites[:5], 1):  # Show first 5
            print(f"  {i}. {site['name']} ({site['lat']}, {site['lon']})")
        
        if len(sites) > 5:
            print(f"  ... and {len(sites) - 5} more")
        
        # Save to CSV
        filename = save_to_csv(sites, destination)
        if filename:
            print(f"\n✅ Successfully collected dive sites for {destination}")
            print(f"📁 Results saved to: {filename}")
    else:
        print(f"\n❌ No dive sites found for {destination}")
        print("This could be due to:")
        print("  - No dive sites in the area")
        print("  - All sites filtered out as businesses")

if __name__ == "__main__":
    main() 