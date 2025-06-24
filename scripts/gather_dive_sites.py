import requests
import json
import sys
import time

def get_bounding_box(destination):
    """
    Use Nominatim to get the bounding box for a destination.
    Returns (south, west, north, east) as floats.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": destination,
        "format": "json",
        "limit": 1,
        "polygon_geojson": 0
    }
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": "DiveVibe/1.0"})
        resp.raise_for_status()
        data = resp.json()
        if not data:
            print(f"No results found for '{destination}'")
            return None
        bbox = data[0]['boundingbox']
        return tuple(map(float, bbox))  # (south, north, west, east)
    except Exception as e:
        print(f"Error fetching bounding box: {e}")
        return None

def is_dive_shop(tags):
    """
    Check if an element is a dive shop based on various tags and indicators.
    Returns True if it's a dive shop, False if it's a dive site.
    """
    # Direct dive shop indicators
    dive_shop_indicators = [
        "amenity:dive_centre",
        "tourism:dive_shop", 
        "shop:diving",
        "amenity=dive_centre",
        "tourism=dive_shop",
        "shop=diving"
    ]
    
    # Check for dive shop specific tags
    for indicator in dive_shop_indicators:
        if ":" in indicator:
            key, value = indicator.split(":", 1)
            if tags.get(key) == value:
                return True
        else:
            key, value = indicator.split("=", 1)
            if tags.get(key) == value:
                return True
    
    # Check for business/service indicators that suggest it's a shop
    business_indicators = [
        "email",
        "website", 
        "phone",
        "contact:email",
        "contact:website",
        "contact:phone",
        "opening_hours",
        "operator",
        "brand"
    ]
    
    # If it has business contact info, it's likely a shop
    for indicator in business_indicators:
        if indicator in tags:
            return True
    
    # Check for shop-related tags
    shop_tags = [
        "shop",
        "amenity",
        "tourism"
    ]
    
    # If it has shop-related tags but not dive site specific ones, it might be a shop
    has_shop_tags = any(tag in tags for tag in shop_tags)
    has_dive_site_tags = any(tag in tags for tag in ["dive_site", "scuba_diving"])
    
    if has_shop_tags and not has_dive_site_tags:
        return True
    
    # Check name patterns that suggest it's a shop
    name = tags.get("name", "").lower()
    shop_name_indicators = [
        "dive center",
        "dive centre", 
        "dive shop",
        "diving center",
        "diving centre",
        "diving shop",
        "scuba center",
        "scuba centre",
        "scuba shop",
        "dive store",
        "diving store",
        "scuba store"
    ]
    
    for indicator in shop_name_indicators:
        if indicator in name:
            return True
    
    return False

def query_dive_sites(bbox):
    """
    Query Overpass API for dive sites within the bounding box.
    Returns a list of site dicts.
    """
    south, north, west, east = bbox
    # Overpass QL query (broader)
    query = f"""
    [out:json][timeout:60];
    (
      node["sport"="scuba_diving"]({south},{west},{north},{east});
      node["scuba_diving"="site"]({south},{west},{north},{east});
      node["dive_site"="yes"]({south},{west},{north},{east});
      node["dive_site"]({south},{west},{north},{east});
      node["tourism"="attraction"]["attraction"="dive_site"]({south},{west},{north},{east});
      way["sport"="scuba_diving"]({south},{west},{north},{east});
      way["scuba_diving"="site"]({south},{west},{north},{east});
      way["dive_site"="yes"]({south},{west},{north},{east});
      way["dive_site"]({south},{west},{north},{east});
      way["tourism"="attraction"]["attraction"="dive_site"]({south},{west},{north},{east});
      relation["sport"="scuba_diving"]({south},{west},{north},{east});
      relation["scuba_diving"="site"]({south},{west},{north},{east});
      relation["dive_site"="yes"]({south},{west},{north},{east});
      relation["dive_site"]({south},{west},{north},{east});
      relation["tourism"="attraction"]["attraction"="dive_site"]({south},{west},{north},{east});
    );
    out center tags;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        resp = requests.post(url, data=query, headers={"User-Agent": "DiveVibe/1.0"})
        resp.raise_for_status()
        return resp.json().get("elements", [])
    except Exception as e:
        print(f"Error querying Overpass API: {e}")
        return []

def extract_site_info(element):
    """
    Extract relevant info from an Overpass element.
    Excludes dive shops based on various indicators.
    """
    tags = element.get("tags", {})
    name = tags.get("name")
    if not name:
        return None
    
    # Check if this is a dive shop and exclude it
    if is_dive_shop(tags):
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
        sys.exit(1)
    destination = " ".join(sys.argv[1:])
    print(f"Looking up bounding box for: {destination}")
    bbox = get_bounding_box(destination)
    if not bbox:
        sys.exit(1)
    print(f"Bounding box: {bbox}")
    print("Querying Overpass API for dive sites...")
    elements = query_dive_sites(bbox)
    print(f"Found {len(elements)} elements. Extracting site info...")
    sites = []
    excluded_count = 0
    for el in elements:
        info = extract_site_info(el)
        if info:
            sites.append(info)
        else:
            excluded_count += 1
    
    print(f"Collected {len(sites)} dive sites with names and coordinates.")
    print(f"Excluded {excluded_count} elements (likely dive shops or invalid entries).")
    
    out_file = f"dive_sites_{destination.replace(' ', '_').lower()}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2)
    print(f"Saved results to {out_file}")

if __name__ == "__main__":
    main() 