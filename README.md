# Dive Vibe Community Data

A community-driven dive site database with 120+ destinations and 2,700+ dive sites worldwide. Data is sourced from OpenStreetMap (Overpass API) and supplemented with curated entries and AI-assisted research validation.

## Repository Structure

```
dive-vibe-community/
├── destinations.json              # Master config (name, slug, region, bounds, countryCode)
├── divesites/                     # Generated dive site pages
│   └── {slug}/
│       ├── index.json             # Site index for the destination
│       └── {site-name}.md        # Individual site pages (frontmatter + description)
├── data/
│   ├── osm/{slug}.json            # Raw Overpass API scrape results
│   ├── osm_clean/{slug}.json      # Cleaned data (commercial entries removed)
│   └── external/osm_extended/     # Extended scraper results (wrecks, reefs, caves)
├── scripts/
│   ├── gather_osm_all.py          # Base Overpass scraper
│   ├── gather_osm_extended.py     # Extended scraper (wrecks, reefs, caves)
│   ├── clean_osm_data.py          # Bulk cleaner (removes commercial entries)
│   ├── fill_new_destinations.py   # Curated site gap-filler
│   ├── generate_sites.py         # Markdown generator (full regeneration)
│   └── sync_sites.py             # Sync osm_clean changes → markdown frontmatter + index.json
└── .claude/
    └── commands/                  # Claude Code slash commands (agentic workflows)
        ├── add-destinations.md    # /add-destinations — full pipeline for new destinations
        ├── quality-check.md       # /quality-check — data quality audit
        ├── validate-sites.md      # /validate-sites — research-driven site validation
        └── coverage-report.md     # /coverage-report — regional coverage analysis
```

## Data Pipeline

```
OpenStreetMap ──► gather_osm_all.py ──► data/osm/{slug}.json
                  gather_osm_extended.py ──► data/external/osm_extended/
                          │
                          ▼
                  clean_osm_data.py ──► data/osm_clean/{slug}.json
                          │
                          ▼
                  generate_sites.py ──► divesites/{slug}/*.md (first time)
                          │
                          ▼
              /validate-sites ──► Research + rewrite descriptions
                          │
                          ▼
                  sync_sites.py ──► Update frontmatter + index.json
```

## Working with Claude Code

