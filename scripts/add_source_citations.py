#!/usr/bin/env python3
"""
Add standardized source citations to all dive site markdown files.

This script:
1. Parses existing citation info from markdown files (## Sources sections, compiled-from lines)
2. Cross-references validation_source from osm_clean JSON data
3. Generates standardized *Sources: ... Last updated YYYY-MM-DD.* footer lines
4. Handles overview files separately from individual site files

The standard footer format (from CLAUDE.md):
  *Sources: [Source Name](URL), [Source Name](URL). Last updated YYYY-MM-DD.*
  OR if no sources: *Description based on regional diving characteristics. No site-specific sources found.*
"""

import json
import os
import re
import glob
import sys
from datetime import date

TODAY = date.today().isoformat()

def load_json_sources(slug):
    """Load validation_source data from osm_clean JSON for a destination."""
    json_path = f'data/osm_clean/{slug}.json'
    site_sources = {}
    if os.path.exists(json_path):
        with open(json_path) as f:
            data = json.load(f)
        for site in data:
            vs = site.get('validation_source', '')
            name = site.get('name', '')
            if vs and name:
                site_sources[name.lower().strip()] = vs
    return site_sources


def slug_from_filename(filepath):
    """Extract site name from markdown filename for matching."""
    basename = os.path.basename(filepath).replace('.md', '')
    return basename.replace('-', ' ')


