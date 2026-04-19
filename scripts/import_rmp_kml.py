#!/usr/bin/env python3
"""
Import dive sites from the Roatan Marine Park canonical KML feed
(https://www.google.com/maps/d/kml?mid=1VAAlEKHNYaqEzG1-mQVxQSmVTYVjdyfA&forcekml=1)
into data/osm_clean/roatan.json.

Pipeline:
  1. Fetch the KML (or read --kml-path).
  2. Parse Placemarks (lng, lat).
  3. Normalize names: collapse RMP's O-for-0 typos, fix title casing, handle
     unique-disambiguation for duplicate names like "UNNAMED".
  4. Drop snorkel-only sites (not dive sites).
  5. Classify site_type from name patterns.
  6. Parse depth from depth-encoded names (e.g. "65Ft Mount" => 20 m).
  7. Bounds-check against destinations.json. Sites outside Roatan's bounds are
     reported and skipped (they should be ingested into a different destination).
  8. Dedupe against the existing osm_clean entries by normalized slug. Existing
     entries are preserved as-is; only genuinely-new sites are appended.
  9. Write the merged file back to data/osm_clean/roatan.json.

Usage:
    python3 scripts/import_rmp_kml.py                 # fetch + import
    python3 scripts/import_rmp_kml.py --dry-run       # report only, no write
    python3 scripts/import_rmp_kml.py --kml-path /tmp/roatan_rmp.kml
"""

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

KML_URL = (
    "https://www.google.com/maps/d/kml"
    "?mid=1VAAlEKHNYaqEzG1-mQVxQSmVTYVjdyfA&forcekml=1"
)
KML_NS = {"k": "http://www.opengis.net/kml/2.2"}

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_PATH = PROJECT_ROOT / "data" / "osm_clean" / "roatan.json"
DESTINATIONS_PATH = PROJECT_ROOT / "destinations.json"
DIVESITES_DIR = PROJECT_ROOT / "divesites" / "roatan"

SOURCE_TAG = "rmp_canonical_2026_03"
ADDED_BY_TAG = "rmp_canonical_kml_import"

# Wreck names (substring match, uppercase) — RMP source uses these.
WRECK_NAME_TOKENS = {
    "WRECK", "AGUILA", "ODYSSEY", "SHANG YING", "DOS ANGUILAS",
    "ATOCHA", "HALLIBURTON", "PRINCE ALBERT",
}


def fetch_kml(path: Path) -> bytes:
    if path:
        return Path(path).read_bytes()
    with urllib.request.urlopen(KML_URL, timeout=30) as resp:
        return resp.read()


def normalize_name(raw: str) -> str:
    """Fix RMP source quirks: O-for-0 typos, weird casing, whitespace."""
    name = re.sub(r"\s+", " ", raw).strip()
    # Replace digit 0 with letter O inside any whitespace-delimited token that
    # contains other letters but no non-zero digits — covers "LIGHTH0USE",
    # "BARREL SP0NGE", "M00NLIGHT", "SP00KY", while leaving numeric tokens
    # like "40FT", "100FT", "Y20" alone.
    def _fix_token(tok: str) -> str:
        if not re.search(r"[A-Za-z]", tok):
            return tok
        if re.search(r"[1-9]", tok):
            return tok
        return tok.replace("0", "O").replace("0", "o" if tok[0].islower() else "O")
    name = " ".join(_fix_token(t) for t in name.split(" "))
    # Insert a space between a leading number and trailing letters in
    # depth-encoded tokens: "65FT" -> "65 FT", "100FTMOUNT" stays untouched
    # (no real cases). Also "40FT" -> "40 FT".
    name = re.sub(r"\b(\d+)(FT)\b", r"\1 \2", name, flags=re.IGNORECASE)
    return _title_case(name)


