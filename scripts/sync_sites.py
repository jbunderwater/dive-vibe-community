#!/usr/bin/env python3
"""
Sync dive site data from osm_clean JSON to divesites/ markdown files and index.json.

Propagates changes to siteType, difficulty, maxDepth, entryType from the
osm_clean source-of-truth to the generated markdown frontmatter, body
"Site Information" section, and index.json — without regenerating full content.

Also removes markdown files and index entries for sites that no longer exist
in osm_clean (e.g., removed hulks, commercial entries).

Usage:
    python3 scripts/sync_sites.py                    # sync all destinations
    python3 scripts/sync_sites.py bonaire red-sea    # sync specific slugs
"""

import json
import os
import re
import sys
from pathlib import Path


# Map site_type codes to display names used in markdown body
SITE_TYPE_DISPLAY = {
    "reef": "Reef",
    "wall": "Wall dive",
    "wreck": "Wreck dive",
    "cave": "Cave/cavern",
    "muck": "Muck dive",
    "beach": "Beach dive",
    "drift": "Drift dive",
    "pinnacle": "Pinnacle/seamount",
}

ENTRY_TYPE_DISPLAY = {
    "shore": "Shore entry",
    "boat": "Boat dive",
    "both": "Shore or boat entry",
}


def sanitize_filename(name):
    """Convert site name to kebab-case filename (matching generate_sites.py)."""
    name = name.strip()
    # Keep unicode letters but convert to lowercase
    name = name.lower()
    # Replace spaces and special chars with hyphens
    name = re.sub(r'[^\w\s-]', '', name, flags=re.UNICODE)
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')
    return name


def update_frontmatter(content, field, new_value):
    """Update a single YAML frontmatter field in markdown content."""
    # Match the field line between --- delimiters
    pattern = rf'^({re.escape(field)}:\s*)(.+)$'
    lines = content.split('\n')
    in_frontmatter = False
    updated = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break  # end of frontmatter
        if in_frontmatter:
            m = re.match(pattern, line)
            if m:
                lines[i] = f"{field}: {new_value}"
                updated = True
                break

    if updated:
        return '\n'.join(lines)
    return content


def update_site_info_line(content, label, new_value):
    """Update a line in the '## Site Information' section."""
    # Match: - **Label**: old value
    pattern = rf'(- \*\*{re.escape(label)}\*\*:\s*)(.+)'
    return re.sub(pattern, rf'\g<1>{new_value}', content)


def sync_markdown_file(md_path, site_type, difficulty, depth, entry_type):
    """Update a single markdown file's frontmatter and body to match source data."""
    if not md_path.exists():
        return False

    content = md_path.read_text(encoding='utf-8')
    original = content

    # Update frontmatter
    content = update_frontmatter(content, 'siteType', site_type)
    content = update_frontmatter(content, 'difficulty', difficulty)
    if depth:
        content = update_frontmatter(content, 'maxDepth', depth)
    if entry_type:
        content = update_frontmatter(content, 'entryType', entry_type)

    # Update Site Information section in body
    type_display = SITE_TYPE_DISPLAY.get(site_type, site_type.capitalize())
    content = update_site_info_line(content, 'Site Type', type_display)
    content = update_site_info_line(content, 'Difficulty Level', difficulty)
    if depth:
        content = update_site_info_line(content, 'Maximum Depth', f'{depth} meters')

    entry_display = ENTRY_TYPE_DISPLAY.get(entry_type, entry_type or 'Shore entry')
    content = update_site_info_line(content, 'Entry Type', entry_display)

    if content != original:
        md_path.write_text(content, encoding='utf-8')
        return True
    return False


def sync_destination(slug, project_root):
    """Sync a single destination's markdown files and index.json from osm_clean data."""
    osm_path = project_root / 'data' / 'osm_clean' / f'{slug}.json'
    divesites_dir = project_root / 'divesites' / slug

    if not osm_path.exists():
        return 0, 0, 0

    with open(osm_path, 'r', encoding='utf-8') as f:
        osm_data = json.load(f)

    if not divesites_dir.exists():
        return 0, 0, 0

    # Build lookup from osm_clean: filename -> site data
    osm_by_filename = {}
    for site in osm_data:
        fn = sanitize_filename(site['name'])
        if fn and fn not in osm_by_filename:
            osm_by_filename[fn] = site

    # Load existing index.json
    index_path = divesites_dir / 'index.json'
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    else:
        index_data = []

    # Build index lookup by filename
    index_by_filename = {}
    for entry in index_data:
        fn = entry.get('filename', '').replace('.md', '')
        index_by_filename[fn] = entry

    updated_md = 0
    removed = 0

    # Find markdown files that no longer have a corresponding osm_clean entry
    existing_md_files = set()
    for md_file in divesites_dir.glob('*.md'):
        if md_file.name in ('overview.md', '_template.md'):
            continue
        fn = md_file.stem
        existing_md_files.add(fn)
        if fn not in osm_by_filename:
            md_file.unlink()
            removed += 1

    # Update markdown files that exist
    for fn, site in osm_by_filename.items():
        md_path = divesites_dir / f'{fn}.md'
        site_type = site.get('site_type') or 'reef'
        difficulty = site.get('difficulty') or 'Intermediate'
        depth = site.get('depth')
        entry_type = site.get('entry_type')

        if sync_markdown_file(md_path, site_type, difficulty, depth, entry_type):
            updated_md += 1

    # Rebuild index.json from osm_clean data
    new_index = []
    seen = set()
    for site in osm_data:
        fn = sanitize_filename(site['name'])
        if not fn or fn in seen:
            continue
        seen.add(fn)

        # Preserve existing index entry fields, update from osm_clean
        existing = index_by_filename.get(fn, {})
        entry = {
            'name': site['name'],
            'filename': f'{fn}.md',
            'lat': site['lat'],
            'lng': site['lon'],
            'difficulty': site.get('difficulty') or 'Intermediate',
            'maxDepth': site.get('depth') or existing.get('maxDepth', 25),
            'entryType': site.get('entry_type') or existing.get('entryType', 'shore'),
            'siteType': site.get('site_type') or 'reef',
            'ref': site.get('tags', {}).get('ref', existing.get('ref', '')),
            'osmId': site.get('osm_id') or existing.get('osmId'),
        }
        new_index.append(entry)

    # Write updated index.json
    index_changed = json.dumps(new_index, indent=2, ensure_ascii=False) != json.dumps(index_data, indent=2, ensure_ascii=False)
    if index_changed:
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(new_index, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return updated_md, removed, 1 if index_changed else 0


def main():
    project_root = Path(__file__).parent.parent

    # Determine which slugs to process
    if len(sys.argv) > 1:
        slugs = sys.argv[1:]
    else:
        osm_dir = project_root / 'data' / 'osm_clean'
        slugs = sorted(
            f.stem for f in osm_dir.glob('*.json')
            if f.stem != '_summary'
        )

    total_updated = 0
    total_removed = 0
    total_index = 0

    for slug in slugs:
        updated, removed, idx = sync_destination(slug, project_root)
        if updated or removed or idx:
            parts = []
            if updated:
                parts.append(f'{updated} md updated')
            if removed:
                parts.append(f'{removed} md removed')
            if idx:
                parts.append('index.json updated')
            print(f'  {slug:40s} {", ".join(parts)}')
        total_updated += updated
        total_removed += removed
        total_index += idx

    print(f'\n{"=" * 60}')
    print(f'Markdown files updated: {total_updated}')
    print(f'Markdown files removed: {total_removed}')
    print(f'Index files updated:    {total_index}')


if __name__ == '__main__':
    main()
