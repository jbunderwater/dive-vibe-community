#!/usr/bin/env python3
"""
PADI dive site scraper.

PADI's dive site directory renders client-side via JavaScript, but the page
metadata and embedded JS contain useful structured data:
  - window.locationId, window.locationSlug
  - window.filters (dive types available)
  - Map marker coordinates (if SSR-rendered)

This scraper also hits PADI's individual dive site pages which contain
SSR-rendered content with:
  - Site name, description
  - Location name, country
  - Dive types (wreck, cave, reef, etc.)
  - Max depth (sometimes)
  - Entry type (sometimes)

For locations where PADI renders dive site lists, we extract site names and
then look up coordinates from known databases.

Usage:
    python scripts/scrape_padi.py --destination fiji
    python scripts/scrape_padi.py --list-countries
    python scripts/scrape_padi.py --destination all --dry-run
"""

import json
import os
import sys
import time
import re
import argparse
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: requires 'requests' and 'beautifulsoup4'. pip install requests beautifulsoup4")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external" / "padi"
DESTINATIONS_FILE = PROJECT_ROOT / "destinations.json"

RATE_LIMIT_SECONDS = 3

# Map our destination slugs to PADI URL slugs
PADI_SLUG_MAP = {
    "fiji": "fiji",
    "bermuda": "bermuda",
    "bahamas": "bahamas",
    "cayman-islands": "cayman-islands",
    "turks-and-caicos": "turks-and-caicos",
    "saba": "saba",
    "british-virgin-islands": "british-virgin-islands",
    "hawaii-big-island": "hawaii",
    "papua-new-guinea": "papua-new-guinea",
    "mozambique": "mozambique",
    "south-africa": "south-africa",
    "tanzania": "tanzania",
    "zanzibar": "zanzibar",
    "seychelles": "seychelles",
    "mauritius": "republic-of-mauritius",
    "tonga": "tonga",
    "solomon-islands": "solomon-islands",
    "vanuatu": "vanuatu",
    "malta-and-gozo": "malta",
    "croatia": "croatia",
    "greece": "greece",
    "turkey": "turkey",
    "red-sea": "egypt",
    "oman": "oman",
    "maldives": "maldives",
    "bali": "bali",
    "raja-ampat": "raja-ampat",
    "great-barrier-reef": "australia",
    "bonaire": "bonaire",
    "curacao": "curacao",
    "cozumel": "cozumel",
    "belize-barrier-reef": "belize",
    "florida-keys": "florida",
    "galapagos-islands": "galapagos",
    "azores": "azores",
    "sardinia": "italy",
    "okinawa": "japan",
    "koh-tao": "koh-tao",
    "sipadan": "sipadan",
    "lembeh-strait": "lembeh-strait",
    "philippines-palawan": "philippines",
    "christmas-island": "christmas-island",
    "poor-knights-islands": "new-zealand",
    "lord-howe-island": "lord-howe-island",
    "ningaloo-reef": "ningaloo-reef",
    "sri-lanka": "sri-lanka",
    "madagascar": "madagascar",
    "djibouti": "djibouti",
    "palau": "palau",
    "french-polynesia": "french-polynesia",
    "chuuk-lagoon": "micronesia",
    "marshall-islands": "marshall-islands",
    "cocos-island": "costa-rica",
    "socorro-islands": "mexico",
    "vancouver-island": "canada",
    "komodo-national-park": "komodo",
    "jordan-aqaba": "jordan",
    "scapa-flow": "scotland",
}

# PADI uses AngularJS SPA on travel.padi.com and React on padi.com
# The padi.com/dive-sites/ pages have SSR metadata we can extract
PADI_BASE = "https://www.padi.com/dive-sites"


def fetch_padi_page(padi_slug):
    """Fetch a PADI dive sites country/region page."""
    url = f"{PADI_BASE}/{padi_slug}/"
    try:
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (compatible; DiveVibeCommunity/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        })
        if resp.status_code == 200:
            return resp.text
        print(f"    HTTP {resp.status_code}")
        return None
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def extract_padi_metadata(html):
    """Extract structured metadata from a PADI dive sites page."""
    data = {}

    # Extract window variables
    for m in re.finditer(r"window\.(\w+)\s*=\s*(['\"]?)(.+?)\2\s*;", html):
        key, _, value = m.groups()
        data[key] = value

    # Extract location info
    loc_id_match = re.search(r"window\.locationId\s*=\s*['\"]?(\d+)", html)
    if loc_id_match:
        data["locationId"] = int(loc_id_match.group(1))

    loc_slug_match = re.search(r"window\.locationSlug\s*=\s*['\"]([^'\"]+)", html)
    if loc_slug_match:
        data["locationSlug"] = loc_slug_match.group(1)

    loc_title_match = re.search(r"window\.locationTitle\s*=\s*['\"]([^'\"]+)", html)
    if loc_title_match:
        data["locationTitle"] = loc_title_match.group(1)

    loc_type_match = re.search(r"window\.locationType\s*=\s*['\"]([^'\"]+)", html)
    if loc_type_match:
        data["locationType"] = loc_type_match.group(1)

    # Extract filter data (tells us what dive types exist at this location)
    filters_match = re.search(r"window\.filters\s*=\s*(\[.*?\]);", html, re.DOTALL)
    if filters_match:
        try:
            data["filters"] = json.loads(filters_match.group(1))
        except json.JSONDecodeError:
            pass

    # Extract map bounds
    bounds_matches = re.findall(r'"lat":\s*(-?[\d.]+)\s*,\s*"lng":\s*(-?[\d.]+)', html)
    if bounds_matches:
        data["bounds"] = [(float(lat), float(lng)) for lat, lng in bounds_matches]

    # Extract dive site links from SSR content
    soup = BeautifulSoup(html, "html.parser")

    # Check for site cards or list items
    site_links = []
    for a in soup.find_all("a", href=re.compile(r"/dive-site/")):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if text and len(text) > 2:
            site_links.append({"name": text, "url": href})

    if site_links:
        data["sites"] = site_links

    # Extract meta description for context
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        data["description"] = meta_desc.get("content", "")

    # Count references to dive site types
    text = soup.get_text()
    data["mentions"] = {
        "wreck": len(re.findall(r'\bwreck\b', text, re.I)),
        "cave": len(re.findall(r'\bcave\b', text, re.I)),
        "wall": len(re.findall(r'\bwall\b', text, re.I)),
        "reef": len(re.findall(r'\breef\b', text, re.I)),
    }

    return data


