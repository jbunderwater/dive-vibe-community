#!/usr/bin/env python3
"""
GPS Coordinate Quality Check

Flags dive sites with suspicious coordinates that likely need research-based
correction. Detects:
  1. Suspiciously round coordinates (<=2 decimal places)
  2. Low-precision coordinates (<=3 decimal places, ~100m+ error)
  3. Uniform spacing patterns (grid-like placement suggesting estimation)
  4. Tight clustering around a center point (sites placed near destination center)
  5. Sites outside destination bounding box
  6. Duplicate/near-duplicate coordinates for non-companion sites
  7. All-curated destinations with no OSM-sourced coordinates

Usage:
  python3 scripts/check_gps_quality.py                  # Check all destinations
  python3 scripts/check_gps_quality.py bermuda alor-archipelago  # Check specific ones
  python3 scripts/check_gps_quality.py --summary         # One-line-per-destination overview
"""

import json
import math
import sys
from pathlib import Path
from collections import defaultdict


PROJECT_ROOT = Path(__file__).parent.parent

# Precision thresholds
# 1 decimal place ~ 11km, 2dp ~ 1.1km, 3dp ~ 110m, 4dp ~ 11m, 5dp+ ~ 1m
ROUND_COORD_THRESHOLD = 2      # <= this many decimal places = "suspiciously round"
LOW_PRECISION_THRESHOLD = 3    # <= this many decimal places = "low precision"

# Clustering: if most sites within this radius of centroid, flag it
CLUSTER_RADIUS_KM = 5.0
CLUSTER_FRACTION = 0.7  # flag if >= 70% of sites within cluster radius

# Grid detection: if coordinate deltas are multiples of a step within tolerance
GRID_STEP_TOLERANCE = 0.002  # ~200m


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance between two points in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def decimal_places(value):
    """Count significant decimal places of a float (ignoring trailing zeros in the original data)."""
    s = str(value)
    if '.' not in s:
        return 0
    # Remove trailing zeros to get significant precision
    decimals = s.split('.')[1].rstrip('0')
    return len(decimals) if decimals else 0


def decimal_places_raw(value):
    """Count raw decimal places as stored (including trailing zeros in string repr)."""
    s = str(value)
    if '.' not in s:
        return 0
    return len(s.split('.')[1])


