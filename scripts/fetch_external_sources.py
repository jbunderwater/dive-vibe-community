#!/usr/bin/env python3
"""
Fetch dive site data from external APIs and databases.

Supports multiple sources with a unified interface:
1. PADI Travel API (requires API key)
2. DiveAdvisor API
3. Diveboard API (requires API key)
4. Divesites.com API
5. GBIF species observations (for enrichment)

Each fetcher class handles one source and returns standardized site records.

Usage:
    python scripts/fetch_external_sources.py --source padi --destination fiji
    python scripts/fetch_external_sources.py --source all --list-gaps
    python scripts/fetch_external_sources.py --source diveboard --destination all

Environment variables for API keys:
    PADI_API_KEY        - PADI Travel API key
    DIVEBOARD_API_KEY   - Diveboard API key
    DIVEAPI_KEY         - TheDiveAPI.com key
"""

import json
import os
import sys
import time
import argparse
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"
DESTINATIONS_FILE = PROJECT_ROOT / "destinations.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# Rate limiting helper
_last_request_time = {}


def rate_limit(source, min_interval=1.0):
    """Enforce minimum interval between requests to a source."""
    now = time.time()
    last = _last_request_time.get(source, 0)
    wait = min_interval - (now - last)
    if wait > 0:
        time.sleep(wait)
    _last_request_time[source] = time.time()


def load_destinations():
    with open(DESTINATIONS_FILE) as f:
        return {d["slug"]: d for d in json.load(f) if not d.get("isGroup")}


def get_gap_destinations(min_sites=5):
    """Find destinations with fewer than min_sites dive sites."""
    destinations = load_destinations()
    gaps = []
    for slug, dest in destinations.items():
        clean_path = OSM_CLEAN_DIR / f"{slug}.json"
        count = 0
        if clean_path.exists():
            with open(clean_path) as f:
                count = len(json.load(f))
        if count < min_sites:
            gaps.append({"slug": slug, "name": dest["name"], "count": count, "dest": dest})
    return sorted(gaps, key=lambda x: x["count"])


# =============================================================================
# BASE FETCHER
# =============================================================================

