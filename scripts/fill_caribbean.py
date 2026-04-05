#!/usr/bin/env python3
"""Populate dive site data for new Caribbean destinations."""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_DIR = PROJECT_ROOT / "data" / "osm_clean"
DESTINATIONS_FILE = PROJECT_ROOT / "destinations.json"

CURATED_SITES = {
    "grenada": [
        {"name": "Bianca C", "lat": 12.040, "lon": -61.750, "depth": 50, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Underwater Sculpture Park", "lat": 12.060, "lon": -61.740, "depth": 8, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Flamingo Bay", "lat": 12.050, "lon": -61.760, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Boss Reef", "lat": 12.080, "lon": -61.730, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Dragon Bay", "lat": 12.010, "lon": -61.740, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Purple Rain", "lat": 12.070, "lon": -61.720, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Veronica L Wreck", "lat": 12.045, "lon": -61.755, "depth": 15, "site_type": "wreck", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Shakem Wreck", "lat": 12.055, "lon": -61.745, "depth": 28, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Northern Exposure", "lat": 12.200, "lon": -61.620, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Spice Island Reef", "lat": 12.030, "lon": -61.770, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Valley of Whales", "lat": 12.020, "lon": -61.735, "depth": 32, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Happy Hill", "lat": 12.065, "lon": -61.735, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "dominica": [
        {"name": "Champagne Reef", "lat": 15.235, "lon": -61.370, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Scotts Head Pinnacle", "lat": 15.215, "lon": -61.365, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Soufrière Pinnacle", "lat": 15.225, "lon": -61.360, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Danglebens Pinnacles", "lat": 15.240, "lon": -61.380, "depth": 35, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Coral Gardens", "lat": 15.250, "lon": -61.375, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "L'Abym", "lat": 15.260, "lon": -61.385, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Toucari Bay", "lat": 15.625, "lon": -61.475, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Cabrits Drop", "lat": 15.580, "lon": -61.470, "depth": 32, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Point Guignard", "lat": 15.280, "lon": -61.390, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Nose Reef", "lat": 15.210, "lon": -61.358, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Five Finger Rock", "lat": 15.550, "lon": -61.460, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Rodney's Rock", "lat": 15.270, "lon": -61.378, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "st-lucia": [
        {"name": "Superman's Flight", "lat": 13.860, "lon": -61.070, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Anse Chastanet Reef", "lat": 13.862, "lon": -61.072, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Pinnacles (Anse Cochon)", "lat": 13.920, "lon": -61.060, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Key Hole Pinnacles", "lat": 13.855, "lon": -61.065, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Turtle Reef", "lat": 13.870, "lon": -61.075, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Lesleen M Wreck", "lat": 13.910, "lon": -61.055, "depth": 20, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Jalousie Beach Reef", "lat": 13.840, "lon": -61.060, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Anse La Raye Wall", "lat": 13.940, "lon": -61.050, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Daini Koyomaru Wreck", "lat": 14.050, "lon": -61.010, "depth": 18, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Coral Gardens Soufrière", "lat": 13.848, "lon": -61.068, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "The Drift (Pitons)", "lat": 13.835, "lon": -61.058, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Grand Caille", "lat": 13.950, "lon": -61.045, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "us-virgin-islands": [
        {"name": "Buck Island Reef", "lat": 17.790, "lon": -64.620, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Cane Bay Wall", "lat": 17.770, "lon": -64.810, "depth": 40, "site_type": "wall", "entry_type": "shore", "difficulty": "Advanced"},
        {"name": "Frederiksted Pier", "lat": 17.715, "lon": -64.882, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "WIT Shoal II Wreck", "lat": 18.320, "lon": -64.940, "depth": 26, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cow and Calf", "lat": 18.310, "lon": -64.880, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Cartanser Sr Wreck", "lat": 18.315, "lon": -64.935, "depth": 20, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Salt River Canyon", "lat": 17.780, "lon": -64.760, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Grain Wreck (Suffolk Maid)", "lat": 18.340, "lon": -64.960, "depth": 18, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Coral World", "lat": 18.350, "lon": -64.860, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "The Pinnacle (St. Croix)", "lat": 17.760, "lon": -64.830, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "French Cap Cay", "lat": 18.265, "lon": -64.690, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Sapphire Beach Reef", "lat": 18.335, "lon": -64.850, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
    ],
    "tobago": [
        {"name": "Japanese Gardens", "lat": 11.290, "lon": -60.500, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Kelleston Drain", "lat": 11.280, "lon": -60.490, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cathedral", "lat": 11.295, "lon": -60.505, "depth": 22, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "London Bridge", "lat": 11.300, "lon": -60.510, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Maverick Wreck", "lat": 11.180, "lon": -60.740, "depth": 30, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Diver's Dream", "lat": 11.285, "lon": -60.495, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Bookends", "lat": 11.305, "lon": -60.515, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Angel Reef", "lat": 11.270, "lon": -60.485, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Flying Reef", "lat": 11.310, "lon": -60.520, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Arnos Vale", "lat": 11.210, "lon": -60.790, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Mt Irvine Wall", "lat": 11.200, "lon": -60.800, "depth": 20, "site_type": "wall", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Sisters Rocks", "lat": 11.275, "lon": -60.488, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "aruba": [
        {"name": "SS Antilla Wreck", "lat": 12.600, "lon": -70.045, "depth": 18, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Mangel Halto Reef", "lat": 12.460, "lon": -69.960, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Boca Catalina", "lat": 12.580, "lon": -70.050, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Arashi Reef", "lat": 12.610, "lon": -70.060, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Pedernales Wreck", "lat": 12.590, "lon": -70.055, "depth": 10, "site_type": "wreck", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Jane Sea Wreck", "lat": 12.540, "lon": -70.020, "depth": 25, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Skalahein Reef", "lat": 12.445, "lon": -69.940, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Malmok Reef", "lat": 12.570, "lon": -70.048, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Sonesta Plane Wreck", "lat": 12.560, "lon": -70.030, "depth": 8, "site_type": "wreck", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Kantil Reef", "lat": 12.450, "lon": -69.950, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Mike's Reef", "lat": 12.550, "lon": -70.035, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "De Palm Slope", "lat": 12.470, "lon": -69.970, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "guadeloupe": [
        {"name": "Cousteau Reserve - Pigeon Island", "lat": 16.168, "lon": -61.790, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Aquarium", "lat": 16.170, "lon": -61.785, "depth": 8, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Jardin de Corail", "lat": 16.165, "lon": -61.792, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Piscine", "lat": 16.172, "lon": -61.788, "depth": 6, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Les Sources d'Eau Chaude", "lat": 16.160, "lon": -61.795, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Pointe Malendure", "lat": 16.175, "lon": -61.780, "depth": 18, "site_type": "reef", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "La Caye", "lat": 16.155, "lon": -61.798, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Augustin Fresnel Wreck", "lat": 16.250, "lon": -61.530, "depth": 28, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Pointe à Lézard", "lat": 16.180, "lon": -61.775, "depth": 22, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Sec Pâté", "lat": 16.150, "lon": -61.800, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Anse Caraïbe", "lat": 16.190, "lon": -61.770, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Les Saintes - Pain de Sucre", "lat": 15.870, "lon": -61.620, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "barbados": [
        {"name": "Stavronikita Wreck", "lat": 13.095, "lon": -59.620, "depth": 40, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Carlisle Bay - Berwyn", "lat": 13.085, "lon": -59.625, "depth": 8, "site_type": "wreck", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Carlisle Bay - Ce-Trek", "lat": 13.088, "lon": -59.622, "depth": 12, "site_type": "wreck", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Carlisle Bay - Eilon", "lat": 13.090, "lon": -59.618, "depth": 10, "site_type": "wreck", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Pamir Wreck", "lat": 13.100, "lon": -59.615, "depth": 14, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Friars Craig Wreck", "lat": 13.082, "lon": -59.628, "depth": 18, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Bright Ledge", "lat": 13.160, "lon": -59.600, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Dottin's Reef", "lat": 13.170, "lon": -59.590, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Folkestone Marine Park", "lat": 13.190, "lon": -59.640, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Bell Buoy Reef", "lat": 13.110, "lon": -59.610, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Shark Bank Barbados", "lat": 13.150, "lon": -59.605, "depth": 30, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Coconut Court Reef", "lat": 13.070, "lon": -59.580, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
    ],
    "sint-eustatius": [
        {"name": "Charles L. Brown Wreck", "lat": 17.490, "lon": -62.990, "depth": 20, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Anchor Point South", "lat": 17.475, "lon": -62.975, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Blue Bead Hole", "lat": 17.480, "lon": -62.980, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Stenapa Reef", "lat": 17.485, "lon": -62.985, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Hangover", "lat": 17.500, "lon": -62.995, "depth": 28, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Crooks Castle", "lat": 17.470, "lon": -62.970, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Double Wreck", "lat": 17.495, "lon": -62.992, "depth": 16, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Nursing Station", "lat": 17.465, "lon": -62.968, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Five Fingers South", "lat": 17.460, "lon": -62.965, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "The Ledges", "lat": 17.505, "lon": -63.000, "depth": 20, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "dominican-republic": [
        {"name": "Catalina Wall", "lat": 18.220, "lon": -68.950, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "St. George Wreck", "lat": 18.470, "lon": -69.880, "depth": 22, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "La Caleta Underwater Park", "lat": 18.430, "lon": -69.750, "depth": 18, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Silver Bank", "lat": 20.800, "lon": -69.000, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Padre Nuestro", "lat": 18.380, "lon": -68.830, "depth": 10, "site_type": "cave", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Bayahibe Reef", "lat": 18.360, "lon": -68.850, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Saona Island", "lat": 18.150, "lon": -68.720, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Punta Cana Reef", "lat": 18.520, "lon": -68.370, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Las Terrenas Drop-Off", "lat": 19.320, "lon": -69.530, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Sosua Bay", "lat": 19.760, "lon": -70.510, "depth": 16, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "El Dudú Cenote", "lat": 19.690, "lon": -69.880, "depth": 25, "site_type": "cave", "entry_type": "shore", "difficulty": "Intermediate"},
        {"name": "Atlantic Princess Wreck", "lat": 18.450, "lon": -69.860, "depth": 28, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
    ],
    "puerto-rico": [
        {"name": "Desecheo Island Wall", "lat": 18.383, "lon": -67.480, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Mona Island", "lat": 18.085, "lon": -67.890, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "La Parguera Wall", "lat": 17.960, "lon": -67.050, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Crash Boat Beach", "lat": 18.490, "lon": -67.160, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Steps (Tres Palmas)", "lat": 18.350, "lon": -67.270, "depth": 15, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Blue Beach", "lat": 18.060, "lon": -65.290, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Culebra Reef", "lat": 18.300, "lon": -65.300, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Caja de Muertos", "lat": 17.890, "lon": -66.520, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Escambrón Reef", "lat": 18.470, "lon": -66.080, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Humacao Reef", "lat": 18.140, "lon": -65.780, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "El Natural Wreck", "lat": 18.400, "lon": -67.200, "depth": 28, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Mosquito Pier", "lat": 18.060, "lon": -65.310, "depth": 14, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
    ],
    "antigua-and-barbuda": [
        {"name": "Pillars of Hercules", "lat": 17.010, "lon": -61.760, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Cades Reef", "lat": 17.030, "lon": -61.870, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Andes Wreck", "lat": 17.040, "lon": -61.780, "depth": 20, "site_type": "wreck", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Sunken Rock", "lat": 17.020, "lon": -61.770, "depth": 28, "site_type": "reef", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Deep Bay Wreck (Andes)", "lat": 17.140, "lon": -61.870, "depth": 10, "site_type": "wreck", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Sandy Island Reef", "lat": 17.160, "lon": -61.880, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Ariadne Shoal", "lat": 17.050, "lon": -61.790, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Great Bird Island", "lat": 17.170, "lon": -61.700, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Barbuda Reef", "lat": 17.620, "lon": -61.750, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Carpenter's Reef", "lat": 17.035, "lon": -61.865, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "st-vincent-grenadines": [
        {"name": "Tobago Cays", "lat": 12.625, "lon": -61.350, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "The Wall (Bequia)", "lat": 13.010, "lon": -61.240, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Anchor Reef", "lat": 13.150, "lon": -61.200, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Bottle Reef", "lat": 13.160, "lon": -61.210, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "New Guinea Reef", "lat": 13.175, "lon": -61.190, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Critter Corner", "lat": 13.170, "lon": -61.195, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Mayreau Gardens", "lat": 12.640, "lon": -61.390, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Petit St. Vincent Reef", "lat": 12.540, "lon": -61.380, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Mustique Reef", "lat": 12.885, "lon": -61.180, "depth": 25, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Bat Cave (St. Vincent)", "lat": 13.200, "lon": -61.220, "depth": 15, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
    ],
    "jamaica": [
        {"name": "Widowmaker's Cave", "lat": 18.360, "lon": -78.360, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "The Throne Room", "lat": 18.365, "lon": -78.355, "depth": 25, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Montego Bay Marine Park", "lat": 18.480, "lon": -77.930, "depth": 15, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "The Point (Negril)", "lat": 18.340, "lon": -78.370, "depth": 30, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Airport Reef", "lat": 18.500, "lon": -77.910, "depth": 12, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Shallow Plane Wreck", "lat": 18.370, "lon": -78.350, "depth": 10, "site_type": "wreck", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Arches (Negril)", "lat": 18.350, "lon": -78.365, "depth": 18, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Port Royal Reef", "lat": 17.940, "lon": -76.840, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Ocho Rios Reef", "lat": 18.410, "lon": -77.100, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Runaway Bay Wall", "lat": 18.470, "lon": -77.330, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Cayman Trench Edge", "lat": 18.355, "lon": -78.360, "depth": 40, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "The Coral Gardens", "lat": 18.490, "lon": -77.920, "depth": 8, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "st-kitts-and-nevis": [
        {"name": "MV River Taw Wreck", "lat": 17.290, "lon": -62.720, "depth": 15, "site_type": "wreck", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Monkey Shoals", "lat": 17.300, "lon": -62.730, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Brassball Wreck", "lat": 17.310, "lon": -62.740, "depth": 12, "site_type": "wreck", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Coral Garden", "lat": 17.280, "lon": -62.710, "depth": 10, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Grid Iron", "lat": 17.320, "lon": -62.750, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Sandy Point Reef", "lat": 17.340, "lon": -62.840, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Nag's Head", "lat": 17.270, "lon": -62.700, "depth": 25, "site_type": "wall", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Coconut Tree Reef", "lat": 17.360, "lon": -62.790, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Devil's Caves", "lat": 17.130, "lon": -62.600, "depth": 20, "site_type": "cave", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Booby Shoals", "lat": 17.160, "lon": -62.620, "depth": 16, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
    ],
    "martinique": [
        {"name": "Diamond Rock", "lat": 14.445, "lon": -61.040, "depth": 35, "site_type": "wall", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Rocher du Diamant Cave", "lat": 14.447, "lon": -61.038, "depth": 25, "site_type": "cave", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Anse Dufour", "lat": 14.525, "lon": -61.085, "depth": 12, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "St. Pierre Wrecks", "lat": 14.740, "lon": -61.180, "depth": 30, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Rocher de la Perle", "lat": 14.770, "lon": -61.210, "depth": 20, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Anse Noire", "lat": 14.530, "lon": -61.088, "depth": 8, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Cap Enragé", "lat": 14.440, "lon": -61.030, "depth": 22, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Pointe Burgos", "lat": 14.550, "lon": -61.090, "depth": 18, "site_type": "reef", "entry_type": "boat", "difficulty": "Intermediate"},
        {"name": "Nahoon Wreck", "lat": 14.735, "lon": -61.175, "depth": 28, "site_type": "wreck", "entry_type": "boat", "difficulty": "Advanced"},
        {"name": "Grande Anse Reef", "lat": 14.460, "lon": -61.050, "depth": 14, "site_type": "reef", "entry_type": "boat", "difficulty": "Beginner"},
        {"name": "Citadelle", "lat": 14.745, "lon": -61.185, "depth": 16, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
        {"name": "Jardin Tropical", "lat": 14.520, "lon": -61.080, "depth": 10, "site_type": "reef", "entry_type": "shore", "difficulty": "Beginner"},
    ],
}


def load_destinations():
    with open(DESTINATIONS_FILE) as f:
        return {d["slug"]: d for d in json.load(f) if not d.get("isGroup")}


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
            "tags": {"source": "curated", "addedBy": "fill_caribbean"},
        })
        existing_names.add(site["name"].lower().strip())
        added += 1

    import os
    os.makedirs(clean_path.parent, exist_ok=True)
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return added, skipped_bounds, skipped_dupe


def main():
    destinations = load_destinations()

    print(f"{'='*60}")
    print("POPULATE CARIBBEAN DESTINATIONS")
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
