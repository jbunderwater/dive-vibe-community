#!/usr/bin/env python3
"""
One-time script to integrate Jaibar's community contribution (GitHub Issue #52).

Converts contribution data from divesites/index.json format to osm_clean format,
cleans commercial entries, removes corrupted data, deduplicates against existing
sites (500m radius), and merges into osm_clean files.
"""

import json
import math
import re
from pathlib import Path

CONTRIBUTION_DIR = Path("/tmp/dive-vibe-contribution")
PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"

# Explicit list of commercial entries to remove
COMMERCIAL_NAMES = {
    # Red Sea resorts
    "Sinai Grand Resort",
    "Elphinstone Resort House Reef",
    "Cataract Resort",
    "Akassia Housereef",
    # Israel-Eilat Hebrew dive clubs
    "מועדון צלילה אחלה",
    "מועדון צלילה סיגלה",
    "מועדון צלילה כפר הצוללים",
    "מועדון צלילה סנובה",
    "מועדון צלילה סימור",
    "מועדון צלילה אקווה סטאר",
    # Israel-Mediterranean Hebrew dive clubs + shop
    "מועדון צלילה פוצקר",
    "לצלול מועדון צלילה",
    "מועדון צלילה אינדיגו",
    "מועדון צלילה רוח צפונית אקווה דורה",
    "מועדון צלילה קיסריה העתיקה",
    "מועדון צלילה מכמורת - לי-ים",
    "מועדון צלילה ריף הרצליה",
    "מועדון אשדוד צוללי המזרח התיכון",
    "מועדון צלילה קפוסטא",
    "מועדון צלילה אשקלון צוללי הדרום",
    "Dugit Dive Shop",
}

# Hebrew pattern for dive clubs
COMMERCIAL_PATTERN = re.compile(r"מועדון")


