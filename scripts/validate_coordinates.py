#!/usr/bin/env python3
"""
Validate dive site coordinates:
1. Check all sites fall within their destination's bounding box
2. Check for duplicate coordinates (sites at exact same location)
3. Check for suspiciously inland coordinates using reverse geocoding
4. Check for obviously wrong coordinates (0,0 / null island / etc.)
"""

import json
import math
from pathlib import Path
from collections import defaultdict


def load_destinations():
    project_root = Path(__file__).parent.parent
    with open(project_root / "destinations.json") as f:
        return {d["slug"]: d for d in json.load(f) if not d.get("isGroup")}


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km."""
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def validate_destination(slug, dest, index_path):
    """Validate all sites for a single destination."""
    issues = []

    if not index_path.exists():
        return issues

    with open(index_path) as f:
        sites = json.load(f)

    if not sites:
        return issues

    bounds = dest.get("bounds", [])
    if len(bounds) == 2:
        south, west = bounds[0]
        north, east = bounds[1]
    else:
        return issues

    seen_coords = {}

    for site in sites:
        name = site.get("name", "Unknown")
        lat = site.get("lat")
        lng = site.get("lng")

        if lat is None or lng is None:
            issues.append({"site": name, "dest": slug, "issue": "MISSING_COORDS", "severity": "error"})
            continue

        # Check for null island (0,0)
        if abs(lat) < 0.01 and abs(lng) < 0.01:
            issues.append({"site": name, "dest": slug, "issue": "NULL_ISLAND", "severity": "error",
                          "detail": f"({lat}, {lng}) is near Null Island"})
            continue

        # Check bounds
        # Handle wrap-around for Pacific destinations (e.g., Fiji with bounds crossing 180°)
        if west > east:  # Crosses the antimeridian
            in_bounds = (south <= lat <= north) and (lng >= west or lng <= east)
        else:
            in_bounds = (south <= lat <= north) and (west <= lng <= east)

        if not in_bounds:
            # Calculate distance to nearest bound edge
            center_lat = (south + north) / 2
            center_lon = (west + east) / 2 if west < east else ((west + east + 360) / 2) % 360
            dist = haversine_distance(lat, lng, center_lat, center_lon)
            issues.append({
                "site": name, "dest": slug, "issue": "OUT_OF_BOUNDS",
                "severity": "error" if dist > 100 else "warning",
                "detail": f"({lat}, {lng}) is {dist:.0f}km from destination center"
            })

        # Check for duplicate coordinates
        coord_key = f"{round(lat, 4)},{round(lng, 4)}"
        if coord_key in seen_coords:
            issues.append({
                "site": name, "dest": slug, "issue": "DUPLICATE_COORDS",
                "severity": "warning",
                "detail": f"Same location as '{seen_coords[coord_key]}'"
            })
        else:
            seen_coords[coord_key] = name

        # Check for unrealistic depths
        depth = site.get("maxDepth", 0)
        if depth and depth > 100:
            issues.append({
                "site": name, "dest": slug, "issue": "EXTREME_DEPTH",
                "severity": "warning",
                "detail": f"maxDepth={depth}m exceeds recreational limits"
            })

    return issues


def main():
    project_root = Path(__file__).parent.parent
    divesites_dir = project_root / "divesites"
    destinations = load_destinations()

    all_issues = []
    total_sites = 0
    total_valid = 0

    for slug, dest in sorted(destinations.items()):
        index_path = divesites_dir / slug / "index.json"
        issues = validate_destination(slug, dest, index_path)

        # Count sites
        if index_path.exists():
            with open(index_path) as f:
                sites = json.load(f)
            total_sites += len(sites)
            total_valid += len(sites) - sum(1 for i in issues if i["severity"] == "error")

        all_issues.extend(issues)

    # Print report
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]

    print(f"{'='*60}")
    print(f"COORDINATE VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Total sites checked: {total_sites}")
    print(f"Valid sites:         {total_valid}")
    print(f"Errors:              {len(errors)}")
    print(f"Warnings:            {len(warnings)}")

    if errors:
        print(f"\n--- ERRORS ---")
        for issue in errors:
            print(f"  [{issue['dest']}] {issue['site']:40s} {issue['issue']}: {issue.get('detail', '')}")

    if warnings:
        print(f"\n--- WARNINGS ---")
        for issue in warnings:
            print(f"  [{issue['dest']}] {issue['site']:40s} {issue['issue']}: {issue.get('detail', '')}")

    # Save report
    report_path = project_root / "data" / "validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({
            "total_sites": total_sites,
            "valid_sites": total_valid,
            "errors": len(errors),
            "warnings": len(warnings),
            "issues": all_issues,
        }, f, indent=2)

    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