This repository is designed to be maintained using [Claude Code](https://docs.anthropic.com/en/docs/claude-code). The `.claude/commands/` directory contains slash commands that automate complex multi-step workflows.

### Prerequisites

1. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
2. Clone this repository
3. Ensure Python 3 is available (for the data scripts)

### Available Slash Commands

#### `/add-destinations <region or destination list>`

Full pipeline for adding new diving destinations:
- Configures `destinations.json` with geographic bounds
- Scrapes OpenStreetMap for dive site data
- Removes commercial businesses (dive shops, schools)
- Validates data integrity and site types
- Gap-fills destinations with fewer than 8 sites
- Generates markdown site pages

#### `/quality-check [slug or "all"]`

Comprehensive data quality audit:
- Detects commercial businesses in all languages (EN/FR/ES)
- Strips contact information and URLs
- Finds near-duplicate sites
- Validates coordinates against destination bounds
- Checks site type and difficulty assignments

#### `/validate-sites <slug> [options]`

**Research-driven site validation** — the core quality improvement workflow. This command dispatches parallel AI agents that:
1. Research each destination's diving character using web sources
2. Correct site types (many sites are incorrectly tagged as "reef")
3. Fix placeholder depths (default 20m) with actual values
4. Rewrite generic template descriptions with site-specific content
5. Add validation tags with source citations

```bash
# Validate a single destination
claude "/validate-sites scapa-flow"

# Validate multiple destinations
claude "/validate-sites bahamas bermuda cayman-islands"

# Validate all unvalidated destinations
claude "/validate-sites --unvalidated"

# Validate an entire region
claude "/validate-sites --region Caribbean"
```

**What it changes:**
- `data/osm_clean/{slug}.json` — site_type, difficulty, depth, entry_type, validation tags
- `divesites/{slug}/*.md` — replaces generic descriptions with researched content
- `divesites/{slug}/index.json` — updated via `sync_sites.py`

**Example improvement (Scapa Flow):**

Before:
> SMS Brummer is a reef dive site in Scapa Flow, Europe.
> SMS Brummer is a dive site in Scapa Flow offering rewarding diving on healthy coral reef structures.

After:
> SMS Brummer is a fast mine-laying cruiser lying on her starboard side in 36 metres of water. Best known for her distinctive brass bridge — installed as an anti-magnetic-mine measure — she is one of Scapa Flow's most photogenic wrecks.

#### `/coverage-report [region or country]`

Regional coverage analysis:
- Site counts per destination
- Gap identification (destinations with < 8 sites)
- Data source breakdown (OSM vs curated)
- Recommendations for new destinations

### Typical Workflow

```bash
# 1. Add new destinations for a region
claude "/add-destinations Pacific"

# 2. Run quality checks
claude "/quality-check all"

# 3. Validate and improve site data with research
claude "/validate-sites --region Pacific"

# 4. Check coverage
claude "/coverage-report Pacific"
```

### Batch Validation (Overnight Runs)

For bulk validation of all 122 destinations, use the batch scripts:

```bash
# Check current validation progress
./scripts/validate_batch.sh status

# Run a specific batch (1-9)
./scripts/validate_batch.sh 3

# Run the next unprocessed batch
./scripts/validate_batch.sh next

# Run all remaining batches overnight (start before bed)
nohup ./scripts/validate_overnight.sh >> logs/validate.log 2>&1 &

# Monitor progress
tail -f logs/validate.log
```

Destinations are grouped into 9 batches by priority:
1. Specialty sites (wrecks, muck, pelagic) — highest misclassification risk
2. Caribbean (part 1)
3. Caribbean (part 2)
4. Southeast Asia
5. Pacific & East Asia
6. Europe & Middle East
7. Africa & Indian Ocean
8. North America (East) & Oceania
9. North America (West) & remaining

Each batch commits and pushes its changes automatically.

### Manual Data Updates

If you edit `data/osm_clean/{slug}.json` directly (changing depths, types, difficulty), sync the changes to markdown:

```bash
python3 scripts/sync_sites.py <slug>
```

This updates frontmatter in the `.md` files and rebuilds `index.json`.

## Data Quality Standards

All data changes must meet these standards (enforced by `/quality-check`):

1. **No commercial businesses** — dive sites only, never shops/schools/operators
2. **No contact information** — no websites, phones, emails, social media
3. **Accurate site types** — validated against real sources, not defaulting to "reef"
4. **Data integrity** — every site needs name, coordinates, difficulty
5. **Coordinate validation** — all coordinates within destination bounding box
6. **No duplicates** — no duplicate or near-duplicate site names

See `CLAUDE.md` for the full specification.

## Current Coverage

- **122 destinations** across all major diving regions
- **2,700+ dive sites** sourced from OpenStreetMap and curated entries
- **Regions**: Caribbean, North America, Central/South America, Pacific, Southeast Asia, Indian Ocean, Middle East, Europe, Africa, Polar

## Contributing

### With Claude Code (recommended)

1. Fork and clone the repository
2. Use `/validate-sites <slug>` to improve site data quality
3. Use `/add-destinations` to add new destinations
4. Submit a pull request

### Manual contributions

1. Fork the repository
2. Add or update dive site data in `data/osm_clean/{slug}.json`
3. Run `python3 scripts/sync_sites.py <slug>` to sync changes
4. Submit a pull request

### Data Guidelines

- **Accuracy**: All information must be verifiable against real sources
- **No fabrication**: Only write what research supports
- **Source citation**: Note validation sources in the `validation_source` tag
- **Consistency**: Follow the established data format

## OpenStreetMap Attribution

This project includes data derived from OpenStreetMap and therefore must preserve attribution and share-alike requirements for derivative databases.

- Required credit: `© OpenStreetMap contributors`
- Required link: [https://www.openstreetmap.org/copyright](https://www.openstreetmap.org/copyright)
- If you publicly use a derivative database from this repository, provide ODbL-compliant attribution and make the derivative database available under ODbL 1.0

Copy-ready attribution text and implementation guidance are in [ATTRIBUTION.md](ATTRIBUTION.md).

## License

Licensing is split by content type:

- **Code in `scripts/` and project tooling**: MIT License (`LICENSE`)
- **Data in `data/` and generated database artifacts (including `divesites/*/index.json`)**: Open Database License (ODbL) 1.0 (`LICENSE-DATA.md`)
- **Site markdown narrative content in `divesites/*/*.md`**: follow source-based rights and ensure OSM-derived facts remain ODbL-compliant when redistributed as a database

See `LICENSE`, `LICENSE-DATA.md`, and `ATTRIBUTION.md` for details.