def extract_existing_sources_section(content):
    """Extract URLs and source names from ## Sources section."""
    sources = []
    match = re.search(r'## Sources\s*\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
    if match:
        section = match.group(1)
        # Extract markdown links: [Name](URL)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', section)
        for name, url in links:
            sources.append({'name': name, 'url': url})
        # Extract plain text source names (lines starting with -)
        for line in section.strip().split('\n'):
            line = line.strip().lstrip('- ')
            if line and not re.search(r'\[.*\]\(.*\)', line) and not line.startswith('OpenStreetMap'):
                # Plain text source without URL
                if len(line) > 5 and not line.startswith('Local') and not line.startswith('Regional') and not line.startswith('Marine') and not line.startswith('Various'):
                    sources.append({'name': line.rstrip('.'), 'url': None})
    return sources


def extract_compiled_from_sources(content):
    """Extract source names from 'compiled from...' lines."""
    match = re.search(r'compiled from\s+(.+?)\.?\s*Last updated', content)
    if not match:
        match = re.search(r'compiled from\s+(.+?)\.?\s*\*?\s*$', content, re.MULTILINE)
    if not match:
        return [], False

    text = match.group(1).strip()

    # Check if it's generic
    generic_patterns = [
        'OpenStreetMap data and regional diving knowledge',
        'OpenStreetMap data, regional diving knowledge, and Atlantic marine research',
        'OpenStreetMap data and regional diving research',
        'regional dive operators, ScubaBoard trip reports, and firsthand diving accounts',
        'liveaboard operator sources, ScubaBoard trip reports, and firsthand diving accounts',
        'liveaboard operator sources and regional diving knowledge',
        'diver community sources and regional diving knowledge',
        'multiple diving sources and local knowledge',
    ]

    is_generic = text.strip().rstrip('*') in generic_patterns

    if is_generic:
        return [], True

    # Has specific sources - parse them
    sources = []
    # Split on commas and "and"
    parts = re.split(r',\s*(?:and\s+)?|\s+and\s+', text)
    for part in parts:
        part = part.strip().rstrip('*')
        if part and len(part) > 2:
            # Skip generic phrases
            if part.lower() in ['regional diving knowledge', 'multiple', 'local knowledge',
                                 'firsthand diving accounts', 'regional diving research',
                                 'atlantic marine research', 'openstreetmap data']:
                continue
            sources.append({'name': part, 'url': None})

    return sources, is_generic


def extract_last_updated(content):
    """Extract existing last updated date."""
    match = re.search(r'Last [Uu]pdated[:\s]*(\d{4}-\d{2}-\d{2})', content)
    if match:
        return match.group(1)
    match = re.search(r'Last updated[:\s]*((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', content)
    if match:
        return match.group(1)
    return None


def format_sources_footer(sources, last_updated=None):
    """Format sources into the standard footer line."""
    if not last_updated:
        last_updated = TODAY

    if not sources:
        return f'*Description based on regional diving characteristics. No site-specific sources found. Last updated {last_updated}.*'

    parts = []
    seen = set()
    for s in sources:
        name = s['name']
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        if s.get('url'):
            parts.append(f'[{name}]({s["url"]})')
        else:
            parts.append(name)

    sources_str = ', '.join(parts)
    return f'*Sources: {sources_str}. Last updated {last_updated}.*'


def remove_old_citations(content):
    """Remove old citation patterns from content."""
    # Remove ## Sources section and everything after it until --- or next ##
    content = re.sub(
        r'\n## Sources\s*\n.*?(?=\n## [^S]|\Z)',
        '',
        content,
        flags=re.DOTALL
    )

    # Remove "compiled from" footer lines
    content = re.sub(
        r'\n---\s*\n\*This dive site information was (?:compiled from|contributed by).*?\*\s*$',
        '',
        content,
        flags=re.MULTILINE | re.DOTALL
    )

    # Remove standalone compiled-from lines without ---
    content = re.sub(
        r'\n\*This dive site information was (?:compiled from|contributed by).*?\*\s*$',
        '',
        content,
        flags=re.MULTILINE
    )

    # Remove old Additional Resources section if it only contains Last Updated
    content = re.sub(
        r'\n## Additional Resources\s*\n\s*- \*\*Last Updated\*\*:.*?\n',
        '\n',
        content
    )

    # Clean up trailing whitespace and extra newlines
    content = content.rstrip('\n') + '\n'

    return content


def process_file(filepath, json_sources, dry_run=False):
    """Process a single markdown file to add/update source citations."""
    with open(filepath) as f:
        content = f.read()

    # Skip overview files - handle separately
    if os.path.basename(filepath) == 'overview.md':
        return None

    # Skip template
    if '_template' in filepath:
        return None

    # Collect all sources for this file
    all_sources = []

    # 1. Extract from ## Sources section (with URLs)
    section_sources = extract_existing_sources_section(content)
    all_sources.extend(section_sources)

    # 2. Extract from compiled-from line
    compiled_sources, is_generic = extract_compiled_from_sources(content)
    all_sources.extend(compiled_sources)

    # 3. Cross-reference with JSON validation_source
    site_slug = slug_from_filename(filepath)
    # Try to match by site name from frontmatter
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        site_name = name_match.group(1).strip()
        json_vs = json_sources.get(site_name.lower().strip(), '')
        if json_vs:
            # Parse validation_source - often comma-separated source names
            for src in re.split(r',\s*', json_vs):
                src = src.strip()
                if src and src.lower() not in ['perplexity', 'openstreetmap tags', 'osm seamark data']:
                    # Check if it's not already in our list
                    existing_names = {s['name'].lower() for s in all_sources}
                    if src.lower() not in existing_names:
                        all_sources.append({'name': src, 'url': None})

    # Get existing last updated date
    last_updated = extract_last_updated(content)

    # Format the new footer
    footer = format_sources_footer(all_sources, last_updated)

    # Remove old citations
    new_content = remove_old_citations(content)

    # Add new footer
    new_content = new_content.rstrip('\n') + '\n\n---\n' + footer + '\n'

    if dry_run:
        if content != new_content:
            return {'file': filepath, 'sources': len(all_sources), 'footer': footer}
        return None

    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return {'file': filepath, 'sources': len(all_sources), 'footer': footer}

    return None


def process_overview(filepath, dry_run=False):
    """Process overview.md files separately."""
    with open(filepath) as f:
        content = f.read()

    # Extract sources from overview
    section_sources = extract_existing_sources_section(content)
    compiled_sources, is_generic = extract_compiled_from_sources(content)
    all_sources = section_sources + compiled_sources

    last_updated = extract_last_updated(content)
    footer = format_sources_footer(all_sources, last_updated)

    new_content = remove_old_citations(content)
    new_content = new_content.rstrip('\n') + '\n\n---\n' + footer + '\n'

    if dry_run:
        if content != new_content:
            return {'file': filepath, 'sources': len(all_sources), 'footer': footer}
        return None

    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return {'file': filepath, 'sources': len(all_sources), 'footer': footer}
    return None


def main():
    dry_run = '--dry-run' in sys.argv
    specific_slug = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            specific_slug = arg
            break

    if dry_run:
        print("DRY RUN - no files will be modified")

    dest_dirs = sorted(glob.glob('divesites/*/'))
    if specific_slug:
        dest_dirs = [f'divesites/{specific_slug}/']

    total_modified = 0
    total_with_sources = 0
    total_no_sources = 0

    for dest_dir in dest_dirs:
        slug = dest_dir.rstrip('/').split('/')[-1]
        if slug.endswith('.md'):
            continue

        json_sources = load_json_sources(slug)
        md_files = sorted(glob.glob(os.path.join(dest_dir, '*.md')))

        dest_modified = 0
        for md_file in md_files:
            if os.path.basename(md_file) == 'overview.md':
                result = process_overview(md_file, dry_run)
            else:
                result = process_file(md_file, json_sources, dry_run)

            if result:
                dest_modified += 1
                total_modified += 1
                if result['sources'] > 0:
                    total_with_sources += 1
                else:
                    total_no_sources += 1
                if dry_run and dest_modified <= 2:
                    print(f"  {result['file']}: {result['footer'][:100]}...")

        if dest_modified > 0:
            print(f"{slug}: {dest_modified} files modified ({len(json_sources)} JSON sources available)")

    print(f"\nTotal: {total_modified} files modified")
    print(f"  With sources: {total_with_sources}")
    print(f"  No sources (generic): {total_no_sources}")


if __name__ == '__main__':
    main()
