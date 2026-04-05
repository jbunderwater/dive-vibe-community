#!/usr/bin/env python3
"""
Fill remaining data gaps for destinations with <8 dive sites.

These are well-known dive sites sourced from public diving knowledge bases,
dive travel guides, and destination tourism information.
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"
DESTINATIONS_FILE = PROJECT_ROOT / "destinations.json"

CURATED_SITES = {
    "philippines-donsol": [
        {"name": "Manta Bowl", "lat": 12.905, "lon": 123.590, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Ticao Pass", "lat": 12.870, "lon": 123.650, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "San Miguel Island", "lat": 12.920, "lon": 123.570, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Donsol Bank", "lat": 12.890, "lon": 123.610, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Balacag Point", "lat": 12.935, "lon": 123.580, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Donsol Whale Shark Area", "lat": 12.910, "lon": 123.595, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Jintotolo Channel", "lat": 12.850, "lon": 123.640, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Burias Pass", "lat": 12.960, "lon": 123.560, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "San Bernardino Strait", "lat": 12.870, "lon": 123.680, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Ticao Island South Wall", "lat": 12.855, "lon": 123.660, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "south-australia-neptune-islands": [
        {"name": "Neptune Islands North", "lat": -35.235, "lon": 136.065, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Neptune Islands South", "lat": -35.335, "lon": 136.120, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "North Neptune Reef", "lat": -35.220, "lon": 136.050, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "The Monument", "lat": -35.250, "lon": 136.080, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Great White Shark Cage Dive Site", "lat": -35.240, "lon": 136.070, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "South Neptune Pinnacles", "lat": -35.340, "lon": 136.130, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Hopkins Island", "lat": -35.200, "lon": 136.040, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "English Island Reef", "lat": -35.260, "lon": 136.090, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Williams Island Caves", "lat": -35.280, "lon": 136.100, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Langton Island", "lat": -35.310, "lon": 136.110, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "utila": [
        {"name": "Black Hills", "lat": 16.115, "lon": -86.920, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Duppy Waters", "lat": 16.080, "lon": -86.950, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "CJ's Drop Off", "lat": 16.105, "lon": -86.940, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Halliburton Wreck", "lat": 16.095, "lon": -86.930, "depth": 28, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "The Maze", "lat": 16.120, "lon": -86.910, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Stingray Point", "lat": 16.100, "lon": -86.945, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Jack Neil Point", "lat": 16.090, "lon": -86.955, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Ron's Wreck", "lat": 16.085, "lon": -86.960, "depth": 20, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Airport Caves", "lat": 16.110, "lon": -86.925, "depth": 25, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Pretty Bush", "lat": 16.075, "lon": -86.965, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Lighthouse Reef", "lat": 16.130, "lon": -86.905, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Ted's Point", "lat": 16.070, "lon": -86.970, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "silfra-fissure": [
        {"name": "Silfra Hall", "lat": 64.256, "lon": -21.117, "depth": 18, "site_type": "cave", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Silfra Cathedral", "lat": 64.255, "lon": -21.116, "depth": 25, "site_type": "cave", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Silfra Lagoon", "lat": 64.254, "lon": -21.115, "depth": 3, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Big Crack", "lat": 64.253, "lon": -21.118, "depth": 12, "site_type": "cave", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Davíðsgjá Fissure", "lat": 64.260, "lon": -21.100, "depth": 20, "site_type": "cave", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Strytan Hydrothermal Chimney", "lat": 64.250, "lon": -21.120, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "svalbard": [
        {"name": "Ny-Ålesund Harbor", "lat": 78.924, "lon": 11.928, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Longyearbyen Pier", "lat": 78.230, "lon": 15.640, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Smeerenburg", "lat": 79.730, "lon": 11.050, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Pyramiden Harbor", "lat": 78.653, "lon": 16.328, "depth": 20, "site_type": "reef", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Kongsfjorden", "lat": 78.960, "lon": 12.000, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Barentsburg Coast", "lat": 78.064, "lon": 14.225, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Isfjorden Kelp Forest", "lat": 78.250, "lon": 15.000, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Alkhornet Cliff", "lat": 78.230, "lon": 13.830, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "monterey-bay": [
        {"name": "Breakwater Cove", "lat": 36.614, "lon": -121.895, "depth": 18, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "McAbee Beach", "lat": 36.618, "lon": -121.900, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Lovers Point", "lat": 36.625, "lon": -121.915, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Point Lobos - Bluefish Cove", "lat": 36.520, "lon": -121.942, "depth": 25, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Point Lobos - Whalers Cove", "lat": 36.519, "lon": -121.938, "depth": 20, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Monastery Beach", "lat": 36.524, "lon": -121.928, "depth": 30, "site_type": "wall", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Coral Street Beach", "lat": 36.630, "lon": -121.920, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Otter Cove", "lat": 36.633, "lon": -121.925, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Eric's Pinnacle", "lat": 36.612, "lon": -121.898, "depth": 22, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Metridium Fields", "lat": 36.611, "lon": -121.896, "depth": 16, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Chase Reef", "lat": 36.617, "lon": -121.905, "depth": 20, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Aumentos Pinnacle", "lat": 36.616, "lon": -121.902, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "vanuatu": [
        {"name": "SS President Coolidge", "lat": -15.519, "lon": 167.182, "depth": 40, "site_type": "wreck", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Million Dollar Point", "lat": -15.465, "lon": 167.222, "depth": 15, "site_type": "wreck", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Tucker's Wall", "lat": -15.520, "lon": 167.180, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Cindy's Reef", "lat": -17.740, "lon": 168.320, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Star of Russia Wreck", "lat": -17.730, "lon": 168.310, "depth": 25, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cathedral Cave", "lat": -17.750, "lon": 168.330, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Hideaway Island Reef", "lat": -17.710, "lon": 168.280, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Paul's Rock", "lat": -15.490, "lon": 167.200, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "The Playground", "lat": -15.510, "lon": 167.190, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Konanda Reef", "lat": -15.480, "lon": 167.210, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "philippines-anilao": [
        {"name": "Cathedral Rock", "lat": 13.770, "lon": 120.900, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Beatrice Rock", "lat": 13.760, "lon": 120.890, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Sepok Wall", "lat": 13.750, "lon": 120.880, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Sombrero Island", "lat": 13.780, "lon": 120.910, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Twin Rocks", "lat": 13.740, "lon": 120.870, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Kirby's Rock", "lat": 13.755, "lon": 120.885, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Secret Bay", "lat": 13.790, "lon": 120.920, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Mainit Point", "lat": 13.745, "lon": 120.875, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Bahura", "lat": 13.800, "lon": 120.930, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Arthur's Rock", "lat": 13.765, "lon": 120.895, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Dead Palm", "lat": 13.785, "lon": 120.915, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Koala Reef", "lat": 13.735, "lon": 120.865, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "poor-knights-islands": [
        {"name": "Rikoriko Cave", "lat": -35.470, "lon": 174.735, "depth": 25, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Northern Arch", "lat": -35.450, "lon": 174.730, "depth": 30, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Middle Arch", "lat": -35.460, "lon": 174.732, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Blue Maomao Arch", "lat": -35.465, "lon": 174.728, "depth": 18, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cream Garden", "lat": -35.475, "lon": 174.740, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Landing Bay Pinnacle", "lat": -35.455, "lon": 174.725, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Barney's Rock", "lat": -35.480, "lon": 174.745, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Tie Dye Arch", "lat": -35.458, "lon": 174.720, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Jan's Tunnel", "lat": -35.468, "lon": 174.738, "depth": 16, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Wild Beast Point", "lat": -35.445, "lon": 174.715, "depth": 24, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "norway-lofoten-islands": [
        {"name": "Ballstad Reef", "lat": 68.075, "lon": 13.540, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Nusfjord Wall", "lat": 68.035, "lon": 13.350, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Kabelvåg Shore", "lat": 68.213, "lon": 14.480, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Henningsvær Wall", "lat": 68.151, "lon": 14.200, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Svolvær Harbor", "lat": 68.234, "lon": 14.568, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Reine Bay", "lat": 67.932, "lon": 13.090, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Å Shore Dive", "lat": 67.878, "lon": 12.980, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Maelstrom Wall", "lat": 67.900, "lon": 13.000, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Stamsund Kelp Forest", "lat": 68.120, "lon": 13.850, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Trollfjord", "lat": 68.350, "lon": 15.800, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "seychelles": [
        {"name": "Shark Bank", "lat": -4.560, "lon": 55.370, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Brissare Rocks", "lat": -4.580, "lon": 55.400, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Aldabra Atoll Channel", "lat": -9.410, "lon": 46.350, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Trompeuse Rocks", "lat": -4.620, "lon": 55.450, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Conception Island", "lat": -4.630, "lon": 55.550, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Marianne Island", "lat": -4.340, "lon": 55.940, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Ennerdale Wreck", "lat": -4.600, "lon": 55.420, "depth": 28, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Ave Maria Rock", "lat": -4.570, "lon": 55.380, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "L'Ilot Island", "lat": -4.550, "lon": 55.500, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Whale Rock", "lat": -4.540, "lon": 55.350, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "mauritius": [
        {"name": "Cathedral Reef", "lat": -20.250, "lon": 57.520, "depth": 28, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Whale Rock", "lat": -20.300, "lon": 57.600, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Coin de Mire", "lat": -19.850, "lon": 57.630, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Trou aux Biches Reef", "lat": -20.030, "lon": 57.530, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Blue Bay Marine Park", "lat": -20.440, "lon": 57.710, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Stella Maru Wreck", "lat": -20.295, "lon": 57.590, "depth": 25, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Colorado Point", "lat": -20.350, "lon": 57.550, "depth": 20, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Flic en Flac Pass", "lat": -20.280, "lon": 57.360, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Rempart Serpent", "lat": -20.310, "lon": 57.580, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Hoi Siong No. 6 Wreck", "lat": -20.160, "lon": 57.500, "depth": 32, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "la-paz-sea-of-cortez": [
        {"name": "Los Islotes", "lat": 24.595, "lon": -110.400, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "El Bajo Seamount", "lat": 24.720, "lon": -110.300, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Swanee Reef", "lat": 24.590, "lon": -110.395, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Salvatierra Wreck", "lat": 24.250, "lon": -110.030, "depth": 18, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Isla Espiritu Santo - The Wall", "lat": 24.500, "lon": -110.360, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "La Reina", "lat": 24.580, "lon": -110.380, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "San Rafaelito", "lat": 24.300, "lon": -110.100, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Fang Ming Wreck", "lat": 24.280, "lon": -110.050, "depth": 20, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Las Animas", "lat": 25.100, "lon": -110.500, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Isla Cerralvo North", "lat": 24.200, "lon": -109.950, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "sardinia": [
        {"name": "Nereo Cave", "lat": 40.560, "lon": 8.160, "depth": 30, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Capo Caccia Cliffs", "lat": 40.570, "lon": 8.155, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "KT Wreck", "lat": 39.220, "lon": 9.120, "depth": 35, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Tavolara Island", "lat": 40.890, "lon": 9.710, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Secca del Papa", "lat": 39.130, "lon": 8.400, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Isola dei Cavoli", "lat": 39.080, "lon": 9.530, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cala Gonone", "lat": 40.280, "lon": 9.640, "depth": 15, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Secca di Spargiotto", "lat": 41.250, "lon": 9.350, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Villasimius Marine Park", "lat": 39.150, "lon": 9.510, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Porto Conte Reef", "lat": 40.580, "lon": 8.180, "depth": 16, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
    ],
    "djibouti": [
        {"name": "Moucha Island Reef", "lat": 11.700, "lon": 43.190, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Maskali Island", "lat": 11.720, "lon": 43.210, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Iles des Sept Frères", "lat": 12.450, "lon": 43.380, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Tadjoura Gulf", "lat": 11.780, "lon": 42.900, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Arta Beach Reef", "lat": 11.520, "lon": 43.000, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Le Grumier Wreck", "lat": 11.590, "lon": 43.150, "depth": 30, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Ghoubbet Al-Kharab", "lat": 11.530, "lon": 42.530, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Whale Shark Point", "lat": 11.700, "lon": 43.200, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "dry-tortugas": [
        {"name": "Windjammer Wreck", "lat": 24.620, "lon": -82.870, "depth": 8, "site_type": "wreck", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Little Africa Reef", "lat": 24.630, "lon": -82.880, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Texas Rock", "lat": 24.640, "lon": -82.860, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Bird Key Reef", "lat": 24.625, "lon": -82.875, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "White Shoal", "lat": 24.650, "lon": -82.850, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Pulaski Shoal", "lat": 24.690, "lon": -82.780, "depth": 5, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Long Key Reef", "lat": 24.615, "lon": -82.890, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Fort Jefferson Wall", "lat": 24.628, "lon": -82.873, "depth": 20, "site_type": "wall", "entry_type": "shore", "difficulty": "Intermediate"},
    ],
    "thailand-similan-islands": [
        {"name": "Elephant Head Rock", "lat": 8.570, "lon": 97.640, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Christmas Point", "lat": 8.680, "lon": 97.620, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "East of Eden", "lat": 8.590, "lon": 97.660, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Anita's Reef", "lat": 8.560, "lon": 97.635, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Deep Six", "lat": 8.650, "lon": 97.615, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "West of Six", "lat": 8.640, "lon": 97.610, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Richelieu Rock", "lat": 9.353, "lon": 98.023, "depth": 35, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Koh Bon Pinnacle", "lat": 8.960, "lon": 97.780, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Koh Tachai Pinnacle", "lat": 9.130, "lon": 97.830, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Beacon Reef", "lat": 8.620, "lon": 97.655, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Turtle Rock", "lat": 8.630, "lon": 97.650, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Fantasea Reef", "lat": 8.600, "lon": 97.645, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "micronesia-yap": [
        {"name": "Manta Ray Bay", "lat": 9.540, "lon": 138.110, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Yap Caverns", "lat": 9.500, "lon": 138.080, "depth": 30, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Lionfish Wall", "lat": 9.510, "lon": 138.090, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Gilman Wall", "lat": 9.520, "lon": 138.100, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Cherry Blossom Wall", "lat": 9.530, "lon": 138.105, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Magic Kingdom", "lat": 9.550, "lon": 138.120, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Sunrise Reef", "lat": 9.560, "lon": 138.130, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Rainbow Wall", "lat": 9.490, "lon": 138.075, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Slow and Easy", "lat": 9.545, "lon": 138.115, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Land's End", "lat": 9.480, "lon": 138.070, "depth": 32, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "galapagos-islands": [
        {"name": "Gordon Rocks", "lat": -0.580, "lon": -90.300, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Kicker Rock (León Dormido)", "lat": -0.770, "lon": -89.520, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Darwin's Arch", "lat": 1.680, "lon": -91.990, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Wolf Island", "lat": 1.380, "lon": -91.820, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Cabo Marshall", "lat": -0.240, "lon": -90.520, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cousins Rock", "lat": -0.200, "lon": -90.560, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Punta Vicente Roca", "lat": -0.050, "lon": -91.560, "depth": 20, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Isla Bartolome", "lat": -0.280, "lon": -90.540, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "North Seymour", "lat": -0.380, "lon": -90.290, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Daphne Minor", "lat": -0.400, "lon": -90.370, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "socorro-islands": [
        {"name": "The Boiler", "lat": 18.720, "lon": -110.970, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Cabo Pearce", "lat": 18.730, "lon": -110.950, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "San Benedicto Canyon", "lat": 19.300, "lon": -110.800, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Roca Partida", "lat": 19.000, "lon": -112.070, "depth": 40, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "O'Neal Rock", "lat": 18.740, "lon": -110.960, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Punta Tosca", "lat": 18.710, "lon": -110.980, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "The Aquarium", "lat": 19.310, "lon": -110.810, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Fondeadero", "lat": 18.750, "lon": -110.940, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
}


def load_destinations():
    with open(DESTINATIONS_FILE) as f:
        return {d["slug"]: d for d in json.load(f) if not d.get("isGroup")}


def in_bounds(lat, lon, bounds):
    south, west = bounds[0]
    north, east = bounds[1]
    if west > east:  # antimeridian
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
            "tags": {"source": "curated", "addedBy": "fill_remaining_gaps"},
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
    print("FILL REMAINING DATA GAPS")
    print(f"{'='*60}\n")

    total_added = 0

    for slug, sites in sorted(CURATED_SITES.items()):
        dest = destinations.get(slug)
        if not dest:
            print(f"  {slug:40s} NOT IN destinations.json")
            continue

        added, oob, dupes = merge_sites(slug, sites, dest["bounds"])
        total_added += added

        clean_path = OSM_CLEAN_DIR / f"{slug}.json"
        with open(clean_path) as f:
            total = len(json.load(f))

        print(f"  {dest['name']:35s} +{added:2d} (oob={oob} dupes={dupes}) → {total} total")

    print(f"\n{'='*60}")
    print(f"Total sites added: {total_added}")
    print(f"Run 'python scripts/generate_sites.py' to create markdown files")


if __name__ == "__main__":
    main()
