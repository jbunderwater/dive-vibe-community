#!/usr/bin/env python3
"""
Batch script to collect dive sites for all destinations using OpenStreetMap Overpass API
Uses Google Maps for geocoding and OSM Overpass API for dive site data
Optimized for OSM API (no rate limits on private.coffee instance)

New feature: World collection mode that processes every country in the world
"""

import json
import subprocess
import sys
import time
import os
import argparse
from pathlib import Path
from datetime import datetime

# Comprehensive list of world countries
WORLD_COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
    "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
    "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
    "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Ivory Coast",
    "Jamaica", "Japan", "Jordan",
    "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
    "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
    "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
    "Oman",
    "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
    "Qatar",
    "Romania", 
    "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
    "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
    "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
    "Yemen",
    "Zambia", "Zimbabwe"
]

# Additional important dive destinations to include
ADDITIONAL_DIVE_DESTINATIONS = [
    "Bora Bora", "Raja Ampat", "Galápagos Islands", "Cayman Brac", "Little Cayman", 
    "Fernando de Noronha", "Gili Islands", "Komodo", "Socorro Island", "Cocos Island",
    "Similan Islands", "Tioman Island", "Sipadan Island", "Andaman Islands", 
    "Poor Knights Islands", "Malpelo Island", "Isla Mujeres", "Isla Holbox", 
    "Fakarava", "Taveuni", "Beqa Island", "Moorea", "Ni'ihau", "Nusa Penida",
    "Pulau Weh", "San Andrés", "Lembongan Island", "Perhentian Islands", 
    "La Gomera", "El Hierro", "Isla de la Juventud", "Isla Coiba", 
    "Bazaruto Archipelago", "Apo Island", "Sanganeb Atoll", "Hallaniyat Islands",
    "Roca Partida", "San Benedicto Island", "Clarion Island", "Wolf Island", 
    "Darwin Island", "Misool", "Dampier Strait", "Waigeo", "Salawati", "Batanta",
    "Sangalaki", "Kakaban", "Maratua", "Layang Layang", "Koh Tao", "Koh Bon", 
    "Koh Tachai", "Fuvahmulah", "Hanifaru Bay", "Dhigurah"
]

# Combined list for world collection
WORLD_COUNTRIES_AND_DESTINATIONS = WORLD_COUNTRIES + ADDITIONAL_DIVE_DESTINATIONS

def load_destinations():
    """Load destinations from destinations.json"""
    try:
        with open('destinations.json', 'r', encoding='utf-8') as f:
            destinations = json.load(f)
        return destinations
    except Exception as e:
        print(f"Error loading destinations.json: {e}")
        return []

def run_osm_collection(destination_name, output_dir="."):
    """Run the OSM dive site collection script for a single destination"""
    try:
        # Create output directory if it doesn't exist
        if output_dir != ".":
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Get the path to the osm_dive_sites.py script
        script_dir = Path(__file__).parent
        osm_script = script_dir / 'osm_dive_sites.py'
        
        # Run the osm_dive_sites.py script
        cmd = [sys.executable, str(osm_script), destination_name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=output_dir)
        
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_if_csv_created(destination_name, output_dir="."):
    """Check if a CSV file was created for the destination"""
    csv_filename = f"{destination_name.replace(' ', '_').lower()}_divesites_osm.csv"
    csv_path = Path(output_dir) / csv_filename
    return csv_path.exists()

def process_destinations(destinations, output_dir=".", rate_limit=0.5, force=False):
    """Process a list of destinations with rate limiting"""
    successful = 0
    failed = 0
    skipped = 0
    failed_destinations = []
    start_time = time.time()
    
    print(f"Processing {len(destinations)} destinations...")
    print(f"Rate limit: {1/rate_limit:.1f} requests per second ({rate_limit}s delay between requests)")
    print(f"Force mode: {'ON' if force else 'OFF'}")
    print(f"Estimated time: ~{len(destinations) * rate_limit / 60:.1f} minutes")
    print("=" * 60)
    
    # Process each destination
    for i, destination in enumerate(destinations, 1):
        destination_name = destination if isinstance(destination, str) else destination.get('name', 'Unknown')
        
        # Check if CSV already exists (unless force mode is enabled)
        if not force and check_if_csv_created(destination_name, output_dir):
            progress = f"[{i:2d}/{len(destinations)}]"
            print(f"{progress} Skipping: {destination_name:<30} ⏭️  (CSV exists)")
            skipped += 1
            continue
        
        # Progress indicator
        progress = f"[{i:2d}/{len(destinations)}]"
        print(f"{progress} Processing: {destination_name:<30}", end="", flush=True)
        
        success, error = run_osm_collection(destination_name, output_dir)
        
        if success:
            # Check if CSV was actually created (some destinations might return no results)
            if check_if_csv_created(destination_name, output_dir):
                print(" ✅")
                successful += 1
            else:
                print(" ⚪ (no results)")
                # Don't count as failed, but also don't count as successful
        else:
            print(" ❌")
            failed += 1
            failed_destinations.append((destination_name, error))
        
        # Add delay between requests (OSM has no rate limits, but we're being respectful)
        if i < len(destinations):
            time.sleep(rate_limit)
    
    return successful, failed, skipped, failed_destinations, time.time() - start_time

