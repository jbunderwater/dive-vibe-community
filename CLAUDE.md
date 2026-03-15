# Dive Vibe Community - Claude Code Instructions

## Project Overview

A community-driven dive site database with 120+ destinations and 2,700+ dive sites worldwide. Data is sourced from OpenStreetMap (Overpass API) and supplemented with curated entries.

## Architecture

```
destinations.json              # Master config (name, slug, region, bounds, countryCode)
data/osm/{slug}.json           # Raw Overpass API scrape results
data/osm_clean/{slug}.json     # Cleaned data (commercial entries removed)
data/external/osm_extended/    # Extended scraper results (wrecks, reefs, caves)
divesites/{slug}/index.json    # Generated site index
divesites/{slug}/*.md          # Generated site markdown pages
scripts/
  gather_osm_all.py            # Base Overpass scraper (accepts slug args)
  gather_osm_extended.py       # Extended scraper (-d slug, --wrecks-only, --gaps-only)
  clean_osm_data.py            # Bulk cleaner
  fill_new_destinations.py     # Curated site gap-filler
  generate_sites.py            # Markdown generator
```

## Data Quality Standards

These standards MUST be enforced on every data change:

### 1. No Commercial Businesses
Dive sites only - never dive shops, schools, operators, or hotels. Check in ALL languages:
- **English**: dive center/centre, dive shop, dive school, PADI, SSI, scuba diving (as standalone name)
- **French**: centre de plongée, club de plongée, école de plongée, [Name] Plongée (e.g., "Alpha Plongée")
- **Spanish**: centro de buceo, escuela de buceo, club de buceo, tienda de buceo
- **OSM tags**: Remove entries with `amenity=dive_centre`, `leisure=sports_centre`, `building=yes` (unless `historic=wreck`)
- **Edge cases**: "Dive Site" or "Site de Plongée" in the name = legitimate site; names like "Shark Hotel" = legitimate dive site name

### 2. No Contact Information
Strip these tag fields: `website`, `phone`, `email`, `contact:*`, `url`, `fax`, `opening_hours`, `operator`, `addr:*`, `facebook`, `instagram`, `twitter`, `verified`, `image*`, `heritage:website`
Also strip `source`, `source_ref`, `note` if they contain URLs.

### 3. Data Integrity
- Every site must have: `name` (non-empty), `lat` (-90 to 90), `lon` (-180 to 180)
- No duplicate names within a destination
- Minimum 8 sites per destination (gap-fill with curated data if needed)

### 4. Coordinate Validation
All coordinates must fall within the destination's bounding box defined in `destinations.json`.

## Adding New Destinations Workflow

Use the `/add-destinations` slash command for the full agentic workflow, or follow these steps manually:

1. Add entry to `destinations.json` with: name, slug, region, center, bounds, description, countryCode
2. Run base scraper: `python3 scripts/gather_osm_all.py <slug>`
3. Run extended scraper: `python3 scripts/gather_osm_extended.py -d <slug>`
4. Run quality checks (see below)
5. Gap-fill if < 8 sites with curated data
6. Run `python3 scripts/generate_sites.py` to generate markdown

## Quality Check Script Pattern

After any data change, run this validation:

```python
# Check for: commercial tags, commercial names (EN/FR/ES), building tags,
# URLs/emails in tags, missing names, invalid coordinates, duplicates,
# low site counts (< 8)
```

See `/add-destinations` and `/quality-check` slash commands for automated versions.