class DiveSiteFetcher(ABC):
    """Base class for external dive site data fetchers."""

    name = "base"
    base_url = ""
    requires_key = False
    rate_limit_seconds = 1.0

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DiveVibeCommunity/1.0 (dive site data aggregator)",
            "Accept": "application/json",
        })

    def _get(self, url, params=None, **kwargs):
        """Make a rate-limited GET request."""
        rate_limit(self.name, self.rate_limit_seconds)
        try:
            resp = self.session.get(url, params=params, timeout=30, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            log.warning(f"[{self.name}] Request failed: {e}")
            return None

    @abstractmethod
    def fetch_sites(self, destination):
        """Fetch dive sites for a destination. Returns list of standardized dicts."""
        pass

    def standardize(self, raw_site):
        """Convert source-specific data to our standard format."""
        return {
            "name": raw_site.get("name", "Unknown"),
            "lat": raw_site.get("lat"),
            "lon": raw_site.get("lon") or raw_site.get("lng"),
            "depth": raw_site.get("depth"),
            "entry_type": raw_site.get("entry_type"),
            "difficulty": raw_site.get("difficulty"),
            "site_type": raw_site.get("site_type", "reef"),
            "source": self.name,
        }


# =============================================================================
# PADI TRAVEL API FETCHER
# =============================================================================

class PADIFetcher(DiveSiteFetcher):
    """
    Fetch from PADI Travel API.

    API endpoint: https://api.global-prod.padi.com/api/v2/travel/
    Requires authentication token.

    To get an API key:
    1. Create a PADI account at padi.com
    2. Contact PADI developer relations for API access
    3. Set PADI_API_KEY environment variable
    """

    name = "padi"
    base_url = "https://api.global-prod.padi.com/api/v2/travel"
    requires_key = True
    rate_limit_seconds = 2.0

    # PADI location IDs for our destinations (discovered from page metadata)
    LOCATION_IDS = {
        "fiji": 164, "bermuda": 29, "bahamas": 17,
        "cayman-islands": 42, "hawaii": 237,
        "papua-new-guinea": 170, "mozambique": 152,
        "south-africa": 200, "tonga": 216,
        "solomon-islands": 192, "vanuatu": 237,
    }

    def fetch_sites(self, destination):
        if not self.api_key:
            log.warning(f"[padi] No API key. Set PADI_API_KEY env var.")
            log.info(f"[padi] Tip: Visit https://www.padi.com/dive-sites/{destination['slug']}/ for manual data")
            return []

        loc_id = self.LOCATION_IDS.get(destination["slug"])
        if not loc_id:
            log.info(f"[padi] No location ID mapped for {destination['slug']}")
            return []

        self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        data = self._get(f"{self.base_url}/dive-sites/", params={
            "location_id": loc_id,
            "limit": 100,
        })

        if not data or "results" not in data:
            return []

        sites = []
        for item in data["results"]:
            site = self.standardize({
                "name": item.get("title") or item.get("name"),
                "lat": item.get("latitude"),
                "lon": item.get("longitude"),
                "depth": item.get("max_depth"),
                "site_type": self._map_type(item.get("dive_site_types", [])),
            })
            if site["lat"] and site["lon"]:
                sites.append(site)

        return sites

    @staticmethod
    def _map_type(types):
        type_map = {"wreck": "wreck", "cave": "cave", "wall": "wall", "reef": "reef"}
        for t in types:
            if t.lower() in type_map:
                return type_map[t.lower()]
        return "reef"


# =============================================================================
# THE DIVE API FETCHER
# =============================================================================

class TheDiveAPIFetcher(DiveSiteFetcher):
    """
    Fetch from TheDiveAPI.com.
    17,000+ dive sites with GPS coordinates.

    To get an API key:
    1. Visit https://thediveapi.com/
    2. Sign up for a plan
    3. Set DIVEAPI_KEY environment variable
    """

    name = "thediveapi"
    base_url = "https://thediveapi.com/api/v1"
    requires_key = True
    rate_limit_seconds = 1.0

    def fetch_sites(self, destination):
        if not self.api_key:
            log.warning(f"[thediveapi] No API key. Set DIVEAPI_KEY env var.")
            return []

        bounds = destination.get("bounds", [[-90, -180], [90, 180]])
        south, west = bounds[0]
        north, east = bounds[1]

        self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        data = self._get(f"{self.base_url}/sites", params={
            "lat_min": south, "lat_max": north,
            "lng_min": west, "lng_max": east,
            "limit": 200,
        })

        if not data:
            return []

        sites_data = data if isinstance(data, list) else data.get("data", data.get("sites", []))
        sites = []
        for item in sites_data:
            site = self.standardize({
                "name": item.get("name"),
                "lat": item.get("lat") or item.get("latitude"),
                "lon": item.get("lng") or item.get("longitude"),
                "depth": item.get("max_depth"),
                "site_type": item.get("type", "reef"),
            })
            if site["name"] and site["lat"] and site["lon"]:
                sites.append(site)

        return sites


# =============================================================================
# DIVEBOARD API FETCHER
# =============================================================================

class DiveboardFetcher(DiveSiteFetcher):
    """
    Fetch from Diveboard API.
    ~100,000 registered divers with species observations.

    API docs: https://github.com/Diveboard/Documentation/blob/master/API.md

    To get an API key:
    1. Email support@diveboard.com for API access
    2. Set DIVEBOARD_API_KEY environment variable
    """

    name = "diveboard"
    base_url = "https://www.diveboard.com/api"
    requires_key = True
    rate_limit_seconds = 2.0

    def fetch_sites(self, destination):
        if not self.api_key:
            log.warning(f"[diveboard] No API key. Email support@diveboard.com for access.")
            return []

        bounds = destination.get("bounds", [[-90, -180], [90, 180]])
        south, west = bounds[0]
        north, east = bounds[1]

        data = self._get(f"{self.base_url}/search/spot", params={
            "apikey": self.api_key,
            "sw_lat": south, "sw_lng": west,
            "ne_lat": north, "ne_lng": east,
        })

        if not data or "result" not in data:
            return []

        sites = []
        for item in data["result"]:
            site = self.standardize({
                "name": item.get("name"),
                "lat": item.get("lat"),
                "lon": item.get("lng"),
                "depth": item.get("max_depth"),
            })
            if site["name"] and site["lat"] and site["lon"]:
                sites.append(site)

        return sites


# =============================================================================
# GBIF SPECIES FETCHER (for enrichment, not site discovery)
# =============================================================================

class GBIFFetcher(DiveSiteFetcher):
    """
    Fetch marine species observations from GBIF.
    Uses the Diveboard citizen science dataset (no key needed).

    Useful for enriching marine life sections with real species data.
    """

    name = "gbif"
    base_url = "https://api.gbif.org/v1"
    requires_key = False
    rate_limit_seconds = 1.0

    # Diveboard dataset key on GBIF
    DIVEBOARD_DATASET = "66f6192f-6cc0-45fd-a2d1-e76f5ae3eab2"

    def fetch_sites(self, destination):
        """Not used for site discovery — use fetch_species instead."""
        return []

    def fetch_species(self, destination, limit=100):
        """Fetch species observations within destination bounds."""
        bounds = destination.get("bounds", [[-90, -180], [90, 180]])
        south, west = bounds[0]
        north, east = bounds[1]

        data = self._get(f"{self.base_url}/occurrence/search", params={
            "datasetKey": self.DIVEBOARD_DATASET,
            "decimalLatitude": f"{south},{north}",
            "decimalLongitude": f"{west},{east}",
            "limit": limit,
            "hasCoordinate": True,
        })

        if not data or "results" not in data:
            return []

        species = {}
        for occ in data["results"]:
            name = occ.get("scientificName") or occ.get("species")
            vernacular = occ.get("vernacularName", "")
            if name:
                if name not in species:
                    species[name] = {"scientific": name, "common": vernacular, "count": 0}
                species[name]["count"] += 1

        return sorted(species.values(), key=lambda x: -x["count"])


# =============================================================================
# COORDINATOR
# =============================================================================

FETCHERS = {
    "padi": PADIFetcher,
    "thediveapi": TheDiveAPIFetcher,
    "diveboard": DiveboardFetcher,
    "gbif": GBIFFetcher,
}

API_KEY_ENV = {
    "padi": "PADI_API_KEY",
    "thediveapi": "DIVEAPI_KEY",
    "diveboard": "DIVEBOARD_API_KEY",
}


def save_external_data(source_name, slug, sites):
    """Save fetched data to data/external/{source}/{slug}.json"""
    out_dir = EXTERNAL_DIR / source_name
    os.makedirs(out_dir, exist_ok=True)
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2, ensure_ascii=False)
    return out_path