def main():
    """Main function to process destinations"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Batch OSM dive site collector')
    parser.add_argument('--world', action='store_true', help='Process all world countries and dive destinations')
    parser.add_argument('--force', action='store_true', help='Force processing even if CSV file already exists')
    args = parser.parse_args()
    
    print("🌊 BATCH OSM DIVE SITE COLLECTOR")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check command line arguments
    if args.world:
        # World collection mode
        print("🌍 WORLD COLLECTION MODE")
        print("Processing every country in the world plus additional dive destinations...")
        print(f"Total destinations: {len(WORLD_COUNTRIES_AND_DESTINATIONS)}")
        print(f"Countries: {len(WORLD_COUNTRIES)}")
        print(f"Additional dive destinations: {len(ADDITIONAL_DIVE_DESTINATIONS)}")
        
        # Create world_collection directory
        output_dir = "world_collection_osm"
        Path(output_dir).mkdir(exist_ok=True)
        
        successful, failed, skipped, failed_destinations, elapsed_time = process_destinations(
            WORLD_COUNTRIES_AND_DESTINATIONS, output_dir, rate_limit=0.5, force=args.force
        )
        
        # Print summary
        print(f"\n{'='*60}")
        print("WORLD COLLECTION COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Total destinations processed: {len(WORLD_COUNTRIES_AND_DESTINATIONS)}")
        print(f"⏱️  Elapsed time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
        print(f"🚀 Average: {len(WORLD_COUNTRIES_AND_DESTINATIONS)/elapsed_time:.1f} requests/second")
        
        # List generated CSV files
        csv_files = list(Path(output_dir).glob('*_divesites_osm.csv'))
        if csv_files:
            print(f"\nGenerated CSV files in {output_dir}/ ({len(csv_files)}):")
            total_sites = 0
            for csv_file in sorted(csv_files):
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines()) - 1
                        total_sites += lines
                    print(f"  - {csv_file.name} ({lines} dive sites)")
                except:
                    print(f"  - {csv_file.name}")
            
            print(f"\n📈 Total dive sites collected: {total_sites}")
        
    else:
        # Standard destinations mode
        print("📋 STANDARD DESTINATIONS MODE")
        
        # Load destinations
        destinations = load_destinations()
        if not destinations:
            print("No destinations found. Exiting.")
            sys.exit(1)
        
        successful, failed, skipped, failed_destinations, elapsed_time = process_destinations(
            destinations, rate_limit=0.5, force=args.force
        )
        
        # Print summary
        print(f"\n{'='*60}")
        print("BATCH PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Total: {len(destinations)}")
        print(f"⏱️  Elapsed time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
        print(f"🚀 Average: {len(destinations)/elapsed_time:.1f} requests/second")
        
        # List generated CSV files
        csv_files = list(Path('.').glob('*_divesites_osm.csv'))
        if csv_files:
            print(f"\nGenerated CSV files ({len(csv_files)}):")
            total_sites = 0
            for csv_file in sorted(csv_files):
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines()) - 1
                        total_sites += lines
                    print(f"  - {csv_file.name} ({lines} dive sites)")
                except:
                    print(f"  - {csv_file.name}")
            
            print(f"\n📈 Total dive sites collected: {total_sites}")
    
    # Print failed destinations if any
    if failed_destinations:
        print(f"\n❌ Failed destinations ({len(failed_destinations)}):")
        for destination, error in failed_destinations:
            print(f"  - {destination}: {error}")

if __name__ == "__main__":
    main() 