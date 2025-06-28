#!/usr/bin/env python3
"""
Script to gather dive sites for all destinations in destinations.json
"""

import json
import subprocess
import sys
import time
import os

def load_destinations():
    """Load destinations from destinations.json"""
    try:
        with open('../destinations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: destinations.json not found. Make sure you're running from the scripts directory.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing destinations.json: {e}")
        sys.exit(1)

def run_gather_script(destination_name):
    """Run the gather_dive_sites.py script for a single destination"""
    print(f"\n{'='*60}")
    print(f"Processing: {destination_name}")
    print(f"{'='*60}")
    
    try:
        # Run the gather_dive_sites.py script with the destination name
        result = subprocess.run([
            sys.executable, 'gather_dive_sites.py', destination_name
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"✅ Successfully processed {destination_name}")
            print(result.stdout)
        else:
            print(f"❌ Failed to process {destination_name}")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Exception while processing {destination_name}: {e}")

def main():
    print("Starting dive site gathering for all destinations...")
    
    # Load destinations
    destinations = load_destinations()
    print(f"Found {len(destinations)} destinations to process")
    
    # Filter out Bonaire since we already have dive site data
    destinations_to_process = [d for d in destinations if d['name'] != 'Bonaire']
    print(f"Skipping Bonaire (already has dive site data)")
    print(f"Processing {len(destinations_to_process)} destinations")
    
    # Process each destination
    for i, destination in enumerate(destinations_to_process, 1):
        destination_name = destination['name']
        print(f"\n[{i}/{len(destinations_to_process)}] Processing {destination_name}")
        
        run_gather_script(destination_name)
        
        # Add a small delay between requests to be respectful to the APIs
        if i < len(destinations_to_process):
            print("Waiting 2 seconds before next destination...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print("✅ Completed processing all destinations!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 