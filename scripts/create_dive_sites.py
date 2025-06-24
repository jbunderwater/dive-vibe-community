#!/usr/bin/env python3
"""
Script to create dive site markdown files from OSM data using the shared template.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

def sanitize_filename(name):
    """Convert site name to a valid filename."""
    # Remove special characters and replace spaces with hyphens
    sanitized = re.sub(r'[^\w\s-]', '', name.lower())
    sanitized = re.sub(r'[-\s]+', '-', sanitized)
    return sanitized.strip('-')

def determine_site_type(tags):
    """Determine the type of dive site based on OSM tags."""
    if tags.get('historic') == 'wreck' or tags.get('seamark:type') == 'wreck':
        return 'wreck'
    elif tags.get('natural') == 'beach':
        return 'beach'
    else:
        return 'reef'

def determine_entry_type(tags):
    """Determine entry type based on OSM tags."""
    entry = tags.get('scuba_diving:entry')
    if entry == 'shore':
        return 'shore'
    elif entry == 'boat':
        return 'boat'
    else:
        # Default to shore for Bonaire as most sites are shore dives
        return 'shore'

def estimate_difficulty(tags):
    """Estimate difficulty based on available information."""
    # This is a rough estimate - could be improved with more data
    if tags.get('wreck:depth'):
        try:
            depth = int(tags['wreck:depth'].replace('m', ''))
            if depth > 30:
                return 'Advanced'
            elif depth > 18:
                return 'Intermediate'
            else:
                return 'Beginner'
        except:
            pass
    
    # Default to intermediate for most sites
    return 'Intermediate'

def create_dive_site_file(site_data, template_path, output_dir):
    """Create a dive site markdown file from OSM data and template."""
    
    # Read the template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Extract site information
    name = site_data['name']
    lat = site_data['lat']
    lon = site_data['lon']
    tags = site_data['tags']
    
    # Determine site characteristics
    site_type = determine_site_type(tags)
    entry_type = determine_entry_type(tags)
    difficulty = estimate_difficulty(tags)
    
    # Get additional info from tags
    ref = tags.get('ref', '')
    website = tags.get('website', '')
    alt_name = tags.get('alt_name', '')
    note = tags.get('note', '')
    
    # Create filename
    filename = sanitize_filename(name)
    if not filename:
        filename = f"site_{site_data['osm_id']}"
    
    # Fill in the template
    content = template_content.replace('[Site Name]', name)
    content = content.replace('[latitude]', str(lat))
    content = content.replace('[longitude]', str(lon))
    content = content.replace('[Beginner/Intermediate/Advanced]', difficulty)
    content = content.replace('[depth in meters]', tags.get('wreck:depth', '30'))
    content = content.replace('[shore/boat/both]', entry_type)
    content = content.replace('[reef/wreck/beach/other]', site_type)
    content = content.replace('[site reference number if available]', ref)
    content = content.replace('[OpenStreetMap ID]', str(site_data['osm_id']))
    content = content.replace('[contributor username]', 'osm_data')
    
    # Create brief description
    brief_desc = f"A {site_type} dive site"
    if site_type == 'wreck':
        brief_desc += f" featuring the {name}"
        if tags.get('wreck:depth'):
            brief_desc += f" at {tags['wreck:depth']} depth"
    elif site_type == 'reef':
        brief_desc += f" known for its marine life and coral formations"
    elif site_type == 'beach':
        brief_desc += f" with easy shore access"
    
    content = content.replace('[Brief one-sentence description of the dive site]', brief_desc)
    
    # Add specific information based on tags
    overview = f"{name} is a popular dive site on Bonaire"
    if site_type == 'wreck':
        overview += f" featuring the wreck of the {name}"
        if tags.get('wreck:date_sunk'):
            overview += f" which sank in {tags['wreck:date_sunk']}"
        if tags.get('wreck:depth'):
            overview += f". The wreck lies at a depth of {tags['wreck:depth']}"
    else:
        overview += " offering excellent diving opportunities"
    
    if note:
        overview += f". Note: {note}"
    
    content = content.replace('[Detailed description of the dive site, including what makes it special, typical conditions, and what divers can expect to see]', overview)
    
    # Fill in site information
    site_info = f"- **Location**: Bonaire\n"
    site_info += f"- **Entry Type**: {entry_type.title()} entry\n"
    site_info += f"- **Site Type**: {site_type.title()}\n"
    site_info += f"- **Difficulty Level**: {difficulty}\n"
    site_info += f"- **Maximum Depth**: {tags.get('wreck:depth', '30')} meters\n"
    site_info += f"- **Typical Visibility**: 15-30 meters\n"
    site_info += f"- **Current**: Light to Moderate\n"
    site_info += f"- **Best Time**: Morning to early afternoon"
    
    content = content.replace('[Specific area or region on the island]\n- **Entry Type**: [Shore entry, boat entry, or both]\n- **Site Type**: [Reef, wreck, beach, etc.]\n- **Difficulty Level**: [Beginner/Intermediate/Advanced]\n- **Maximum Depth**: [X] meters\n- **Typical Visibility**: [X-X] meters\n- **Current**: [None/Light/Moderate/Strong]\n- **Best Time**: [Time of day or season]', site_info)
    
    # Add marine life section
    marine_life = "Bonaire's waters are teeming with marine life. Expect to see colorful reef fish, sea turtles, and a variety of coral species. The site is known for its healthy coral formations and diverse fish populations."
    if site_type == 'wreck':
        marine_life += " Wrecks often attract larger fish and provide excellent opportunities for photography."
    
    content = content.replace('[Description of typical marine life found at this site, including fish species, coral types, and other notable creatures]', marine_life)
    
    # Add dive profile
    dive_profile = f"Recommended dive profile for {name}: Start at the surface and gradually descend to explore the site. For {site_type} sites, plan for a maximum depth of {tags.get('wreck:depth', '30')} meters with appropriate bottom time based on your certification level."
    
    content = content.replace('[Typical dive profile, including recommended depth ranges, bottom time, and any special considerations]', dive_profile)
    
    # Add entry/exit instructions
    entry_exit = f"For {entry_type} entry at {name}, follow the marked entry points. Ensure you have proper equipment and check local conditions before entering the water. Exit at the same location unless otherwise specified."
    
    content = content.replace('[Detailed instructions for entering and exiting the water, including any landmarks, parking information, or special considerations]', entry_exit)
    
    # Add tips
    tips = [
        "Check local weather and sea conditions before diving",
        "Bring appropriate safety equipment",
        "Respect marine life and coral formations",
        "Plan your dive and dive your plan"
    ]
    
    if site_type == 'wreck':
        tips.append("Exercise caution when exploring wreck interiors")
        tips.append("Maintain proper buoyancy to avoid damaging the wreck")
    
    tips_text = '\n'.join([f"- {tip}" for tip in tips])
    content = content.replace('- [Tip 1]\n- [Tip 2]\n- [Tip 3]\n- [Tip 4]', tips_text)
    
    # Add safety considerations
    safety = "Always dive within your certification limits and experience level. Be aware of boat traffic in the area and maintain proper buoyancy control to protect the marine environment."
    
    content = content.replace('[Any safety notes, hazards, or special considerations for this site]', safety)
    
    # Add photography info
    photography = f"{name} offers excellent photography opportunities. The clear waters and abundant marine life make it ideal for both wide-angle and macro photography. Natural light is best during morning hours."
    
    content = content.replace('[Information about photography opportunities, best angles, lighting conditions, and subject matter]', photography)
    
    # Add nearby sites placeholder
    content = content.replace('[Related or nearby dive sites that divers might want to combine with this one]', 'Check the Bonaire dive site map for nearby locations.')
    
    # Add additional resources
    resources = ""
    if website:
        resources += f"- **Website**: {website}\n"
    if ref:
        resources += f"- **Reference**: Site #{ref}\n"
    resources += f"- **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}"
    
    content = content.replace('- **Website**: [Link to more detailed information if available]\n- **Reference**: [Site reference number or other identifiers]\n- **Last Updated**: [Date of last update]', resources)
    
    # Add footer
    content = content.replace('[username]', 'osm_data')
    content = content.replace('[date]', datetime.now().strftime('%Y-%m-%d'))
    
    # Write the file
    output_path = output_dir / f"{filename}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def update_index_json(sites, output_dir):
    """Update the index.json file with new dive sites."""
    index_path = output_dir / 'index.json'
    
    # Read existing index if it exists
    existing_sites = []
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both array and object formats
            if isinstance(data, list):
                existing_sites = data
            else:
                existing_sites = data.get('sites', [])
    
    # Create new site entries
    new_sites = []
    for site in sites:
        filename = sanitize_filename(site['name'])
        if not filename:
            filename = f"site_{site['osm_id']}"
        
        new_sites.append({
            'name': site['name'],
            'filename': f"{filename}.md",
            'lat': site['lat'],
            'lng': site['lon'],
            'difficulty': estimate_difficulty(site['tags']),
            'maxDepth': int(site['tags'].get('wreck:depth', '30').replace('m', '')),
            'entryType': determine_entry_type(site['tags']),
            'siteType': determine_site_type(site['tags']),
            'ref': site['tags'].get('ref', ''),
            'osmId': site['osm_id']
        })
    
    # Combine existing and new sites, avoiding duplicates
    all_sites = existing_sites.copy()
    existing_names = {site['name'] for site in existing_sites}
    
    for site in new_sites:
        if site['name'] not in existing_names:
            all_sites.append(site)
    
    # Write updated index - use the same format as existing (array)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(all_sites, f, indent=2)
    
    return len(new_sites)

def main():
    """Main function to process OSM data and create dive site files."""
    
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    osm_data_file = project_root / 'dive_sites_bonaire.json'
    template_path = project_root / 'divesites' / '_template.md'
    output_dir = project_root / 'divesites' / 'bonaire'
    
    # Check if files exist
    if not osm_data_file.exists():
        print(f"Error: OSM data file not found: {osm_data_file}")
        return
    
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}")
        return
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read OSM data
    print(f"Reading OSM data from {osm_data_file}")
    with open(osm_data_file, 'r', encoding='utf-8') as f:
        sites_data = json.load(f)
    
    print(f"Found {len(sites_data)} dive sites")
    
    # Process each site
    created_files = []
    for i, site in enumerate(sites_data, 1):
        print(f"Processing {i}/{len(sites_data)}: {site['name']}")
        try:
            filename = create_dive_site_file(site, template_path, output_dir)
            created_files.append(filename)
            print(f"  ✓ Created {filename}.md")
        except Exception as e:
            print(f"  ✗ Error creating file for {site['name']}: {e}")
    
    # Update index.json
    print("\nUpdating index.json...")
    new_sites_count = update_index_json(sites_data, output_dir)
    print(f"✓ Updated index.json with {new_sites_count} new sites")
    
    print(f"\nSummary:")
    print(f"- Processed {len(sites_data)} dive sites")
    print(f"- Created {len(created_files)} markdown files")
    print(f"- Updated index.json")
    print(f"- Output directory: {output_dir}")

if __name__ == "__main__":
    main() 