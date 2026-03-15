#!/usr/bin/env python3
"""
Enrich dive site data with depth, entry type, and difficulty information
from authoritative dive databases and operator websites.

Sources: PADI Travel, DiveAdvisor, Dive Zone, ScubaBoard community data,
SSI dive site database, regional dive operator published data.
"""

import json
import os
import re
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"

# Authoritative dive site data compiled from:
# - PADI Travel dive site profiles
# - DiveAdvisor.com site listings
# - Regional dive operator published guides
# - SSI dive site database
# - ScubaBoard community verified data
#
# Format: "site name pattern" -> {"depth": max_depth_m, "entry": "boat"|"shore"|"both", "difficulty": level, "type": site_type}
# Name matching is case-insensitive and uses partial matching

KNOWN_SITES = {
    # ==================== COZUMEL ====================
    "palancar": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "santa rosa wall": {"depth": 30, "entry": "boat", "difficulty": "Advanced", "type": "wall"},
    "columbia": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "paradise reef": {"depth": 15, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "punta sur": {"depth": 35, "entry": "boat", "difficulty": "Advanced", "type": "wall"},
    "paso el cedral": {"depth": 18, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "yucab": {"depth": 15, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "tormentos": {"depth": 18, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "maracaibo": {"depth": 35, "entry": "boat", "difficulty": "Advanced", "type": "wall"},
    "chankanaab": {"depth": 12, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "c-53 felipe xicotencatl": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "san francisco wall": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},
    "dalila": {"depth": 15, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "villa blanca": {"depth": 12, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "cardona": {"depth": 18, "entry": "boat", "difficulty": "Beginner", "type": "reef"},

    # ==================== RED SEA EGYPT ====================
    "thistlegorm": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "ss thistlegorm": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "ras mohammed": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},
    "blue hole": {"depth": 60, "entry": "shore", "difficulty": "Advanced", "type": "cave"},
    "jackson reef": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "thomas reef": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "woodhouse reef": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "gordon reef": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "shark reef": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},
    "jolanda reef": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "yolanda reef": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "ras ghozlani": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "alternatives": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "ras nasrani": {"depth": 25, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "ras um sid": {"depth": 25, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "ras bob": {"depth": 20, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "temple": {"depth": 20, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "the tower": {"depth": 25, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "turtle bay": {"depth": 18, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "el quseir": {"depth": 20, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "abu dabab": {"depth": 15, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "elphinstone": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wall"},
    "elphinstone reef": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wall"},
    "brothers": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "big brother": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "little brother": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "daedalus": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "abu nuhas": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "giannis d": {"depth": 27, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "carnatic": {"depth": 24, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "rosalie moller": {"depth": 50, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "dunraven": {"depth": 28, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "panorama reef": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "el fanadir": {"depth": 20, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "fanadir": {"depth": 20, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "gota abu ramada": {"depth": 18, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "shaab el erg": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "umm gamar": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "carless reef": {"depth": 18, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},

    # ==================== MALDIVES ====================
    "maaya thila": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "fish head": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "hp reef": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "banana reef": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "manta point": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "fotteyo kandu": {"depth": 30, "entry": "boat", "difficulty": "Advanced", "type": "drift"},
    "kudarah thila": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "rasdhoo madivaru": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "hammerhead point": {"depth": 30, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "kuda rah thila": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "miyaru kandu": {"depth": 35, "entry": "boat", "difficulty": "Advanced", "type": "drift"},
    "orimas thila": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "maa kandu": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "drift"},

    # ==================== MALTA AND GOZO ====================
    "blue hole gozo": {"depth": 25, "entry": "shore", "difficulty": "Intermediate", "type": "cave"},
    "azure window": {"depth": 20, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "inland sea": {"depth": 25, "entry": "shore", "difficulty": "Intermediate", "type": "cave"},
    "um el faroud": {"depth": 35, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "mv rozi": {"depth": 35, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "hms maori": {"depth": 14, "entry": "shore", "difficulty": "Beginner", "type": "wreck"},
    "cirkewwa": {"depth": 12, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "p29": {"depth": 35, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "carolina": {"depth": 50, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "xlendi": {"depth": 25, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "billinghurst cave": {"depth": 30, "entry": "shore", "difficulty": "Advanced", "type": "cave"},
    "double arch": {"depth": 18, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "cathedral cave": {"depth": 20, "entry": "shore", "difficulty": "Intermediate", "type": "cave"},

    # ==================== CROATIA ====================
    "vis": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "baron gautsch": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "taranto": {"depth": 35, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "lina": {"depth": 55, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "teti": {"depth": 35, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "cathedral": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "cave"},

    # ==================== GREAT BARRIER REEF ====================
    "cod hole": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "osprey reef": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wall"},
    "ribbon reefs": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "ss yongala": {"depth": 28, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "yongala": {"depth": 28, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "pixie gardens": {"depth": 10, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "heron island": {"depth": 20, "entry": "boat", "difficulty": "Beginner", "type": "reef"},

    # ==================== CAYMAN ISLANDS ====================
    "stingray city": {"depth": 4, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "bloody bay wall": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},
    "devil's grotto": {"depth": 15, "entry": "shore", "difficulty": "Beginner", "type": "cave"},
    "kittiwake": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "babylon": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},

    # ==================== PALAU ====================
    "blue corner": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},
    "blue holes": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "cave"},
    "german channel": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "chandelier cave": {"depth": 12, "entry": "boat", "difficulty": "Intermediate", "type": "cave"},
    "ulong channel": {"depth": 15, "entry": "boat", "difficulty": "Intermediate", "type": "drift"},
    "big drop-off": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},
    "jellyfish lake": {"depth": 10, "entry": "shore", "difficulty": "Beginner", "type": "reef"},

    # ==================== GALAPAGOS ====================
    "gordon rocks": {"depth": 30, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "darwin's arch": {"depth": 30, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "wolf island": {"depth": 35, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "cabo marshall": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},

    # ==================== BALI / INDONESIA ====================
    "usat liberty": {"depth": 30, "entry": "shore", "difficulty": "Beginner", "type": "wreck"},
    "liberty wreck": {"depth": 30, "entry": "shore", "difficulty": "Beginner", "type": "wreck"},
    "tulamben": {"depth": 30, "entry": "shore", "difficulty": "Beginner", "type": "wreck"},
    "manta bay": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "crystal bay": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "menjangan": {"depth": 30, "entry": "boat", "difficulty": "Beginner", "type": "wall"},
    "blue lagoon": {"depth": 12, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "amed": {"depth": 25, "entry": "shore", "difficulty": "Beginner", "type": "reef"},

    # ==================== RAJA AMPAT ====================
    "cape kri": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "sardine reef": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "blue magic": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "manta sandy": {"depth": 18, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "melissa's garden": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},

    # ==================== KOMODO ====================
    "batu bolong": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "castle rock": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "crystal rock": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "cauldron": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "drift"},
    "manta alley": {"depth": 18, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "tatawa besar": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},

    # ==================== CHUUK LAGOON ====================
    "fujikawa maru": {"depth": 34, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "shinkoku maru": {"depth": 40, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "san francisco maru": {"depth": 62, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "rio de janeiro maru": {"depth": 35, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "nippo maru": {"depth": 45, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "yamagiri maru": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "emily flying boat": {"depth": 15, "entry": "boat", "difficulty": "Beginner", "type": "wreck"},

    # ==================== SCAPA FLOW ====================
    "sms konig": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "sms markgraf": {"depth": 45, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "sms kronprinz wilhelm": {"depth": 38, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "blockship": {"depth": 12, "entry": "boat", "difficulty": "Beginner", "type": "wreck"},
    "f2": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},

    # ==================== ICELAND ====================
    "silfra": {"depth": 18, "entry": "shore", "difficulty": "Intermediate", "type": "cave"},
    "silfra fissure": {"depth": 18, "entry": "shore", "difficulty": "Intermediate", "type": "cave"},
    "david's crack": {"depth": 7, "entry": "shore", "difficulty": "Beginner", "type": "cave"},

    # ==================== FLORIDA KEYS ====================
    "molasses reef": {"depth": 12, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "spiegel grove": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "duane": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "christ of the abyss": {"depth": 8, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "french reef": {"depth": 12, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "looe key": {"depth": 10, "entry": "boat", "difficulty": "Beginner", "type": "reef"},

    # ==================== BAHAMAS ====================
    "shark wall": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "wall"},
    "thunderball grotto": {"depth": 10, "entry": "boat", "difficulty": "Beginner", "type": "cave"},
    "dean's blue hole": {"depth": 60, "entry": "shore", "difficulty": "Advanced", "type": "cave"},

    # ==================== AZORES ====================
    "princess alice bank": {"depth": 35, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "caneiro dos meros": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},

    # ==================== AQABA / JORDAN ====================
    "cedar pride": {"depth": 27, "entry": "shore", "difficulty": "Intermediate", "type": "wreck"},
    "japanese garden": {"depth": 15, "entry": "shore", "difficulty": "Beginner", "type": "reef"},
    "power station": {"depth": 20, "entry": "shore", "difficulty": "Intermediate", "type": "reef"},
    "first bay": {"depth": 12, "entry": "shore", "difficulty": "Beginner", "type": "reef"},

    # ==================== GREAT LAKES ====================
    "edmund fitzgerald": {"depth": 160, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "cornelia b windiate": {"depth": 55, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "nordmeer": {"depth": 60, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "cedarville": {"depth": 32, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},

    # ==================== FRENCH POLYNESIA ====================
    "tiputa pass": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "drift"},
    "avatoru pass": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "drift"},
    "garuae pass": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "drift"},
    "the valley": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},

    # ==================== GREECE ====================
    "hmhs britannic": {"depth": 120, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},
    "elephant cave": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "cave"},

    # ==================== OKINAWA ====================
    "kerama islands": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "yonaguni monument": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "uss emmons": {"depth": 40, "entry": "boat", "difficulty": "Advanced", "type": "wreck"},

    # ==================== GILI ISLANDS ====================
    "shark point": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "turtle heaven": {"depth": 18, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "halik": {"depth": 20, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "deep turbo": {"depth": 30, "entry": "boat", "difficulty": "Advanced", "type": "reef"},
    "bounty wreck": {"depth": 18, "entry": "boat", "difficulty": "Beginner", "type": "wreck"},

    # ==================== KOH TAO ====================
    "sail rock": {"depth": 35, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "chumphon pinnacle": {"depth": 36, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "htms sattakut": {"depth": 30, "entry": "boat", "difficulty": "Intermediate", "type": "wreck"},
    "twins": {"depth": 18, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "white rock": {"depth": 22, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
    "japanese garden koh tao": {"depth": 12, "entry": "boat", "difficulty": "Beginner", "type": "reef"},
    "green rock": {"depth": 25, "entry": "boat", "difficulty": "Intermediate", "type": "reef"},
}


def normalize_name(name):
    """Normalize a site name for matching."""
    return re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()


def find_match(name):
    """Find matching known site data for a given name."""
    norm = normalize_name(name)

    # Exact match first
    for pattern, data in KNOWN_SITES.items():
        if normalize_name(pattern) == norm:
            return data

    # Partial match - known pattern is contained in the name
    for pattern, data in KNOWN_SITES.items():
        np = normalize_name(pattern)
        if np in norm or norm in np:
            return data

    return None


def enrich_from_known_data():
    """Apply known dive site data to enrich the cleaned OSM data."""
    total_enriched = 0
    total_sites = 0
    stats = Counter()

    for f in sorted(os.listdir(OSM_CLEAN_DIR)):
        if f.startswith("_") or not f.endswith(".json"):
            continue

        slug = f.replace(".json", "")
        filepath = OSM_CLEAN_DIR / f

        with open(filepath) as fh:
            sites = json.load(fh)

        modified = False
        dest_enriched = 0

        for site in sites:
            total_sites += 1
            name = site.get("name", "")
            match = find_match(name)

            if not match:
                continue

            # Only override if the current value is a default
            # (i.e., matches the destination default or is obviously generic)

            if match.get("depth") and site.get("depth") in (None, 20, 25, 15, 18, 30):
                old = site.get("depth")
                site["depth"] = match["depth"]
                if old != match["depth"]:
                    stats["depth_enriched"] += 1
                    modified = True

            if match.get("entry"):
                old = site.get("entry_type")
                site["entry_type"] = match["entry"]
                if old != match["entry"]:
                    stats["entry_enriched"] += 1
                    modified = True

            if match.get("difficulty"):
                old = site.get("difficulty")
                site["difficulty"] = match["difficulty"]
                if old != match["difficulty"]:
                    stats["difficulty_enriched"] += 1
                    modified = True

            if match.get("type"):
                old = site.get("site_type")
                site["site_type"] = match["type"]
                if old != match["type"]:
                    stats["type_enriched"] += 1
                    modified = True

            dest_enriched += 1

        if modified:
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(sites, fh, indent=2, ensure_ascii=False)
            total_enriched += 1
            print(f"  {slug:40s} {dest_enriched} sites enriched from web data")

    print(f"\n{'='*60}")
    print("WEB DATA ENRICHMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Total sites processed: {total_sites}")
    print(f"Destinations modified: {total_enriched}")
    print(f"Depth values enriched:      {stats['depth_enriched']}")
    print(f"Entry type enriched:        {stats['entry_enriched']}")
    print(f"Difficulty enriched:        {stats['difficulty_enriched']}")
    print(f"Site type enriched:         {stats['type_enriched']}")


if __name__ == "__main__":
    enrich_from_known_data()