def _title_case(name: str) -> str:
    """Title-case a name while preserving 's, .com, and existing internal caps."""
    out = []
    for token in name.split(" "):
        if not token:
            continue
        if token.lower().endswith(".com"):
            base = token[:-4]
            out.append(base.capitalize() + ".com")
            continue
        # Handle apostrophes: "DENNIS'S" -> "Dennis's"
        if "'" in token:
            parts = token.split("'")
            parts = [parts[0].capitalize()] + [p.lower() for p in parts[1:]]
            out.append("'".join(parts))
            continue
        # Numeric prefix like "40", "65", "100", "Y1": keep as-is
        if re.match(r"^\d", token) or re.match(r"^Y\d", token, re.IGNORECASE):
            out.append(token.upper() if re.match(r"^Y\d", token, re.IGNORECASE) else token)
            continue
        out.append(token.capitalize())
    return " ".join(out)


def slugify(name: str) -> str:
    """Match scripts/sync_sites.py:sanitize_filename so dedup keys line up."""
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def dedup_slug(name: str) -> str:
    """Aggressive normalized slug for catching near-duplicates across the
    existing osm_clean and the incoming KML.

    Strips repeated trailing nouns ('reef', 'wall', 'point', 'bay', 'bank',
    'cay'), the leading 'the-', and trailing plural 's' on words so
    "Butcher Bank" and "Butchers Bank" both reduce to "butcher", and
    "Half Moon Bay Wall" and "Half Moon Bay" both reduce to "half-moon".
    """
    s = slugify(name)
    s = re.sub(r"^the-", "", s)
    while True:
        new = re.sub(r"-?(reef|wall|point|bank|cay|bay|site)s?$", "", s)
        if new == s:
            break
        s = new
    # Drop trailing plural 's' on the final remaining word so "butchers" ==
    # "butcher" and "drystins" == "drystin".
    s = re.sub(r"(?<=[a-z])s$", "", s)
    return re.sub(r"-+", "-", s).strip("-")


def classify_site_type(name: str) -> str:
    upper = name.upper()
    if any(t in upper for t in WRECK_NAME_TOKENS):
        return "wreck"
    if "WALL" in upper:
        return "wall"
    if "CAVE" in upper or "CAVERN" in upper or "TUNNEL" in upper:
        return "cave"
    if re.match(r"^Y\d+$", upper):
        return "pinnacle"
    if re.search(r"\b\d+\s*FT\b", upper) and (
        "MOUNT" in upper or "SEAMOUNT" in upper or "POINT" in upper or upper.endswith("FT")
    ):
        return "pinnacle"
    if "SEAMOUNT" in upper or "MOUNT" in upper or "PINNACLE" in upper:
        return "pinnacle"
    return "reef"


def parse_depth_meters(name: str) -> int | None:
    """Convert names like '65 Ft Mount' to meters. None if no depth encoded."""
    m = re.search(r"\b(\d+)\s*FT\b", name.upper())
    if not m:
        return None
    feet = int(m.group(1))
    # 1 ft = 0.3048 m, round to nearest meter
    return max(1, round(feet * 0.3048))


def default_difficulty(site_type: str) -> str:
    if site_type == "wreck":
        return "Intermediate"
    if site_type == "cave":
        return "Advanced"
    if site_type == "pinnacle":
        return "Intermediate"
    return "Beginner"


def is_snorkel_site(name: str) -> bool:
    return "SNORKEL" in name.upper()


