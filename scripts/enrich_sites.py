#!/usr/bin/env python3
"""
Enrich dive site data by:
1. Better extraction of existing OSM structured tags (entry, depth, difficulty, type)
2. Regional heuristics for sites missing data
3. Strip remaining commercial/personal tags
4. Final business name filter pass
"""

import json
import os
import re
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).parent.parent
OSM_RAW_DIR = PROJECT_ROOT / "data" / "osm"
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"


# Regional depth/difficulty defaults based on destination characteristics
DESTINATION_DEFAULTS = {
    # Caribbean - mostly reef diving, moderate depths
    "bonaire": {"default_depth": 25, "default_entry": "shore", "default_difficulty": "Intermediate"},
    "curacao": {"default_depth": 25, "default_entry": "shore", "default_difficulty": "Intermediate"},
    "cayman-islands": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "cozumel": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "bahamas": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "belize-barrier-reef": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "turks-and-caicos": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "roatan": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "saba": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "florida-keys": {"default_depth": 15, "default_entry": "boat", "default_difficulty": "Beginner"},
    "dry-tortugas": {"default_depth": 18, "default_entry": "boat", "default_difficulty": "Intermediate"},

    # Pacific
    "palau": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "fiji": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "french-polynesia": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "chuuk-lagoon": {"default_depth": 30, "default_entry": "boat", "default_difficulty": "Advanced"},
    "solomon-islands": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "vanuatu": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "tonga": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "marshall-islands": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "papua-new-guinea": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "cocos-island": {"default_depth": 30, "default_entry": "boat", "default_difficulty": "Advanced"},

    # Asia
    "maldives": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "bali": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "raja-ampat": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "komodo": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "sipadan": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "similan-islands": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "andaman-islands": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "philippines": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "sri-lanka": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "okinawa": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},

    # Red Sea / Middle East
    "red-sea-egypt": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "red-sea-sudan": {"default_depth": 30, "default_entry": "boat", "default_difficulty": "Advanced"},
    "oman": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "aqaba": {"default_depth": 20, "default_entry": "shore", "default_difficulty": "Intermediate"},

    # Africa
    "mozambique": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "zanzibar": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "sodwana-bay": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "madagascar": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "seychelles": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "mauritius": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "djibouti": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},

    # Europe
    "azores": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "iceland": {"default_depth": 15, "default_entry": "shore", "default_difficulty": "Intermediate"},
    "malta": {"default_depth": 25, "default_entry": "shore", "default_difficulty": "Intermediate"},
    "scotland": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "norway-fjords": {"default_depth": 20, "default_entry": "shore", "default_difficulty": "Intermediate"},
    "croatia": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "greece": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "sardinia": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "turkey": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},

    # Americas
    "galapagos": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Advanced"},
    "california-channel-islands": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "bermuda": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "great-lakes-wrecks": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Advanced"},
    "costa-rica": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "hawaii": {"default_depth": 18, "default_entry": "shore", "default_difficulty": "Intermediate"},
    "cenotes-mexico": {"default_depth": 15, "default_entry": "shore", "default_difficulty": "Intermediate"},
    "british-columbia": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"},

    # Oceania
    "great-barrier-reef": {"default_depth": 20, "default_entry": "boat", "default_difficulty": "Beginner"},
    "poor-knights-islands": {"default_depth": 25, "default_entry": "boat", "default_difficulty": "Intermediate"},
    "christmas-island": {"default_depth": 25, "default_entry": "shore", "default_difficulty": "Intermediate"},

    # Arctic
    "greenland": {"default_depth": 15, "default_entry": "boat", "default_difficulty": "Advanced"},
}


# Business name patterns for final filter pass
BUSINESS_PATTERNS = [
    r'\bdive\s*cent(?:er|re)\b',
    r'\bdive\s*shop\b',
    r'\bdive\s*school\b',
    r'\bdive\s*academy\b',
    r'\bdive\s*resort\b',
    r'\bdiving\s*cent(?:er|re)\b',
    r'\bdiving\s*school\b',
    r'\bscuba\s*school\b',
    r'\bscuba\s*cent(?:er|re)\b',
    r'\bPADI\s+\d+\s*star\b',
    r'\bSSI\s+dive\b',
    r'\bdive\s*club\b',
    r'\bdiving\s*club\b',
    r'\bdive\s*training\b',
]

# Tags to strip from cleaned data (commercial/personal)
TAGS_TO_STRIP = {
    "phone", "contact:phone", "contact:mobile", "fax",
    "email", "contact:email",
    "opening_hours",
    "addr:street", "addr:housenumber", "addr:postcode", "addr:city", "addr:country",
    "brand", "operator", "brand:wikidata",
    "internet_access", "internet_access:fee",
    "payment:cash", "payment:credit_cards",
    "wheelchair",
}


