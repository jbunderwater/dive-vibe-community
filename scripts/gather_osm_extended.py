#!/usr/bin/env python3
"""
Extended Overpass API scraper that discovers dive sites missed by the original
sport=scuba_diving query.

The original gather_osm_all.py only queries:
  - sport=scuba_diving
  - scuba_diving=site
  - dive_site=yes
  - leisure=dive_centre

This extended scraper ALSO queries:
  - seamark:type=wreck (shipwrecks)
  - historic=wreck (historic wrecks)
  - natural=reef (named reefs)
  - natural=cave_entrance (underwater caves)
  - leisure=scuba_diving (alternate tag)

This catches hundreds of additional wrecks and named dive features that are
tagged differently in OSM but are valid dive sites.

Usage:
    python scripts/gather_osm_extended.py                    # All destinations
    python scripts/gather_osm_extended.py -d bermuda         # Specific destination
    python scripts/gather_osm_extended.py --dry-run          # Preview only
    python scripts/gather_osm_extended.py --wrecks-only      # Only wreck features
"""

import json
import os
import sys
import time
import argparse
import re
from pathlib import Path
from collections import Counter

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. pip install requests")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external" / "osm_extended"
DESTINATIONS_FILE = PROJECT_ROOT / "destinations.json"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RATE_LIMIT_SECONDS = 5  # Overpass API rate limit

# Tags that indicate dive shops/businesses (filter these out)
BUSINESS_KEYWORDS = [
    "dive centre", "dive center", "dive shop", "dive school", "dive academy",
    "dive resort", "diving centre", "diving center", "scuba school",
    "watersports", "water sports", "snorkel", "rental", "charters",
]

# OSM tags that indicate businesses
BUSINESS_TAGS = {"shop", "tourism", "amenity", "office"}


def load_destinations():
    with open(DESTINATIONS_FILE) as f:
        return {d["slug"]: d for d in json.load(f)}


def build_overpass_query(bounds, wrecks_only=False):
    """Build an extended Overpass query for dive-relevant features."""
    south, west = bounds[0]
    north, east = bounds[1]
    bbox = f"({south},{west},{north},{east})"

    # Handle antimeridian crossing
    if west > east:
        bbox1 = f"({south},{west},{north},180)"
        bbox2 = f"({south},-180,{north},{east})"
        bboxes = [bbox1, bbox2]
    else:
        bboxes = [bbox]

    queries = []
    for bb in bboxes:
        if not wrecks_only:
            queries.extend([
                f'node["sport"="scuba_diving"]{bb};',
                f'node["scuba_diving"]{bb};',
                f'node["dive_site"]{bb};',
                f'node["leisure"="scuba_diving"]{bb};',
                f'way["sport"="scuba_diving"]{bb};',
                f'way["scuba_diving"]{bb};',
            ])
        # Extended: wrecks and natural features
        queries.extend([
            f'node["seamark:type"="wreck"]{bb};',
            f'node["historic"="wreck"]{bb};',
            f'way["seamark:type"="wreck"]{bb};',
            f'way["historic"="wreck"]{bb};',
            f'relation["seamark:type"="wreck"]{bb};',
        ])
        if not wrecks_only:
            queries.extend([
                f'node["natural"="reef"]["name"]{bb};',
                f'node["natural"="cave_entrance"]["scuba_diving"]{bb};',
                f'way["natural"="reef"]["name"]{bb};',
            ])

    query_body = "\n  ".join(queries)
    return f"""
[out:json][timeout:60];
(
  {query_body}
);
out center body;
"""


def is_business(name, tags):
    """Check if an element is a dive business rather than a dive site."""
    name_lower = (name or "").lower()
    for kw in BUSINESS_KEYWORDS:
        if kw in name_lower:
            return True

    # Check for business-type tags
    for tag_key in BUSINESS_TAGS:
        if tag_key in tags:
            return True

    # Check for phone/address (strong business indicator without dive site tag)
    if tags.get("phone") or tags.get("contact:phone"):
        if not tags.get("scuba_diving") == "site" and not tags.get("dive_site") == "yes":
            return True

    return False


def extract_site_data(element):
    """Extract standardized site data from an OSM element."""
    tags = element.get("tags", {})
    name = tags.get("name") or tags.get("seamark:name") or tags.get("wreck:name")

    if not name:
        return None

    lat = element.get("lat") or (element.get("center", {}) or {}).get("lat")
    lon = element.get("lon") or (element.get("center", {}) or {}).get("lon")

    if not lat or not lon:
        return None

    # Determine site type
    site_type = "reef"
    if tags.get("seamark:type") == "wreck" or tags.get("historic") == "wreck":
        site_type = "wreck"
    elif tags.get("natural") == "reef":
        site_type = "reef"
    elif tags.get("natural") == "cave_entrance":
        site_type = "cave"

    # Extract depth
    depth = None
    for key in ["seamark:wreck:depth", "scuba_diving:maxdepth", "scuba_diving:depth",
                "wreck:depth", "depth", "maxdepth"]:
        val = tags.get(key)
        if val:
            try:
                depth = int(float(str(val).replace("m", "").replace(" ", "").split("-")[-1]))
                if 1 < depth < 300:
                    break
                depth = None
            except (ValueError, IndexError):
                depth = None

    # Extract entry type
    entry_type = None
    entry = tags.get("scuba_diving:entry", "").lower()
    if entry in ("shore", "beach"):
        entry_type = "shore"
    elif entry == "boat":
        entry_type = "boat"

    # Determine difficulty from depth
    difficulty = None
    if depth:
        if depth > 30:
            difficulty = "Advanced"
        elif depth > 18:
            difficulty = "Intermediate"
        else:
            difficulty = "Beginner"

    return {
        "name": name,
        "lat": lat,
        "lon": lon,
        "osm_id": element.get("id"),
        "osm_type": element.get("type"),
        "depth": depth,
        "site_type": site_type,
        "entry_type": entry_type,
        "difficulty": difficulty,
        "tags": {k: v for k, v in tags.items()
                 if k not in ("phone", "contact:phone", "opening_hours",
                              "addr:street", "addr:housenumber")},
    }