def detect_grid_pattern(coords):
    """Detect if coordinates form a uniform grid pattern.

    Returns (is_grid, step_size) where step_size is the detected grid increment.
    """
    if len(coords) < 4:
        return False, None

    lats = sorted(set(c[0] for c in coords))
    lons = sorted(set(c[1] for c in coords))

    for values in [lats, lons]:
        if len(values) < 3:
            continue
        deltas = [round(values[i+1] - values[i], 6) for i in range(len(values) - 1)]
        if not deltas:
            continue
        # Check if deltas are near-uniform (all close to the median)
        median_delta = sorted(deltas)[len(deltas) // 2]
        if median_delta < 0.005:  # too small to be meaningful
            continue
        uniform_count = sum(1 for d in deltas if abs(d - median_delta) < GRID_STEP_TOLERANCE)
        if uniform_count >= len(deltas) * 0.7:
            return True, median_delta

    return False, None


def check_destination(slug, dest_config, sites):
    """Run all GPS quality checks for a single destination.

    Returns a list of issue dicts with keys: site, issue, severity, detail.
    Also returns destination-level flags.
    """
    issues = []
    dest_flags = []

    if not sites:
        return issues, dest_flags

    bounds = dest_config.get("bounds", [])
    if len(bounds) == 2:
        south, west = bounds[0]
        north, east = bounds[1]
    else:
        south, west, north, east = -90, -180, 90, 180

    center = dest_config.get("center", [(south + north) / 2, (west + east) / 2])

    coords = []
    round_count = 0
    low_precision_count = 0
    osm_count = 0
    curated_count = 0

    for site in sites:
        name = site.get("name", "Unknown")
        lat = site.get("lat")
        lng = site.get("lng")

        if lat is None or lng is None:
            issues.append({"site": name, "issue": "MISSING_COORDS", "severity": "error",
                          "detail": "No lat/lng values"})
            continue

        coords.append((lat, lng, name))

        # --- Check 1: Coordinate precision ---
        lat_dp = decimal_places(lat)
        lng_dp = decimal_places(lng)
        min_dp = min(lat_dp, lng_dp)

        if min_dp <= ROUND_COORD_THRESHOLD:
            round_count += 1
            approx_error = {0: "~111km", 1: "~11km", 2: "~1.1km"}
            issues.append({
                "site": name, "issue": "ROUND_COORDS", "severity": "error",
                "detail": f"({lat}, {lng}) only {min_dp}dp precision ({approx_error.get(min_dp, '~1km+')} error)"
            })
        elif min_dp <= LOW_PRECISION_THRESHOLD:
            low_precision_count += 1
            issues.append({
                "site": name, "issue": "LOW_PRECISION", "severity": "warning",
                "detail": f"({lat}, {lng}) only {min_dp}dp precision (~110m error)"
            })

        # --- Check 2: Out of bounds ---
        if west > east:  # antimeridian crossing
            in_bounds = (south <= lat <= north) and (lng >= west or lng <= east)
        else:
            in_bounds = (south <= lat <= north) and (west <= lng <= east)

        if not in_bounds:
            dist = haversine_km(lat, lng, center[0], center[1])
            issues.append({
                "site": name, "issue": "OUT_OF_BOUNDS", "severity": "error",
                "detail": f"({lat}, {lng}) is {dist:.0f}km from destination center"
            })

        # Track source
        osm_id = site.get("osmId")
        if osm_id:
            osm_count += 1
        else:
            curated_count += 1

    # --- Check 3: Duplicate / near-duplicate coordinates ---
    for i, (lat1, lon1, name1) in enumerate(coords):
        for j, (lat2, lon2, name2) in enumerate(coords):
            if j <= i:
                continue
            dist = haversine_km(lat1, lon1, lat2, lon2)
            if dist < 0.01 and lat1 == lat2 and lon1 == lon2:
                # Exact duplicate - only flag if they shouldn't be co-located
                # (companion wrecks like Montana/Constellation are OK)
                issues.append({
                    "site": f"{name1} / {name2}",
                    "issue": "IDENTICAL_COORDS", "severity": "warning",
                    "detail": f"Both at ({lat1}, {lon1}) — verify if co-located or lazy copy"
                })

    # --- Check 4: Grid pattern detection ---
    if len(coords) >= 4:
        is_grid, step = detect_grid_pattern([(c[0], c[1]) for c in coords])
        if is_grid:
            dest_flags.append({
                "issue": "GRID_PATTERN", "severity": "error",
                "detail": f"Coordinates form uniform grid (step ~{step:.3f}°) — likely fabricated"
            })

    # --- Check 5: Tight clustering around centroid ---
    if len(coords) >= 4:
        avg_lat = sum(c[0] for c in coords) / len(coords)
        avg_lon = sum(c[1] for c in coords) / len(coords)
        within_cluster = sum(
            1 for c in coords
            if haversine_km(c[0], c[1], avg_lat, avg_lon) < CLUSTER_RADIUS_KM
        )
        fraction = within_cluster / len(coords)
        spread = max(haversine_km(c[0], c[1], avg_lat, avg_lon) for c in coords)
        if fraction >= CLUSTER_FRACTION and spread < CLUSTER_RADIUS_KM * 1.5:
            dest_flags.append({
                "issue": "TIGHT_CLUSTER", "severity": "warning",
                "detail": f"{within_cluster}/{len(coords)} sites within {CLUSTER_RADIUS_KM}km of centroid "
                          f"(max spread {spread:.1f}km) — may all be estimated from center point"
            })

    # --- Check 6: All-curated with round coords ---
    if osm_count == 0 and len(coords) >= 4 and round_count >= len(coords) * 0.5:
        dest_flags.append({
            "issue": "ALL_ESTIMATED", "severity": "error",
            "detail": f"All {len(coords)} sites are curated (no OSM data) and "
                      f"{round_count}/{len(coords)} have round coords — needs GPS research"
        })

    # --- Check 7: Uniform longitude/latitude (all sites share same rounded value) ---
    if len(coords) >= 4:
        lat_1dp = [round(c[0], 1) for c in coords]
        lon_1dp = [round(c[1], 1) for c in coords]
        if len(set(lat_1dp)) == 1 and len(set(lon_1dp)) == 1:
            dest_flags.append({
                "issue": "SAME_GRID_CELL", "severity": "warning",
                "detail": f"All sites round to same 0.1° cell ({lat_1dp[0]}, {lon_1dp[0]}) "
                          f"— coordinates may be fabricated near a single point"
            })

    return issues, dest_flags


def load_sites_from_index(slug):
    """Load sites from divesites/{slug}/index.json."""
    index_path = PROJECT_ROOT / "divesites" / slug / "index.json"
    if not index_path.exists():
        return []
    with open(index_path) as f:
        return json.load(f)


def load_sites_from_osm_clean(slug):
    """Load sites from data/osm_clean/{slug}.json (has osmId as osm_id)."""
    osm_path = PROJECT_ROOT / "data" / "osm_clean" / f"{slug}.json"
    if not osm_path.exists():
        return []
    with open(osm_path) as f:
        sites = json.load(f)
    # Normalize field names to match index.json format
    normalized = []
    for s in sites:
        normalized.append({
            "name": s.get("name", "Unknown"),
            "lat": s.get("lat"),
            "lng": s.get("lon"),
            "maxDepth": s.get("depth"),
            "siteType": s.get("site_type"),
            "osmId": s.get("osm_id"),
        })
    return normalized


def print_report(results, summary_mode=False):
    """Print formatted report."""
    total_dests = len(results)
    flagged_dests = sum(1 for r in results.values() if r["issues"] or r["flags"])
    total_issues = sum(len(r["issues"]) for r in results.values())
    total_flags = sum(len(r["flags"]) for r in results.values())
    error_count = sum(
        sum(1 for i in r["issues"] if i["severity"] == "error") +
        sum(1 for f in r["flags"] if f["severity"] == "error")
        for r in results.values()
    )
    warning_count = total_issues + total_flags - error_count

    print(f"{'=' * 70}")
    print(f"GPS COORDINATE QUALITY CHECK")
    print(f"{'=' * 70}")
    print(f"Destinations checked:  {total_dests}")
    print(f"Destinations flagged:  {flagged_dests}")
    print(f"Total site issues:     {total_issues} ({error_count} errors, {warning_count} warnings)")
    print(f"Destination flags:     {total_flags}")

    if summary_mode:
        print(f"\n{'─' * 70}")
        print(f"{'Destination':<35s} {'Sites':>5s} {'Errors':>7s} {'Warns':>6s}  Status")
        print(f"{'─' * 70}")
        for slug in sorted(results.keys()):
            r = results[slug]
            n_sites = r["site_count"]
            n_errors = sum(1 for i in r["issues"] if i["severity"] == "error") + \
                       sum(1 for f in r["flags"] if f["severity"] == "error")
            n_warns = (len(r["issues"]) + len(r["flags"])) - n_errors
            if n_errors > 0:
                status = "NEEDS RESEARCH"
            elif n_warns > 0:
                status = "review"
            else:
                status = "ok"
            if n_errors > 0 or n_warns > 0:
                print(f"  {slug:<33s} {n_sites:>5d} {n_errors:>7d} {n_warns:>6d}  {status}")
        print(f"{'─' * 70}")
        return

    # Detailed output grouped by destination
    for slug in sorted(results.keys()):
        r = results[slug]
        if not r["issues"] and not r["flags"]:
            continue

        errors = [i for i in r["issues"] if i["severity"] == "error"]
        warnings = [i for i in r["issues"] if i["severity"] == "warning"]
        error_flags = [f for f in r["flags"] if f["severity"] == "error"]
        warning_flags = [f for f in r["flags"] if f["severity"] == "warning"]

        print(f"\n{'─' * 70}")
        print(f"  {slug}  ({r['site_count']} sites)")
        print(f"{'─' * 70}")

        if error_flags or warning_flags:
            for f in error_flags + warning_flags:
                severity_tag = "ERROR" if f["severity"] == "error" else "WARN "
                print(f"  [{severity_tag}] {f['issue']}: {f['detail']}")

        for issue in errors:
            print(f"  [ERROR] {issue['site']:35s}  {issue['issue']}: {issue['detail']}")

        for issue in warnings:
            print(f"  [WARN ] {issue['site']:35s}  {issue['issue']}: {issue['detail']}")


def main():
    with open(PROJECT_ROOT / "destinations.json") as f:
        all_dests = {d["slug"]: d for d in json.load(f)}

    # Parse arguments
    args = sys.argv[1:]
    summary_mode = "--summary" in args
    args = [a for a in args if a != "--summary"]

    if args:
        slugs = args
    else:
        slugs = sorted(all_dests.keys())

    results = {}
    for slug in slugs:
        if slug not in all_dests:
            print(f"Warning: '{slug}' not found in destinations.json, skipping")
            continue

        dest_config = all_dests[slug]

        # Prefer index.json (has normalized fields), fall back to osm_clean
        sites = load_sites_from_index(slug)
        if not sites:
            sites = load_sites_from_osm_clean(slug)

        issues, flags = check_destination(slug, dest_config, sites)
        results[slug] = {
            "site_count": len(sites),
            "issues": issues,
            "flags": flags,
        }

    print_report(results, summary_mode=summary_mode)

    # Save JSON report
    report_path = PROJECT_ROOT / "data" / "gps_quality_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nJSON report saved to {report_path}")


if __name__ == "__main__":
    main()