def parse_depth(value):
    """Parse a depth value from various OSM formats."""
    if value is None:
        return None
    s = str(value).strip().lower().replace("m", "").replace("ft", "").replace(" ", "")
    # Handle ranges like "10-30"
    if "-" in s:
        parts = s.split("-")
        try:
            return int(float(parts[-1]))
        except (ValueError, IndexError):
            return None
    try:
        return int(float(s))
    except ValueError:
        return None


def extract_entry_type(tags):
    """Extract entry type from all available OSM tags."""
    # Direct entry tag
    entry = tags.get("scuba_diving:entry", "").lower()
    if entry in ("shore", "beach"):
        return "shore"
    if entry == "boat":
        return "boat"
    if entry == "ladder":
        return "shore"

    # Boolean entry tags
    has_boat = tags.get("scuba_diving:entry:boat", "").lower() == "yes"
    has_shore = tags.get("scuba_diving:entry:shore", "").lower() == "yes"
    has_ladder = tags.get("scuba_diving:entry:ladder", "").lower() == "yes"
    has_steps = tags.get("scuba_diving:entry:steps", "").lower() == "yes"
    has_stair = tags.get("scuba_diving:entry:stair", "").lower() == "yes"

    shore_access = has_shore or has_ladder or has_steps or has_stair
    if shore_access and has_boat:
        return "both"
    if shore_access:
        return "shore"
    if has_boat:
        return "boat"

    return None


def extract_depth(tags):
    """Extract maximum depth from all available OSM tags."""
    for key in ["scuba_diving:maxdepth", "scuba_diving:depth", "wreck:depth", "depth", "maxdepth", "wreck:max_depth"]:
        val = parse_depth(tags.get(key))
        if val and 1 < val < 300:
            return val
    return None


def extract_min_depth(tags):
    """Extract minimum depth from OSM tags."""
    for key in ["scuba_diving:mindepth", "mindepth"]:
        val = parse_depth(tags.get(key))
        if val and 0 <= val < 300:
            return val
    return None


def extract_difficulty(tags, depth=None):
    """Extract difficulty from OSM tags or infer from depth."""
    osm_diff = tags.get("scuba_diving:difficulty", "")
    if osm_diff == "1":
        return "Beginner"
    if osm_diff == "2":
        return "Intermediate"
    if osm_diff in ("3", "4", "5"):
        return "Advanced"

    # Infer from depth if available
    if depth:
        if depth > 30:
            return "Advanced"
        if depth > 18:
            return "Intermediate"
        return "Beginner"

    return None


def extract_site_type(tags, name=""):
    """Extract site type from all available OSM tags."""
    # Check wreck indicators
    if (tags.get("historic") == "wreck" or
        tags.get("seamark:type") == "wreck" or
        tags.get("scuba_diving:type") == "wreck" or
        tags.get("scuba_diving:type:wreck", "").lower() == "yes" or
        tags.get("wreck:type")):
        return "wreck"

    # Check cave
    if (tags.get("natural") == "cave_entrance" or
        tags.get("scuba_diving:type:cave", "").lower() == "yes" or
        tags.get("scuba_diving:type") == "cave"):
        return "cave"

    # Check wall
    if (tags.get("scuba_diving:type:wall", "").lower() == "yes" or
        tags.get("scuba_diving:type") == "wall"):
        return "wall"

    # Check drift
    if (tags.get("scuba_diving:type:drift", "").lower() == "yes" or
        tags.get("scuba_diving:type") == "drift"):
        return "drift"

    # Check reef
    if (tags.get("scuba_diving:type:reef", "").lower() == "yes" or
        tags.get("scuba_diving:type") == "reef" or
        tags.get("reef")):
        return "reef"

    # Check from name
    name_lower = name.lower()
    if "wreck" in name_lower or "shipwreck" in name_lower:
        return "wreck"
    if "cave" in name_lower or "cavern" in name_lower or "cenote" in name_lower:
        return "cave"
    if "wall" in name_lower:
        return "wall"

    # Check scuba_diving:type direct value
    st = tags.get("scuba_diving:type", "").lower()
    if st in ("reef", "wall", "cave", "wreck", "drift", "rocks", "sand"):
        return st

    return None


def is_business(name, tags):
    """Final check if a site name suggests a business."""
    name_lower = name.lower()
    for pattern in BUSINESS_PATTERNS:
        if re.search(pattern, name_lower):
            # Allow if explicitly tagged as dive site
            if tags.get("scuba_diving") == "site" or tags.get("dive_site") == "yes":
                continue
            if tags.get("scuba_diving:divespot") == "yes":
                continue
            return True
    return False


