#!/usr/bin/env python3
"""
Populate dive site data for newly added destinations.
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"
DESTINATIONS_FILE = PROJECT_ROOT / "destinations.json"

CURATED_SITES = {
    "roatan": [
        {"name": "Mary's Place", "lat": 16.285, "lon": -86.555, "depth": 40, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "West End Wall", "lat": 16.305, "lon": -86.600, "depth": 30, "site_type": "wall", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Blue Channel", "lat": 16.310, "lon": -86.590, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "El Aguila Wreck", "lat": 16.270, "lon": -86.530, "depth": 33, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Herby's Place", "lat": 16.315, "lon": -86.585, "depth": 18, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Bear's Den", "lat": 16.290, "lon": -86.545, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Spooky Channel", "lat": 16.300, "lon": -86.570, "depth": 28, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Texas", "lat": 16.275, "lon": -86.520, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Calvin's Crack", "lat": 16.295, "lon": -86.560, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Half Moon Bay Wall", "lat": 16.320, "lon": -86.580, "depth": 20, "site_type": "wall", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Overheat Reef", "lat": 16.308, "lon": -86.575, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Butcher Bank", "lat": 16.265, "lon": -86.510, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Peter's Place", "lat": 16.280, "lon": -86.540, "depth": 24, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Lighthouse Reef", "lat": 16.325, "lon": -86.595, "depth": 16, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Odyssey Wreck", "lat": 16.260, "lon": -86.500, "depth": 30, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "providencia-island": [
        {"name": "Felipe's Place", "lat": 13.360, "lon": -81.380, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Manta's City", "lat": 13.370, "lon": -81.400, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Nick's Place", "lat": 13.380, "lon": -81.370, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "The Pinnacle", "lat": 13.350, "lon": -81.390, "depth": 35, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Stairway to Heaven", "lat": 13.340, "lon": -81.360, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Crab Cay Reef", "lat": 13.375, "lon": -81.375, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Blue Diamond", "lat": 13.355, "lon": -81.395, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Tete's Place", "lat": 13.365, "lon": -81.385, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Convento Reef", "lat": 13.385, "lon": -81.365, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Table Rock", "lat": 13.345, "lon": -81.350, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "bocas-del-toro": [
        {"name": "Tiger Rock", "lat": 9.280, "lon": -82.180, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Hospital Point", "lat": 9.340, "lon": -82.240, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "The Playground", "lat": 9.310, "lon": -82.200, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Crawl Cay", "lat": 9.270, "lon": -82.150, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Polo Beach Wall", "lat": 9.350, "lon": -82.260, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Dark Wood Reef", "lat": 9.300, "lon": -82.190, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cayo Coral", "lat": 9.250, "lon": -82.130, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Wreck Rock", "lat": 9.320, "lon": -82.220, "depth": 22, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Punta Juan", "lat": 9.290, "lon": -82.170, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Zapatillas Reef", "lat": 9.260, "lon": -82.080, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Dolphins Bay", "lat": 9.330, "lon": -82.230, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Long Cay Wall", "lat": 9.245, "lon": -82.120, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "coiba-national-park": [
        {"name": "Faro Reef", "lat": 7.620, "lon": -81.720, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Machete Point", "lat": 7.580, "lon": -81.750, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Granito de Oro", "lat": 7.550, "lon": -81.700, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Iglesia Point", "lat": 7.650, "lon": -81.680, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Bahia Damas", "lat": 7.500, "lon": -81.780, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Canales de Afuera", "lat": 7.400, "lon": -81.850, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Jicarita Island", "lat": 7.210, "lon": -81.800, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Santa Cruz", "lat": 7.680, "lon": -81.650, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Montaña Rusa", "lat": 7.450, "lon": -81.820, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Shark Point Coiba", "lat": 7.530, "lon": -81.730, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "cape-town": [
        {"name": "A-Frame", "lat": -34.195, "lon": 18.465, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Shark Alley (False Bay)", "lat": -34.350, "lon": 18.490, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Smitswinkel Bay Wrecks", "lat": -34.250, "lon": 18.470, "depth": 30, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Castle Rock", "lat": -34.200, "lon": 18.460, "depth": 18, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Photographer's Reef", "lat": -34.080, "lon": 18.350, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Tafelberg Reef", "lat": -33.900, "lon": 18.380, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Justin's Caves", "lat": -34.220, "lon": 18.455, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "SAS Transvaal Wreck", "lat": -34.180, "lon": 18.440, "depth": 33, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Outer Castle", "lat": -34.210, "lon": 18.458, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Finlay's Point", "lat": -34.190, "lon": 18.470, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Bos 400 Wreck", "lat": -33.820, "lon": 18.360, "depth": 15, "site_type": "wreck", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Long Beach Kelp Forest", "lat": -34.130, "lon": 18.430, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Cow and Calf", "lat": -34.205, "lon": 18.462, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Partridge Point", "lat": -34.230, "lon": 18.450, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "kenya-coast": [
        {"name": "Kisite Marine Park", "lat": -4.710, "lon": 39.370, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Mpunguti Marine Reserve", "lat": -4.680, "lon": 39.390, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Watamu Marine Park", "lat": -3.370, "lon": 40.020, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Diani Reef", "lat": -4.340, "lon": 39.600, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "MV Dania Wreck", "lat": -4.050, "lon": 39.700, "depth": 30, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Mtwapa Creek", "lat": -3.950, "lon": 39.750, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Nyali Reef", "lat": -4.020, "lon": 39.710, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Shimoni Caves Reef", "lat": -4.650, "lon": 39.380, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Sita Reef", "lat": -4.700, "lon": 39.360, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Funzi Island", "lat": -4.560, "lon": 39.420, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Tewa Caves", "lat": -3.380, "lon": 40.030, "depth": 18, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Malindi Marine Park", "lat": -3.250, "lon": 40.120, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "ustica": [
        {"name": "Grotta della Pastizza", "lat": 38.710, "lon": 13.170, "depth": 22, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Secca della Colombara", "lat": 38.730, "lon": 13.155, "depth": 35, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Scoglio del Medico", "lat": 38.700, "lon": 13.200, "depth": 40, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Punta dell'Arpa", "lat": 38.720, "lon": 13.180, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Grotta Azzurra", "lat": 38.705, "lon": 13.165, "depth": 15, "site_type": "cave", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Punta Gavazzi", "lat": 38.695, "lon": 13.175, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Punta Spalmatore", "lat": 38.715, "lon": 13.150, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Punta Omo Morto", "lat": 38.690, "lon": 13.190, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cala Sidoti", "lat": 38.725, "lon": 13.195, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Secca di Tramontana", "lat": 38.735, "lon": 13.160, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "port-cros": [
        {"name": "La Gabinière", "lat": 43.000, "lon": 6.400, "depth": 40, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "La Pointe de la Galère", "lat": 42.985, "lon": 6.390, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Le Donator Wreck", "lat": 43.020, "lon": 6.380, "depth": 50, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "La Pointe du Vaisseau", "lat": 42.990, "lon": 6.410, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Le Grec Wreck", "lat": 43.030, "lon": 6.370, "depth": 45, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Îlot de la Croix", "lat": 43.005, "lon": 6.420, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "La Palud", "lat": 43.010, "lon": 6.395, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Les Deux Frères", "lat": 43.050, "lon": 6.350, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Pierre de Bagaud", "lat": 42.995, "lon": 6.405, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "La Gabinière Nord", "lat": 43.002, "lon": 6.398, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Plage de la Fausse Monnaie", "lat": 43.015, "lon": 6.385, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Pointe du Cognet", "lat": 42.980, "lon": 6.415, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "triton-bay": [
        {"name": "Little Komodo", "lat": -3.830, "lon": 134.100, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Batu Rufas", "lat": -3.850, "lon": 134.050, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Flasher Beach", "lat": -3.870, "lon": 134.080, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Whale Shark Bagan", "lat": -3.800, "lon": 134.120, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Namatota Channel", "lat": -3.820, "lon": 134.060, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Saruenus Island", "lat": -3.780, "lon": 134.150, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Iris Wall", "lat": -3.860, "lon": 134.070, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "The Corals Garden", "lat": -3.840, "lon": 134.110, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Sawandek Jetty", "lat": -3.810, "lon": 134.130, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Aiduma Island Wall", "lat": -3.900, "lon": 134.040, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "alor-archipelago": [
        {"name": "Clown Valley", "lat": -8.250, "lon": 124.450, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "The Cathedral", "lat": -8.280, "lon": 124.500, "depth": 30, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Kal's Dream", "lat": -8.230, "lon": 124.420, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Shark Close", "lat": -8.300, "lon": 124.530, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Mike's Delight", "lat": -8.260, "lon": 124.470, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Mucky Mosque", "lat": -8.240, "lon": 124.440, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Babylon", "lat": -8.270, "lon": 124.490, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "The Boardroom", "lat": -8.220, "lon": 124.410, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Pantar Strait", "lat": -8.310, "lon": 124.550, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Beang Abang", "lat": -8.200, "lon": 124.400, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "ambon": [
        {"name": "Laha", "lat": -3.710, "lon": 128.090, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Rhino City", "lat": -3.720, "lon": 128.100, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Psychedelic Frogfish Site", "lat": -3.690, "lon": 128.080, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Air Manis", "lat": -3.740, "lon": 128.120, "depth": 18, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Hukurila Cave", "lat": -3.750, "lon": 128.200, "depth": 22, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Nama Point", "lat": -3.700, "lon": 128.085, "depth": 20, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Duke of Sparta Wreck", "lat": -3.680, "lon": 128.070, "depth": 30, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Pintu Kota", "lat": -3.760, "lon": 128.210, "depth": 15, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Twilight Zone", "lat": -3.730, "lon": 128.110, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Amahusu Reef", "lat": -3.715, "lon": 128.095, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
    ],
}


def load_destinations():
    with open(DESTINATIONS_FILE) as f:
        return {d["slug"]: d for d in json.load(f)}


def in_bounds(lat, lon, bounds):
    south, west = bounds[0]
    north, east = bounds[1]
    if west > east:
        return south <= lat <= north and (lon >= west or lon <= east)
    return south <= lat <= north and west <= lon <= east


def merge_sites(slug, new_sites, bounds):
    clean_path = OSM_CLEAN_DIR / f"{slug}.json"
    existing = []
    if clean_path.exists():
        with open(clean_path) as f:
            existing = json.load(f)

    existing_names = {s.get("name", "").lower().strip() for s in existing}
    added = 0
    skipped_bounds = 0
    skipped_dupe = 0

    for site in new_sites:
        if not in_bounds(site["lat"], site["lon"], bounds):
            skipped_bounds += 1
            continue
        if site["name"].lower().strip() in existing_names:
            skipped_dupe += 1
            continue
        existing.append({
            "name": site["name"],
            "lat": site["lat"],
            "lon": site["lon"],
            "depth": site.get("depth"),
            "site_type": site.get("site_type"),
            "entry_type": site.get("entry_type"),
            "difficulty": site.get("difficulty"),
            "tags": {"source": "curated", "addedBy": "fill_new_destinations"},
        })
        existing_names.add(site["name"].lower().strip())
        added += 1

    os.makedirs(clean_path.parent, exist_ok=True)
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return added, skipped_bounds, skipped_dupe


def main():
    destinations = load_destinations()

    print(f"{'='*60}")
    print("POPULATE NEW DESTINATIONS")
    print(f"{'='*60}\n")

    total_added = 0
    for slug, sites in sorted(CURATED_SITES.items()):
        dest = destinations.get(slug)
        if not dest:
            print(f"  {slug:35s} NOT IN destinations.json")
            continue

        added, oob, dupes = merge_sites(slug, sites, dest["bounds"])
        total_added += added

        clean_path = OSM_CLEAN_DIR / f"{slug}.json"
        with open(clean_path) as f:
            total = len(json.load(f))

        print(f"  {dest['name']:30s} +{added:2d} (oob={oob} dupes={dupes}) → {total} total")

    print(f"\n{'='*60}")
    print(f"Total sites added: {total_added}")


if __name__ == "__main__":
    main()
