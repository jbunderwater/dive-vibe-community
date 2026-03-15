#!/usr/bin/env python3
"""
Clean OSM data by removing dive shops, dive centres, and other businesses
that are not actual dive sites. Produces cleaned JSON files in data/osm_clean/.
"""

import json
import re
from pathlib import Path

# Keywords in names that indicate a business, not a dive site
BUSINESS_NAME_KEYWORDS = [
    "dive center", "dive centre", "diving center", "diving centre",
    "dive shop", "diving shop", "dive store",
    "dive school", "diving school", "scuba school",
    "dive academy", "diving academy",
    "dive resort", "diving resort",
    "dive club", "diving club",
    "dive operator", "dive company", "diving company",
    "water sports", "watersports", "water sport",
    "travel agency", "tour operator",
    "dive master", "divemaster",
    "scuba center", "scuba centre",
    "snorkel center", "snorkeling center",
]

# Business name patterns (regex)
BUSINESS_PATTERNS = [
    r'\bpadi\b',      # PADI certification center
    r'\bssi\b',       # SSI certification center
    r'\bnaui\b',      # NAUI certification center
    r'\bbsac\b',      # BSAC
    r'\bcmas\b',      # CMAS
    r'\bdivers?\b$',  # ends with "Diver" or "Divers"
    r'^dive\s',       # starts with "Dive " (like "Dive Shop")
    r'\bltd\.?\b',    # Ltd company
    r'\bgmbh\b',      # German company
    r'\binc\.?\b',    # Inc company
    r'\bllc\b',       # LLC
    r'\bs\.?r\.?l\.?\b',  # SRL (Italian company)
]

# Tags that strongly indicate a business
BUSINESS_TAGS = {
    "leisure": ["dive_centre"],
    "shop": ["scuba_diving", "sports", "outdoor", "travel_agency"],
    "tourism": ["travel_agency"],
    "office": ["travel_agent"],
}


def is_business(site):
    """Determine if an OSM entry is a business rather than a dive site."""
    name = site.get("name", "").lower()
    tags = site.get("tags", {})

    reasons = []

    # Check business tags
    for tag_key, tag_values in BUSINESS_TAGS.items():
        if tags.get(tag_key, "").lower() in [v.lower() for v in tag_values]:
            # If it also has dive_site or scuba_diving:site tags, it might be both
            if tags.get("scuba_diving") == "site" or tags.get("dive_site") == "yes":
                continue  # It's tagged as a site, keep it
            reasons.append(f"tag {tag_key}={tags.get(tag_key)}")

    # Check shop tag (any value)
    if "shop" in tags and tags.get("scuba_diving") != "site":
        reasons.append(f"shop={tags['shop']}")

    # Check name keywords
    for kw in BUSINESS_NAME_KEYWORDS:
        if kw in name:
            reasons.append(f"name contains '{kw}'")
            break

    # Check name patterns
    for pattern in BUSINESS_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            reasons.append(f"name matches pattern '{pattern}'")
            break

    # Check for business indicators in tags
    if tags.get("phone") or tags.get("opening_hours") or tags.get("contact:phone"):
        # Sites don't have phone numbers; businesses do
        if not tags.get("scuba_diving") == "site" and not tags.get("dive_site") == "yes":
            reasons.append("has phone/opening_hours")

    # Check for addr: tags (street address = business)
    if tags.get("addr:street") or tags.get("addr:housenumber"):
        if not tags.get("scuba_diving") == "site":
            reasons.append("has street address")

    return (len(reasons) > 0, reasons)


def clean_destination(slug, osm_dir, clean_dir):
    """Clean OSM data for a single destination."""
    src = osm_dir / f"{slug}.json"
    if not src.exists():
        return 0, 0, []

    with open(src) as f:
        sites = json.load(f)

    cleaned = []
    removed = []

    for site in sites:
        is_biz, reasons = is_business(site)
        if is_biz:
            removed.append({"name": site["name"], "reasons": reasons})
        else:
            cleaned.append(site)

    # Write cleaned data
    dst = clean_dir / f"{slug}.json"
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    return len(sites), len(cleaned), removed


def main():
    project_root = Path(__file__).parent.parent
    osm_dir = project_root / "data" / "osm"
    clean_dir = project_root / "data" / "osm_clean"
    clean_dir.mkdir(parents=True, exist_ok=True)

    total_before = 0
    total_after = 0
    all_removed = []

    for f in sorted(osm_dir.glob("*.json")):
        if f.name == "_summary.json":
            continue

        slug = f.stem
        before, after, removed = clean_destination(slug, osm_dir, clean_dir)
        total_before += before
        total_after += after

        if removed:
            print(f"\n{slug}: {before} → {after} (removed {len(removed)})")
            for r in removed:
                print(f"  ✗ {r['name']:50s} [{', '.join(r['reasons'])}]")
            all_removed.extend([{**r, "dest": slug} for r in removed])
        elif before > 0:
            print(f"{slug}: {after} sites (clean)")

    print(f"\n{'='*60}")
    print(f"CLEANUP SUMMARY")
    print(f"{'='*60}")
    print(f"Total sites before: {total_before}")
    print(f"Total sites after:  {total_after}")
    print(f"Removed:            {total_before - total_after} businesses")
    print(f"Removal rate:       {(total_before - total_after)/max(total_before,1)*100:.1f}%")

    # Save removal log
    with open(clean_dir / "_removed.json", "w", encoding="utf-8") as f:
        json.dump(all_removed, f, indent=2)


if __name__ == "__main__":
    main()
