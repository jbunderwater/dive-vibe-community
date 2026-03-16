#!/usr/bin/env python3
"""
Script to update markdown frontmatter coordinates with coordinates from index.json
"""

import json
import re
import os
from pathlib import Path

def load_index_data(index_path):
    """Load data from index.json"""
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading index.json: {e}")
        return []

def update_markdown_coordinates():
    """Update markdown frontmatter coordinates with index.json coordinates"""
    index_path = "index.json"
    index_data = load_index_data(index_path)
    
    if not index_data:
        return
    
    # Create a mapping of filename to index data
    index_map = {}
    for site in index_data:
        if 'filename' in site:
            index_map[site['filename']] = site
    
    updated_files = []
    skipped_files = []
    error_files = []
    
    print("🌊 UPDATING MARKDOWN COORDINATES")
    print("=" * 60)
    
    # Process each markdown file
    for filename in os.listdir('.'):
        if filename.endswith('.md') and filename in index_map:
            index_site = index_map[filename]
            index_lat = index_site.get('lat')
            index_lng = index_site.get('lng')
            
            if index_lat is None or index_lng is None:
                skipped_files.append((filename, "No coordinates in index.json"))
                continue
            
            try:
                # Read markdown file
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file has frontmatter
                if not content.startswith('---'):
                    skipped_files.append((filename, "No frontmatter found"))
                    continue
                
                # Split content by frontmatter delimiters
                parts = content.split('---')
                if len(parts) < 3:
                    skipped_files.append((filename, "Invalid frontmatter format"))
                    continue
                
                # Extract frontmatter
                frontmatter_text = parts[1].strip()
                
                # Check if lat/lng already exist in frontmatter
                current_lat_match = re.search(r'lat:\s*([0-9.-]+)', frontmatter_text)
                current_lng_match = re.search(r'lng:\s*([0-9.-]+)', frontmatter_text)
                
                if current_lat_match and current_lng_match:
                    current_lat = float(current_lat_match.group(1))
                    current_lng = float(current_lng_match.group(1))
                    
                    # Check if coordinates are different
                    if abs(current_lat - index_lat) < 0.0001 and abs(current_lng - index_lng) < 0.0001:
                        skipped_files.append((filename, "Coordinates already match"))
                        continue
                
                # Update coordinates in frontmatter
                # Replace existing lat/lng or add new ones
                updated_frontmatter = frontmatter_text
                
                # Remove existing lat/lng lines
                updated_frontmatter = re.sub(r'lat:\s*[0-9.-]+\s*\n?', '', updated_frontmatter)
                updated_frontmatter = re.sub(r'lng:\s*[0-9.-]+\s*\n?', '', updated_frontmatter)
                
                # Add new coordinates (add before the closing ---)
                # Find the last line before the closing ---
                lines = updated_frontmatter.split('\n')
                insert_index = len(lines) - 1
                
                # Insert lat/lng before the last line
                lines.insert(insert_index, f"lat: {index_lat}")
                lines.insert(insert_index + 1, f"lng: {index_lng}")
                
                updated_frontmatter = '\n'.join(lines)
                
                # Reconstruct the file content
                parts[1] = updated_frontmatter
                new_content = '---\n' + parts[1] + '\n---' + ''.join(parts[2:])
                
                # Write updated content back to file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated_files.append(filename)
                print(f"✅ Updated {filename}: {index_lat}, {index_lng}")
                
            except Exception as e:
                error_files.append((filename, str(e)))
                print(f"❌ Error updating {filename}: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("UPDATE SUMMARY")
    print("=" * 60)
    print(f"✅ Files updated: {len(updated_files)}")
    print(f"⏭️  Files skipped: {len(skipped_files)}")
    print(f"❌ Files with errors: {len(error_files)}")
    print(f"📊 Total files processed: {len(index_map)}")
    
    if updated_files:
        print(f"\n📝 Updated files:")
        for filename in sorted(updated_files):
            print(f"  - {filename}")
    
    if skipped_files:
        print(f"\n⏭️  Skipped files:")
        for filename, reason in sorted(skipped_files):
            print(f"  - {filename}: {reason}")
    
    if error_files:
        print(f"\n❌ Files with errors:")
        for filename, error in sorted(error_files):
            print(f"  - {filename}: {error}")

if __name__ == "__main__":
    update_markdown_coordinates() 