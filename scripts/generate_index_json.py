#!/usr/bin/env python3
"""
Script to generate index.json files for dive site directories.

This script scans a directory containing markdown files with dive site information
and generates an index.json file with metadata extracted from the frontmatter.

Usage:
    python generate_index_json.py [directory_path]

If no directory path is provided, the script will use the current directory.
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def extract_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """
    Extract YAML frontmatter from markdown content.
    
    Args:
        content: The markdown file content
        
    Returns:
        Dictionary containing the frontmatter data, or None if no frontmatter found
    """
    # Match YAML frontmatter between --- markers
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    
    if not frontmatter_match:
        return None
    
    try:
        frontmatter_content = frontmatter_match.group(1)
        return yaml.safe_load(frontmatter_content)
    except yaml.YAMLError as e:
        print(f"Warning: Could not parse YAML frontmatter: {e}")
        return None


def extract_name_from_content(content: str, filename: str) -> str:
    """
    Extract dive site name from markdown content if not in frontmatter.
    
    Args:
        content: The markdown file content
        filename: The filename (used as fallback)
        
    Returns:
        The dive site name
    """
    # Look for the first heading (# Name)
    heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()
    
    # Fallback to filename without extension
    return Path(filename).stem.replace('-', ' ').title()


def process_markdown_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Process a single markdown file and extract dive site metadata.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Dictionary containing dive site metadata, or None if processing failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter
        frontmatter = extract_frontmatter(content)
        
        if not frontmatter:
            print(f"Warning: No frontmatter found in {file_path.name}")
            return None
        
        # Ensure required fields are present
        if 'name' not in frontmatter:
            frontmatter['name'] = extract_name_from_content(content, file_path.name)
        
        # Add filename
        frontmatter['filename'] = file_path.name
        
        # Convert difficulty to proper case if present
        if 'difficulty' in frontmatter:
            difficulty = str(frontmatter['difficulty']).lower()
            if difficulty in ['beginner', 'intermediate', 'advanced']:
                frontmatter['difficulty'] = difficulty.title()
        
        # Ensure numeric fields are properly typed
        for field in ['lat', 'lng', 'maxDepth', 'osmId']:
            if field in frontmatter:
                try:
                    value = str(frontmatter[field]).strip()
                    # Handle "30m" format for maxDepth
                    if field == 'maxDepth' and value.endswith('m'):
                        value = value[:-1]
                    frontmatter[field] = float(value) if field in ['lat', 'lng'] else int(value)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid {field} value in {file_path.name}: {frontmatter[field]}")
                    if field in ['lat', 'lng']:
                        frontmatter[field] = 0.0
                    else:
                        frontmatter[field] = 0
        
        # Set default values for missing required fields
        if 'lat' not in frontmatter:
            frontmatter['lat'] = 0.0
        if 'lng' not in frontmatter:
            frontmatter['lng'] = 0.0
        if 'difficulty' not in frontmatter:
            frontmatter['difficulty'] = 'Intermediate'
        if 'maxDepth' not in frontmatter:
            frontmatter['maxDepth'] = 30
        if 'entryType' not in frontmatter:
            frontmatter['entryType'] = 'shore'
        if 'siteType' not in frontmatter:
            frontmatter['siteType'] = 'reef'
        if 'ref' not in frontmatter:
            frontmatter['ref'] = ''
        if 'osmId' not in frontmatter:
            frontmatter['osmId'] = 0
        if 'addedBy' not in frontmatter:
            frontmatter['addedBy'] = 'unknown'
        
        return frontmatter
        
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return None


def generate_index_json(directory_path: str) -> None:
    """
    Generate index.json file for a dive site directory.
    
    Args:
        directory_path: Path to the directory containing markdown files
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Error: Directory {directory_path} does not exist")
        return
    
    if not directory.is_dir():
        print(f"Error: {directory_path} is not a directory")
        return
    
    # Find all markdown files (excluding overview.md, index.md, and _template.md)
    markdown_files = []
    for file_path in directory.glob("*.md"):
        if file_path.name not in ['overview.md', 'index.md', '_template.md']:
            markdown_files.append(file_path)
    
    if not markdown_files:
        print(f"No markdown files found in {directory_path}")
        return
    
    print(f"Found {len(markdown_files)} markdown files in {directory_path}")
    
    # Process each markdown file
    dive_sites = []
    for file_path in sorted(markdown_files):
        print(f"Processing {file_path.name}...")
        dive_site_data = process_markdown_file(file_path)
        # Only include if 'name' is a string
        if dive_site_data and isinstance(dive_site_data.get('name', None), str):
            dive_sites.append(dive_site_data)
    
    if not dive_sites:
        print("No valid dive site data found")
        return
    
    # Sort dive sites by name
    dive_sites.sort(key=lambda x: x['name'].lower())
    
    # Write index.json
    index_path = directory / "index.json"
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(dive_sites, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully generated {index_path} with {len(dive_sites)} dive sites")
        
        # Print summary
        print("\nSummary:")
        print(f"Total dive sites: {len(dive_sites)}")
        
        # Count by difficulty
        difficulties = {}
        for site in dive_sites:
            diff = site.get('difficulty', 'Unknown')
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        print("By difficulty:")
        for diff, count in sorted(difficulties.items()):
            print(f"  {diff}: {count}")
        
        # Count sites with coordinates
        sites_with_coords = sum(1 for site in dive_sites if site.get('lat', 0) != 0 and site.get('lng', 0) != 0)
        print(f"Sites with coordinates: {sites_with_coords}/{len(dive_sites)}")
        
    except Exception as e:
        print(f"Error writing index.json: {e}")


def main():
    """Main function to handle command line arguments and execute the script."""
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = "."
    
    print(f"Generating index.json for directory: {directory_path}")
    generate_index_json(directory_path)


if __name__ == "__main__":
    main() 