def enrich_destination(slug):
    """Enrich all sites for a single destination."""
    clean_path = OSM_CLEAN_DIR / f"{slug}.json"
    raw_path = OSM_RAW_DIR / f"{slug}.json"

    if not clean_path.exists():
        return None, {}

    with open(clean_path) as f:
        clean_sites = json.load(f)

    # Build lookup of raw data by osm_id for richer tag access
    raw_by_id = {}
    if raw_path.exists():
        with open(raw_path) as f:
            raw_sites = json.load(f)
        for site in raw_sites:
            raw_by_id[site.get("osm_id")] = site

    defaults = DESTINATION_DEFAULTS.get(slug, {
        "default_depth": 20, "default_entry": "boat", "default_difficulty": "Intermediate"
    })

    enriched = []
    removed = []
    stats = Counter()

    for site in clean_sites:
        name = site.get("name", "Unknown")
        tags = site.get("tags", {})

        # Also check raw data for richer tags
        raw_site = raw_by_id.get(site.get("osm_id"), {})
        raw_tags = raw_site.get("tags", {})
        # Merge: raw_tags as base, overridden by clean tags
        merged_tags = {**raw_tags, **tags}

        # Final business filter
        if is_business(name, merged_tags):
            removed.append(name)
            stats["removed_business"] += 1
            continue

        # Extract enriched fields
        entry_type = site.get("entry_type") or extract_entry_type(merged_tags)
        depth = site.get("depth") or extract_depth(merged_tags)
        min_depth = extract_min_depth(merged_tags)
        difficulty = site.get("difficulty") or extract_difficulty(merged_tags, depth)
        site_type = extract_site_type(merged_tags, name) or site.get("site_type")

        # Track what was enriched from OSM tags
        if entry_type and not site.get("entry_type"):
            stats["enriched_entry_osm"] += 1
        if depth and not site.get("depth"):
            stats["enriched_depth_osm"] += 1
        if difficulty and not site.get("difficulty"):
            stats["enriched_difficulty_osm"] += 1
        if site_type and site_type != site.get("site_type"):
            stats["enriched_type_osm"] += 1

        # Apply defaults for remaining gaps
        if not entry_type:
            entry_type = defaults["default_entry"]
            stats["default_entry"] += 1
        if not depth:
            depth = defaults["default_depth"]
            stats["default_depth"] += 1
        if not difficulty:
            difficulty = defaults["default_difficulty"]
            stats["default_difficulty"] += 1
        if not site_type:
            site_type = "reef"
            stats["default_type"] += 1

        # Strip commercial/personal tags
        stripped_tags = {k: v for k, v in merged_tags.items() if k not in TAGS_TO_STRIP}

        enriched_site = {
            "name": name,
            "lat": site["lat"],
            "lon": site["lon"],
            "osm_id": site.get("osm_id"),
            "osm_type": site.get("osm_type"),
            "depth": depth,
            "minDepth": min_depth,
            "site_type": site_type,
            "entry_type": entry_type,
            "difficulty": difficulty,
            "tags": stripped_tags,
        }

        # Remove minDepth if None
        if enriched_site["minDepth"] is None:
            del enriched_site["minDepth"]

        enriched.append(enriched_site)

    return enriched, stats, removed


def main():
    print(f"{'='*60}")
    print("DIVE SITE ENRICHMENT")
    print(f"{'='*60}")

    total_stats = Counter()
    total_removed = []
    total_enriched = 0
    total_sites = 0

    for f in sorted(os.listdir(OSM_CLEAN_DIR)):
        if f.startswith("_") or not f.endswith(".json"):
            continue

        slug = f.replace(".json", "")
        result = enrich_destination(slug)
        if result is None:
            continue

        enriched, stats, removed = result

        if not enriched:
            continue

        # Save enriched data back to clean directory
        out_path = OSM_CLEAN_DIR / f
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(enriched, fh, indent=2, ensure_ascii=False)

        total_sites += len(enriched)
        total_enriched += 1
        for k, v in stats.items():
            total_stats[k] += v
        total_removed.extend(removed)

        enriched_count = stats.get("enriched_entry_osm", 0) + stats.get("enriched_depth_osm", 0)
        if enriched_count > 0 or removed:
            print(f"  {slug:40s} {len(enriched)} sites, {enriched_count} fields enriched"
                  + (f", {len(removed)} removed" if removed else ""))

    print(f"\n{'='*60}")
    print("ENRICHMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Total sites processed: {total_sites}")
    print(f"Destinations enriched: {total_enriched}")
    print(f"\nFrom OSM tags:")
    print(f"  Entry type enriched:  {total_stats['enriched_entry_osm']}")
    print(f"  Depth enriched:       {total_stats['enriched_depth_osm']}")
    print(f"  Difficulty enriched:  {total_stats['enriched_difficulty_osm']}")
    print(f"  Site type enriched:   {total_stats['enriched_type_osm']}")
    print(f"\nDefaults applied:")
    print(f"  Entry type defaults:  {total_stats['default_entry']}")
    print(f"  Depth defaults:       {total_stats['default_depth']}")
    print(f"  Difficulty defaults:  {total_stats['default_difficulty']}")
    print(f"  Site type defaults:   {total_stats['default_type']}")

    if total_removed:
        print(f"\nBusiness entries removed ({len(total_removed)}):")
        for name in total_removed:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
