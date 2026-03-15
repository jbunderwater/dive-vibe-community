#!/usr/bin/env python3
"""
Gather dive site data from OpenStreetMap for all destinations using
bounding boxes already defined in destinations.json (no Google API needed).

Queries Overpass API for nodes/ways tagged with scuba diving related tags
and outputs per-destination JSON files to data/osm/.
"""

import json
import os
import sys
import time
import requests
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "DiveVibe/1.0 (https://github.com/jbunderwater/dive-vibe-community)"
DELAY_BETWEEN_REQUESTS = 3  # seconds, be polite to the API

# Destinations that already have full data
SKIP_SLUGS = {"bonaire", "curacao"}


def load_destinations():
    project_root = Path(__file__).parent.parent
    with open(project_root / "destinations.json", "r", encoding="utf-8") as f:
        return json.load(f)


def query_overpass(south, west, north, east, timeout=60):
    """Query Overpass API for dive sites within bounding box."""
    bbox = f"{south},{west},{north},{east}"
    query = f"""[out:json][timeout:{timeout}];
(
  node["sport"="scuba_diving"]({bbox});
  node["scuba_diving"="site"]({bbox});
  node["dive_site"="yes"]({bbox});
  node["leisure"="dive_centre"]({bbox});
  way["sport"="scuba_diving"]({bbox});
  way["scuba_diving"="site"]({bbox});
  way["dive_site"="yes"]({bbox});
  relation["sport"="scuba_diving"]({bbox});
);
out center tags;"""

    try:
        resp = requests.post(
            OVERPASS_URL,
            data=query,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout + 10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("elements", [])
    except requests.exceptions.HTTPError as e:
        print(f"  HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"  Error: {e}")
        return []


def extract_site_info(element):
    """Extract structured dive site info from an Overpass element."""
    tags = element.get("tags", {})
    name = tags.get("name")
    if not name:
        return None

    lat = element.get("lat") or (element.get("center", {}) or {}).get("lat")
    lon = element.get("lon") or (element.get("center", {}) or {}).get("lon")
    if lat is None or lon is None:
        return None

    # Determine if this is a dive centre vs dive site
    is_dive_centre = tags.get("leisure") == "dive_centre"
    if is_dive_centre and tags.get("sport") != "scuba_diving":
        # Pure dive centre without dive site tag - skip
        return None

    # Extract depth info
    depth = None
    for depth_key in ["scuba_diving:maxdepth", "scuba_diving:depth", "wreck:depth", "depth"]:
        if depth_key in tags:
            try:
                depth = int(str(tags[depth_key]).replace("m", "").replace(" ", "").split("-")[-1])
                break
            except (ValueError, IndexError):
                pass

    # Determine site type
    site_type = "reef"
    if tags.get("historic") == "wreck" or tags.get("seamark:type") == "wreck":
        site_type = "wreck"
    elif tags.get("natural") == "cave_entrance" or "cave" in tags.get("name", "").lower():
        site_type = "cave"
    elif tags.get("natural") == "beach":
        site_type = "beach"
    elif "wall" in tags.get("name", "").lower() or "wall" in tags.get("description", "").lower():
        site_type = "wall"

    # Determine entry type
    entry = tags.get("scuba_diving:entry", "")
    if entry in ("shore", "beach"):
        entry_type = "shore"
    elif entry == "boat":
        entry_type = "boat"
    elif entry == "ladder":
        entry_type = "shore"
    else:
        entry_type = None  # Unknown

    # Determine difficulty
    difficulty = None
    osm_diff = tags.get("scuba_diving:difficulty", "")
    if osm_diff == "1":
        difficulty = "Beginner"
    elif osm_diff == "2":
        difficulty = "Intermediate"
    elif osm_diff == "3":
        difficulty = "Advanced"
    elif depth:
        if depth > 30:
            difficulty = "Advanced"
        elif depth > 18:
            difficulty = "Intermediate"
        else:
            difficulty = "Beginner"

    return {
        "name": name,
        "lat": round(lat, 7),
        "lon": round(lon, 7),
        "osm_id": element.get("id"),
        "osm_type": element.get("type"),
        "depth": depth,
        "site_type": site_type,
        "entry_type": entry_type,
        "difficulty": difficulty,
        "tags": tags,
    }


def gather_for_destination(dest, output_dir):
    """Gather OSM dive sites for a single destination."""
    slug = dest["slug"]
    bounds = dest["bounds"]
    south, west = bounds[0]
    north, east = bounds[1]

    print(f"\n{'='*60}")
    print(f"Gathering: {dest['name']} ({slug})")
    print(f"  Bounds: [{south},{west}] to [{north},{east}]")

    elements = query_overpass(south, west, north, east)
    print(f"  Raw elements: {len(elements)}")

    sites = []
    seen_names = set()
    for el in elements:
        info = extract_site_info(el)
        if info and info["name"] not in seen_names:
            sites.append(info)
            seen_names.add(info["name"])

    print(f"  Unique named sites: {len(sites)}")

    # Save results
    out_file = output_dir / f"{slug}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2, ensure_ascii=False)

    return sites


def main():
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "data" / "osm"
    output_dir.mkdir(parents=True, exist_ok=True)

    destinations = load_destinations()

    # Allow filtering by slug(s) via command line
    filter_slugs = set()
    if len(sys.argv) > 1:
        filter_slugs = set(sys.argv[1:])

    results_summary = []
    for dest in destinations:
        slug = dest["slug"]
        if slug in SKIP_SLUGS:
            print(f"Skipping {slug} (already has data)")
            continue
        if filter_slugs and slug not in filter_slugs:
            continue

        sites = gather_for_destination(dest, output_dir)
        results_summary.append({"name": dest["name"], "slug": slug, "sites": len(sites)})
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    total = 0
    for r in results_summary:
        status = f"{r['sites']} sites" if r["sites"] > 0 else "NO OSM DATA"
        print(f"  {r['name']:40s} {status}")
        total += r["sites"]
    print(f"\nTotal: {total} dive sites across {len(results_summary)} destinations")
    print(f"Destinations with data: {sum(1 for r in results_summary if r['sites'] > 0)}")
    print(f"Destinations without data: {sum(1 for r in results_summary if r['sites'] == 0)}")

    # Save summary
    with open(output_dir / "_summary.json", "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)


if __name__ == "__main__":
    main()