def get_existing_names(slug):
    """Get existing site names for deduplication."""
    clean_path = OSM_CLEAN_DIR / f"{slug}.json"
    if not clean_path.exists():
        return set()
    with open(clean_path) as f:
        sites = json.load(f)
    return {s.get("name", "").lower().strip() for s in sites}


def merge_to_clean(slug, new_sites):
    """Merge new sites into the OSM clean data."""
    clean_path = OSM_CLEAN_DIR / f"{slug}.json"

    existing = []
    if clean_path.exists():
        with open(clean_path) as f:
            existing = json.load(f)

    existing_names = {s.get("name", "").lower().strip() for s in existing}
    existing_coords = {(round(s.get("lat", 0), 3), round(s.get("lon", s.get("lng", 0)), 3))
                       for s in existing}

    added = []
    for site in new_sites:
        name_key = site["name"].lower().strip()
        coord_key = (round(site["lat"], 3), round(site["lon"], 3))

        if name_key in existing_names:
            continue
        if coord_key in existing_coords:
            continue

        # Add source tag
        site.setdefault("tags", {})["source"] = "osm_extended"
        site["tags"]["addedBy"] = "extended_overpass"

        existing.append(site)
        added.append(site["name"])
        existing_names.add(name_key)
        existing_coords.add(coord_key)

    if added:
        os.makedirs(clean_path.parent, exist_ok=True)
        with open(clean_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

    return added


def fetch_destination(dest, wrecks_only=False):
    """Fetch extended OSM data for a destination."""
    query = build_overpass_query(dest["bounds"], wrecks_only)

    try:
        resp = requests.get(OVERPASS_URL, params={"data": query}, timeout=120)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"    ERROR: {e}")
        return []

    elements = data.get("elements", [])
    sites = []
    skipped_business = 0
    skipped_unnamed = 0

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("seamark:name") or tags.get("wreck:name")

        if not name:
            skipped_unnamed += 1
            continue

        if is_business(name, tags):
            skipped_business += 1
            continue

        site = extract_site_data(el)
        if site:
            sites.append(site)

    # Deduplicate within results (by name)
    seen = set()
    unique = []
    for s in sites:
        key = s["name"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique


def main():
    parser = argparse.ArgumentParser(description="Extended Overpass API dive site scraper")
    parser.add_argument("--destination", "-d", help="Specific destination slug")
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't merge")
    parser.add_argument("--wrecks-only", action="store_true", help="Only fetch wreck features")
    parser.add_argument("--gaps-only", action="store_true", help="Only process destinations with <10 sites")
    parser.add_argument("--min-sites", type=int, default=10, help="Gap threshold")
    args = parser.parse_args()

    destinations = load_destinations()

    if args.destination:
        slugs = [args.destination]
    elif args.gaps_only:
        slugs = []
        for slug, dest in destinations.items():
            clean_path = OSM_CLEAN_DIR / f"{slug}.json"
            count = 0
            if clean_path.exists():
                with open(clean_path) as f:
                    count = len(json.load(f))
            if count < args.min_sites:
                slugs.append(slug)
    else:
        slugs = sorted(destinations.keys())

    print(f"{'='*60}")
    print(f"EXTENDED OVERPASS SCRAPER {'(WRECKS ONLY)' if args.wrecks_only else ''}")
    print(f"{'='*60}")
    print(f"Processing {len(slugs)} destinations\n")

    total_fetched = 0
    total_merged = 0
    total_new = 0

    for i, slug in enumerate(slugs):
        dest = destinations.get(slug)
        if not dest:
            print(f"  WARNING: '{slug}' not in destinations.json")
            continue

        print(f"  [{i+1}/{len(slugs)}] {dest['name']:30s}", end="", flush=True)

        sites = fetch_destination(dest, args.wrecks_only)
        total_fetched += len(sites)
        print(f" found {len(sites):3d} features", end="")

        if sites and not args.dry_run:
            # Save raw external data
            os.makedirs(EXTERNAL_DIR, exist_ok=True)
            ext_path = EXTERNAL_DIR / f"{slug}.json"
            with open(ext_path, "w", encoding="utf-8") as f:
                json.dump(sites, f, indent=2, ensure_ascii=False)

            # Merge into clean data
            added = merge_to_clean(slug, sites)
            total_merged += len(added)
            if added:
                print(f" → {len(added)} new", end="")
                total_new += len(added)
            else:
                print(f" → 0 new (all dupes)", end="")
        elif sites:
            existing = get_existing_names(slug)
            new_count = sum(1 for s in sites if s["name"].lower().strip() not in existing)
            print(f" → would add {new_count}", end="")

        print()

        # Rate limit
        if i < len(slugs) - 1:
            time.sleep(RATE_LIMIT_SECONDS)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total features found: {total_fetched}")
    if not args.dry_run:
        print(f"New sites merged:     {total_merged}")
    print(f"Destinations queried: {len(slugs)}")

    if not args.dry_run and total_new > 0:
        print(f"\nNext: Run 'python scripts/generate_sites.py' to create markdown files")


if __name__ == "__main__":
    main()