def merge_external_to_clean(slug, sites):
    """Merge externally fetched sites into OSM clean data."""
    clean_path = OSM_CLEAN_DIR / f"{slug}.json"

    existing = []
    if clean_path.exists():
        with open(clean_path) as f:
            existing = json.load(f)

    existing_names = {s.get("name", "").lower().strip() for s in existing}
    added = []

    for site in sites:
        if site["name"].lower().strip() in existing_names:
            continue
        clean_site = {
            "name": site["name"],
            "lat": site["lat"],
            "lon": site["lon"],
            "osm_id": None,
            "osm_type": None,
            "depth": site.get("depth"),
            "site_type": site.get("site_type", "reef"),
            "entry_type": site.get("entry_type", "boat"),
            "difficulty": site.get("difficulty", "Intermediate"),
            "tags": {"source": site.get("source", "external"), "addedBy": "external_fetch"},
        }
        existing.append(clean_site)
        added.append(site["name"])

    if added:
        os.makedirs(clean_path.parent, exist_ok=True)
        with open(clean_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

    return added


def main():
    parser = argparse.ArgumentParser(description="Fetch dive site data from external APIs")
    parser.add_argument("--source", "-s", choices=list(FETCHERS.keys()) + ["all"],
                        default="all", help="Data source to query")
    parser.add_argument("--destination", "-d", help="Destination slug (or 'gaps' for gap destinations)")
    parser.add_argument("--list-gaps", action="store_true", help="List destinations needing more data")
    parser.add_argument("--list-sources", action="store_true", help="List available sources and API key status")
    parser.add_argument("--merge", action="store_true", help="Merge fetched data into OSM clean")
    parser.add_argument("--min-sites", type=int, default=5, help="Threshold for gap detection")
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't save")
    args = parser.parse_args()

    if args.list_sources:
        print("Available data sources:\n")
        for name, cls in FETCHERS.items():
            key_var = API_KEY_ENV.get(name, "N/A")
            has_key = bool(os.environ.get(key_var, "")) if key_var != "N/A" else True
            status = "ready" if has_key else "missing key"
            print(f"  {name:15s} {'[KEY]' if cls.requires_key else '[FREE]':8s} {status}")
        return

    if args.list_gaps:
        gaps = get_gap_destinations(args.min_sites)
        print(f"Destinations with fewer than {args.min_sites} dive sites:\n")
        for g in gaps:
            print(f"  {g['slug']:30s} {g['count']:3d} sites  ({g['name']})")
        print(f"\nTotal: {len(gaps)} destinations need data")
        return

    destinations = load_destinations()

    # Determine which destinations to process
    if args.destination == "gaps":
        slugs = [g["slug"] for g in get_gap_destinations(args.min_sites)]
    elif args.destination:
        slugs = [args.destination]
    else:
        print("Specify --destination SLUG, --destination gaps, or --list-gaps")
        return

    # Determine which sources to use
    source_names = list(FETCHERS.keys()) if args.source == "all" else [args.source]

    print(f"{'='*60}")
    print("EXTERNAL SOURCE FETCHER")
    print(f"{'='*60}\n")

    total_fetched = 0
    total_merged = 0

    for slug in slugs:
        dest = destinations.get(slug)
        if not dest:
            log.warning(f"Destination '{slug}' not found")
            continue

        print(f"\n--- {dest['name']} ({slug}) ---")

        for source_name in source_names:
            cls = FETCHERS[source_name]
            key_var = API_KEY_ENV.get(source_name)
            api_key = os.environ.get(key_var, "") if key_var else None

            if cls.requires_key and not api_key:
                log.info(f"  [{source_name}] Skipped (no API key)")
                continue

            fetcher = cls(api_key=api_key)
            sites = fetcher.fetch_sites(dest)

            if sites:
                print(f"  [{source_name}] Fetched {len(sites)} sites")
                total_fetched += len(sites)

                if not args.dry_run:
                    save_external_data(source_name, slug, sites)

                    if args.merge:
                        added = merge_external_to_clean(slug, sites)
                        if added:
                            print(f"  [{source_name}] Merged {len(added)} new sites")
                            total_merged += len(added)
            else:
                log.info(f"  [{source_name}] No sites returned")

    print(f"\n{'='*60}")
    print(f"Total fetched: {total_fetched}")
    if args.merge:
        print(f"Total merged:  {total_merged}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