def haversine(lat1, lon1, lat2, lon2):
    """Distance in meters between two GPS points."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sanitize_filename(name):
    """Convert site name to a valid filename (matches generate_sites.py)."""
    sanitized = re.sub(r'[^\w\s-]', '', name.lower())
    sanitized = re.sub(r'[-\s]+', '-', sanitized)
    return sanitized.strip('-')


def is_commercial(name):
    """Check if a site name is a commercial business."""
    if name in COMMERCIAL_NAMES:
        return True
    if COMMERCIAL_PATTERN.search(name):
        return True
    return False


def is_corrupted(site):
    """Check if a site entry is corrupted (timestamp name, bad coords)."""
    if re.match(r'^\d{4}-\d{2}-\d{2}', site.get("name", "")):
        return True
    return False


def convert_to_osm_clean(site):
    """Convert from contribution index.json format to osm_clean format."""
    return {
        "name": site["name"],
        "lat": site["lat"],
        "lon": site["lng"],
        "depth": site.get("maxDepth"),
        "site_type": site.get("siteType") or "",
        "entry_type": site.get("entryType") or "",
        "difficulty": site.get("difficulty") or "",
        "tags": {
            "source": "community_contribution",
            "addedBy": "JaiBar",
            "contribution_ref": "github_issue_52",
        },
    }


def in_bounds(site, bounds):
    """Check if site coordinates fall within destination bounds."""
    south, west = bounds[0]
    north, east = bounds[1]
    return south <= site["lat"] <= north and west <= site["lon"] <= east


def load_existing(slug):
    """Load existing osm_clean data for a destination."""
    path = OSM_CLEAN_DIR / f"{slug}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def find_coordinate_duplicate(site, existing_sites, threshold_m=500):
    """Check if site is within threshold_m meters of any existing site."""
    for existing in existing_sites:
        dist = haversine(site["lat"], site["lon"], existing["lat"], existing["lon"])
        if dist < threshold_m:
            return existing, dist
    return None, None


def process_additions(slug, contrib_path, bounds, stats):
    """Process additions to an existing destination."""
    with open(contrib_path, "r", encoding="utf-8") as f:
        contrib_sites = json.load(f)

    existing = load_existing(slug)
    existing_filenames = {sanitize_filename(s["name"]) for s in existing}

    converted = []
    for site in contrib_sites:
        name = site["name"]

        # Filter commercial
        if is_commercial(name):
            stats["commercial"].append((slug, name))
            continue

        # Filter corrupted
        if is_corrupted(site):
            stats["corrupted"].append((slug, name))
            continue

        osm_site = convert_to_osm_clean(site)

        # Validate bounds
        if not in_bounds(osm_site, bounds):
            stats["out_of_bounds"].append((slug, name, osm_site["lat"], osm_site["lon"]))
            continue

        # Coordinate-based dedup against existing
        match, dist = find_coordinate_duplicate(osm_site, existing, threshold_m=500)
        if match:
            stats["coord_dupes"].append((slug, name, match["name"], round(dist, 1)))
            continue

        # Name/filename collision with existing
        fn = sanitize_filename(name)
        if fn in existing_filenames:
            # Disambiguate by appending a numeric suffix
            i = 2
            while f"{fn}-{i}" in existing_filenames:
                i += 1
            old_name = name
            osm_site["name"] = f"{name} ({i})"
            fn = f"{fn}-{i}"
            stats["disambiguated"].append((slug, old_name, osm_site["name"]))

        existing_filenames.add(fn)
        converted.append(osm_site)

        # Also add to existing list for coord dedup of subsequent sites
        existing.append(osm_site)

    return converted


def process_new_destination(contrib_paths, bounds, stats):
    """Process files for a new destination (Israel combined)."""
    all_sites = []
    for path in contrib_paths:
        with open(path, "r", encoding="utf-8") as f:
            all_sites.extend(json.load(f))

    seen_names = set()
    seen_filenames = set()
    converted = []

    for site in all_sites:
        name = site["name"]

        # Filter commercial
        if is_commercial(name):
            stats["commercial"].append(("israel", name))
            continue

        # Filter corrupted
        if is_corrupted(site):
            stats["corrupted"].append(("israel", name))
            continue

        # Deduplicate by name within the combined file
        if name in seen_names:
            stats["internal_dupes"].append(("israel", name))
            continue
        seen_names.add(name)

        osm_site = convert_to_osm_clean(site)

        # Validate bounds
        if not in_bounds(osm_site, bounds):
            stats["out_of_bounds"].append(("israel", name, osm_site["lat"], osm_site["lon"]))
            continue

        # Coordinate-based dedup within the combined set
        match, dist = find_coordinate_duplicate(osm_site, converted, threshold_m=500)
        if match:
            stats["coord_dupes"].append(("israel", name, match["name"], round(dist, 1)))
            continue

        # Filename collision within combined set
        fn = sanitize_filename(name)
        if fn in seen_filenames:
            i = 2
            while f"{fn}-{i}" in seen_filenames:
                i += 1
            old_name = name
            osm_site["name"] = f"{name} ({i})"
            fn = f"{fn}-{i}"
            stats["disambiguated"].append(("israel", old_name, osm_site["name"]))

        seen_filenames.add(fn)
        converted.append(osm_site)

    return converted


def main():
    # Load destinations for bounds
    with open(PROJECT_ROOT / "destinations.json", "r", encoding="utf-8") as f:
        destinations = json.load(f)
    dest_by_slug = {d["slug"]: d for d in destinations if not d.get("isGroup")}

    stats = {
        "commercial": [],
        "corrupted": [],
        "out_of_bounds": [],
        "coord_dupes": [],
        "internal_dupes": [],
        "disambiguated": [],
    }

    results = {}

    # Process additions to existing destinations
    addition_files = {
        "bahamas": CONTRIBUTION_DIR / "additions_bahamas.json",
        "jordan-aqaba": CONTRIBUTION_DIR / "additions_jordan-aqaba.json",
        "red-sea": CONTRIBUTION_DIR / "additions_red-sea.json",
    }

    for slug, contrib_path in addition_files.items():
        dest = dest_by_slug[slug]
        bounds = dest["bounds"]
        new_sites = process_additions(slug, contrib_path, bounds, stats)
        results[slug] = new_sites

        # Merge into existing osm_clean
        existing = load_existing(slug)
        merged = existing + new_sites
        output_path = OSM_CLEAN_DIR / f"{slug}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  {slug:30s} +{len(new_sites):3d} sites (total: {len(merged)})")

    # Process new Israel destination (combined)
    israel_dest = dest_by_slug["israel"]
    israel_bounds = israel_dest["bounds"]
    israel_sites = process_new_destination(
        [
            CONTRIBUTION_DIR / "new_dest_israel-eilat.json",
            CONTRIBUTION_DIR / "new_dest_israel-mediterranean.json",
        ],
        israel_bounds,
        stats,
    )
    results["israel"] = israel_sites

    output_path = OSM_CLEAN_DIR / "israel.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(israel_sites, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  {'israel':30s} +{len(israel_sites):3d} sites (new destination)")

    # Print report
    print(f"\n{'='*60}")
    print("INTEGRATION REPORT")
    print(f"{'='*60}")

    total_added = sum(len(v) for v in results.values())
    print(f"\nSites added: {total_added}")
    for slug, sites in results.items():
        print(f"  {slug:30s} {len(sites)}")

    if stats["commercial"]:
        print(f"\nCommercial entries removed ({len(stats['commercial'])}):")
        for slug, name in stats["commercial"]:
            print(f"  [{slug}] {name}")

    if stats["corrupted"]:
        print(f"\nCorrupted entries removed ({len(stats['corrupted'])}):")
        for slug, name in stats["corrupted"]:
            print(f"  [{slug}] {name}")

    if stats["out_of_bounds"]:
        print(f"\nOut-of-bounds entries removed ({len(stats['out_of_bounds'])}):")
        for slug, name, lat, lon in stats["out_of_bounds"]:
            print(f"  [{slug}] {name} ({lat}, {lon})")

    if stats["coord_dupes"]:
        print(f"\nCoordinate duplicates removed ({len(stats['coord_dupes'])}):")
        for slug, name, existing_name, dist in stats["coord_dupes"]:
            print(f"  [{slug}] {name} <-> {existing_name} ({dist}m)")

    if stats["internal_dupes"]:
        print(f"\nInternal duplicates removed ({len(stats['internal_dupes'])}):")
        for slug, name in stats["internal_dupes"]:
            print(f"  [{slug}] {name}")

    if stats["disambiguated"]:
        print(f"\nNames disambiguated ({len(stats['disambiguated'])}):")
        for slug, old_name, new_name in stats["disambiguated"]:
            print(f"  [{slug}] {old_name} -> {new_name}")


if __name__ == "__main__":
    main()
