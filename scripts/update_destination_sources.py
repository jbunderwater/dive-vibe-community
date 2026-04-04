#!/usr/bin/env python3
"""
Update source citations for a specific destination's markdown files.

Usage: python3 scripts/update_destination_sources.py <slug> <sources_json>

Where sources_json is a JSON string like:
  '[{"name": "Source Name", "url": "https://example.com"}, ...]'

These sources apply to ALL sites in the destination (destination-level sources).
For site-specific sources, use --site-sources with format:
  '{"site-filename": [{"name": "Source", "url": "URL"}], ...}'
"""

import json
import os
import re
import sys
import glob
from datetime import date

TODAY = date.today().isoformat()


def update_file_sources(filepath, dest_sources, site_specific_sources=None):
    """Update a single markdown file with source citations."""
    with open(filepath) as f:
        content = f.read()

    basename = os.path.basename(filepath).replace('.md', '')

    # Collect sources: site-specific take priority, then destination-level
    sources = []
    seen = set()

    # Add site-specific sources first
    if site_specific_sources and basename in site_specific_sources:
        for s in site_specific_sources[basename]:
            key = s['name'].lower()
            if key not in seen:
                seen.add(key)
                sources.append(s)

    # Add destination-level sources
    for s in dest_sources:
        key = s['name'].lower()
        if key not in seen:
            seen.add(key)
            sources.append(s)

    # Also preserve any existing sources with URLs that aren't in our new list
    existing_match = re.search(r'\*Sources: (.*?)\. Last updated', content)
    if existing_match:
        existing_text = existing_match.group(1)
        # Extract existing [Name](URL) entries
        for name, url in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', existing_text):
            key = name.lower()
            if key not in seen:
                seen.add(key)
                sources.append({'name': name, 'url': url})

    if not sources:
        return False  # No sources to add

    # Build footer
    parts = []
    for s in sources:
        if s.get('url'):
            parts.append(f'[{s["name"]}]({s["url"]})')
        else:
            parts.append(s['name'])

    sources_str = ', '.join(parts)
    footer = f'*Sources: {sources_str}. Last updated {TODAY}.*'

    # Remove old footer
    content = re.sub(
        r'\n---\n\*(?:Sources:|Description based on).*?\*\s*$',
        '',
        content,
        flags=re.DOTALL
    )

    # Add new footer
    content = content.rstrip('\n') + '\n\n---\n' + footer + '\n'

    with open(filepath, 'w') as f:
        f.write(content)

    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/update_destination_sources.py <slug> <sources_json> [--site-sources <json>]")
        sys.exit(1)

    slug = sys.argv[1]
    dest_sources = json.loads(sys.argv[2])

    site_specific_sources = None
    if '--site-sources' in sys.argv:
        idx = sys.argv.index('--site-sources')
        site_specific_sources = json.loads(sys.argv[idx + 1])

    dest_dir = f'divesites/{slug}'
    if not os.path.isdir(dest_dir):
        print(f"Error: {dest_dir} not found")
        sys.exit(1)

    md_files = sorted(glob.glob(os.path.join(dest_dir, '*.md')))
    updated = 0

    for md_file in md_files:
        if update_file_sources(md_file, dest_sources, site_specific_sources):
            updated += 1

    print(f"{slug}: {updated}/{len(md_files)} files updated with sources")


if __name__ == '__main__':
    main()