def extract_site_names_from_text(html):
    """Extract potential dive site names from the page text/HTML."""
    soup = BeautifulSoup(html, "html.parser")
    names = set()

    # Look for bold or heading elements that might be site names
    for tag in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
        text = tag.get_text(strip=True)
        if text and 3 < len(text) < 80:
            # Filter out generic headers
            lower = text.lower()
            if any(kw in lower for kw in ["dive site", "reef", "wreck", "cave", "wall",
                                           "pinnacle", "point", "rock", "island", "bay"]):
                if not any(skip in lower for skip in ["about", "how to", "when to",
                                                       "best time", "getting", "weather"]):
                    names.add(text)

    return names


def scrape_destination(slug, padi_slug):
    """Scrape PADI data for a destination."""
    html = fetch_padi_page(padi_slug)
    if not html:
        return None

    metadata = extract_padi_metadata(html)
    site_names = extract_site_names_from_text(html)
    metadata["extracted_site_names"] = list(site_names)

    return metadata


def main():
    parser = argparse.ArgumentParser(description="Scrape PADI dive site data")
    parser.add_argument("--destination", "-d", help="Destination slug (or 'all' or 'gaps')")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and show metadata only")
    parser.add_argument("--list-countries", action="store_true", help="List PADI slug mappings")
    args = parser.parse_args()

    if args.list_countries:
        print("PADI slug mappings:")
        for our_slug, padi_slug in sorted(PADI_SLUG_MAP.items()):
            print(f"  {our_slug:35s} → {padi_slug}")
        print(f"\nTotal: {len(PADI_SLUG_MAP)} mappings")
        return

    destinations = load_destinations()

    if args.destination == "all":
        slugs = sorted(PADI_SLUG_MAP.keys())
    elif args.destination == "gaps":
        slugs = []
        for slug in PADI_SLUG_MAP:
            clean_path = OSM_CLEAN_DIR / f"{slug}.json"
            count = 0
            if clean_path.exists():
                with open(clean_path) as f:
                    count = len(json.load(f))
            if count < 10:
                slugs.append(slug)
    elif args.destination:
        slugs = [args.destination]
    else:
        print("Specify --destination SLUG, --destination all/gaps, or --list-countries")
        return

    print(f"{'='*60}")
    print("PADI DIVE SITE SCRAPER")
    print(f"{'='*60}\n")

    os.makedirs(EXTERNAL_DIR, exist_ok=True)

    for i, slug in enumerate(slugs):
        padi_slug = PADI_SLUG_MAP.get(slug)
        if not padi_slug:
            print(f"  {slug:30s} no PADI mapping")
            continue

        dest = destinations.get(slug)
        if not dest:
            print(f"  {slug:30s} not in destinations.json")
            continue

        print(f"  [{i+1}/{len(slugs)}] {dest['name']:30s}", end="", flush=True)

        metadata = scrape_destination(slug, padi_slug)
        if not metadata:
            print(" → failed")
            continue

        loc_id = metadata.get("locationId", "?")
        site_count = len(metadata.get("sites", []))
        name_count = len(metadata.get("extracted_site_names", []))
        mentions = metadata.get("mentions", {})

        print(f" id={loc_id} sites={site_count} names={name_count} "
              f"wreck={mentions.get('wreck',0)} reef={mentions.get('reef',0)}")

        # Save metadata
        out_path = EXTERNAL_DIR / f"{slug}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        if metadata.get("sites"):
            print(f"    Sites found:")
            for s in metadata["sites"][:10]:
                print(f"      - {s['name']}")

        if metadata.get("extracted_site_names"):
            print(f"    Extracted names:")
            for n in sorted(metadata["extracted_site_names"])[:10]:
                print(f"      - {n}")

        if i < len(slugs) - 1:
            time.sleep(RATE_LIMIT_SECONDS)

    print(f"\n{'='*60}")
    print(f"Data saved to {EXTERNAL_DIR}")


def load_destinations():
    with open(DESTINATIONS_FILE) as f:
        return {d["slug"]: d for d in json.load(f) if not d.get("isGroup")}


if __name__ == "__main__":
    main()