def parse_placemarks(kml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(kml_bytes)
    placemarks = []
    seen_unnamed = 0
    for pm in root.iter("{http://www.opengis.net/kml/2.2}Placemark"):
        name_el = pm.find("k:name", KML_NS)
        coord_el = pm.find(".//k:coordinates", KML_NS)
        if name_el is None or coord_el is None:
            continue
        raw_name = (name_el.text or "").strip()
        if not raw_name:
            continue
        coord_text = (coord_el.text or "").strip()
        parts = coord_text.split(",")
        if len(parts) < 2:
            continue
        try:
            lng, lat = float(parts[0]), float(parts[1])
        except ValueError:
            continue
        # RMP source has two UNNAMED placemarks; disambiguate by occurrence.
        if raw_name.upper() == "UNNAMED":
            seen_unnamed += 1
            raw_name = f"Unnamed {seen_unnamed}"
        # Note one known typo placemark "LABYRITH" is preserved separately
        # from "LABYRINTH"; both end up in the output with normalized casing.
        placemarks.append({"raw_name": raw_name, "lat": lat, "lng": lng})
    return placemarks


def in_bounds(lat: float, lng: float, bounds: list) -> bool:
    south, west = bounds[0]
    north, east = bounds[1]
    return south <= lat <= north and west <= lng <= east


def load_destination(slug: str) -> dict:
    with open(DESTINATIONS_PATH) as f:
        for d in json.load(f):
            if d["slug"] == slug:
                return d
    raise SystemExit(f"destination not found: {slug}")


def load_existing_osm_clean() -> list[dict]:
    if not OSM_CLEAN_PATH.exists():
        return []
    with open(OSM_CLEAN_PATH) as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would change without writing files.")
    parser.add_argument("--kml-path", default=None,
                        help="Read KML from a local file instead of fetching.")
    args = parser.parse_args()

    print(f"Fetching KML…")
    kml_bytes = fetch_kml(args.kml_path)
    print(f"  ({len(kml_bytes):,} bytes)")

    placemarks = parse_placemarks(kml_bytes)
    print(f"Parsed {len(placemarks)} placemarks from KML.")

    destination = load_destination("roatan")
    bounds = destination["bounds"]
    print(f"Roatan bounds: {bounds}")

    existing = load_existing_osm_clean()
    print(f"Existing osm_clean entries: {len(existing)}")

    existing_dedup_slugs = {dedup_slug(s["name"]) for s in existing}
    existing_exact_slugs = {slugify(s["name"]) for s in existing}

    new_entries = []
    skipped_snorkel = []
    skipped_oob = []
    skipped_dupe = []
    incoming_slugs_seen = set()

    for pm in placemarks:
        raw = pm["raw_name"]
        if is_snorkel_site(raw):
            skipped_snorkel.append(raw)
            continue
        normalized = normalize_name(raw)
        slug = slugify(normalized)
        dslug = dedup_slug(normalized)

        if not in_bounds(pm["lat"], pm["lng"], bounds):
            skipped_oob.append((normalized, pm["lat"], pm["lng"]))
            continue

        if slug in existing_exact_slugs or dslug in existing_dedup_slugs:
            skipped_dupe.append((normalized, "matches existing osm_clean"))
            continue
        if slug in incoming_slugs_seen or dslug in incoming_slugs_seen:
            skipped_dupe.append((normalized, "duplicate within incoming KML"))
            continue
        incoming_slugs_seen.add(slug)
        incoming_slugs_seen.add(dslug)

        site_type = classify_site_type(normalized)
        depth = parse_depth_meters(normalized)
        new_entries.append({
            "name": normalized,
            "lat": pm["lat"],
            "lon": pm["lng"],
            "depth": depth if depth is not None else 18,  # default placeholder
            "site_type": site_type,
            "entry_type": "boat",
            "difficulty": default_difficulty(site_type),
            "tags": {
                "source": SOURCE_TAG,
                "addedBy": ADDED_BY_TAG,
                "coordinate_source": "rmp_canonical_kml_2026_03",
                "validated": False,
                "validation_source": "rmp_canonical_kml_only",
                "depth_inferred_from_name": depth is not None,
            },
        })

    print(f"\n=== Import summary ===")
    print(f"  new entries to add:   {len(new_entries)}")
    print(f"  skipped (snorkel):    {len(skipped_snorkel)}")
    print(f"  skipped (out of box): {len(skipped_oob)}")
    print(f"  skipped (duplicate):  {len(skipped_dupe)}")
    print(f"  total processed:      "
          f"{len(new_entries) + len(skipped_snorkel) + len(skipped_oob) + len(skipped_dupe)}")

    if skipped_oob:
        print(f"\nOut-of-bounds (route to a different destination):")
        for name, lat, lng in skipped_oob[:25]:
            print(f"  - {name:30s} {lat:.4f}, {lng:.4f}")
        if len(skipped_oob) > 25:
            print(f"  …and {len(skipped_oob) - 25} more")

    if skipped_dupe:
        print(f"\nDuplicate-skipped (already in osm_clean or RMP itself):")
        for name, reason in skipped_dupe[:25]:
            print(f"  - {name:30s} ({reason})")
        if len(skipped_dupe) > 25:
            print(f"  …and {len(skipped_dupe) - 25} more")

    if args.dry_run:
        print("\n(dry-run — no files written)")
        return 0

    merged = existing + new_entries
    OSM_CLEAN_PATH.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {len(merged)} entries to {OSM_CLEAN_PATH.relative_to(PROJECT_ROOT)}")

    written_stubs = 0
    for entry in new_entries:
        md_path = DIVESITES_DIR / f"{slugify(entry['name'])}.md"
        if md_path.exists():
            continue
        md_path.write_text(_render_stub(entry), encoding="utf-8")
        written_stubs += 1
    print(f"Wrote {written_stubs} stub markdown files to "
          f"{DIVESITES_DIR.relative_to(PROJECT_ROOT)}/")
    return 0


SITE_TYPE_DISPLAY = {
    "reef": "Coral reef",
    "wall": "Wall dive",
    "wreck": "Wreck dive",
    "cave": "Cave/cavern",
    "muck": "Muck dive",
    "beach": "Beach dive",
    "drift": "Drift dive",
    "pinnacle": "Pinnacle/seamount",
}


def _render_stub(entry: dict) -> str:
    """Render a minimal placeholder markdown for a site with no curated content.

    Body intentionally minimal. The footer flags this as un-validated and
    points to the canonical RMP source so a future research pass can replace
    placeholders with sourced content (see CLAUDE.md anti-hallucination policy).
    """
    name = entry["name"]
    site_type = entry["site_type"]
    type_display = SITE_TYPE_DISPLAY.get(site_type, site_type.capitalize())
    depth = entry.get("depth")
    depth_inferred = entry.get("tags", {}).get("depth_inferred_from_name", False)
    depth_line = (
        f"- **Maximum Depth**: {depth} meters"
        + ("  *(inferred from site name)*" if depth_inferred else
           "  *(placeholder — RMP map does not list depth)*")
    )
    return (
        f"---\n"
        f"name: {name}\n"
        f"lat: {entry['lat']}\n"
        f"lng: {entry['lon']}\n"
        f"difficulty: {entry['difficulty']}\n"
        f"maxDepth: {depth}\n"
        f"entryType: {entry['entry_type']}\n"
        f"siteType: {site_type}\n"
        f"ref: null\n"
        f"osmId: null\n"
        f"addedBy: {entry['tags']['addedBy']}\n"
        f"---\n"
        f"\n"
        f"## {name}\n"
        f"\n"
        f"{name} is a Roatan Marine Park mooring site. The RMP canonical map "
        f"records its location and mooring designation; site-specific details "
        f"(depth profile, marine life, conditions) have not been independently "
        f"validated and are placeholders pending research.\n"
        f"\n"
        f"## Site Information\n"
        f"\n"
        f"- **Location**: Roatán, Honduras\n"
        f"- **Entry Type**: Boat dive\n"
        f"- **Site Type**: {type_display}\n"
        f"- **Difficulty Level**: {entry['difficulty']}  *(placeholder)*\n"
        f"{depth_line}\n"
        f"\n"
        f"---\n"
        f"*Source: [Roatan Marine Park canonical mooring map](https://www.google.com/maps/d/u/0/viewer?mid=1VAAlEKHNYaqEzG1-mQVxQSmVTYVjdyfA). "
        f"Site details not yet validated against dive-operator or ScubaBoard sources.*\n"
    )


if __name__ == "__main__":
    sys.exit(main())
