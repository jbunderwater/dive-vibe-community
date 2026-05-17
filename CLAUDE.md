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
  generate_sites.py            # Markdown stub generator (frontmatter + brief overview + structural Site Information only; no auto-generated marine life, dive profile, photography, or safety claims)
  strip_boilerplate.py         # Removes auto-generated boilerplate sections from existing markdown
  sync_sites.py                # Sync osm_clean changes to markdown frontmatter + index.json
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

### 3. Accurate Site Types (NOT defaulting to "reef")
The Overpass scraper defaults `site_type=reef` for any site without explicit tags. This is wrong ~30% of the time. Every site's type MUST be validated against real sources.

**Valid site types**: `reef`, `wall`, `wreck`, `cave`, `muck`, `beach`, `drift`, `pinnacle`

**Known misclassification patterns**:
- Muck diving destinations (Lembeh) scraped as "reef"
- Wall diving destinations (Bunaken, Bonaire) scraped as "reef"
- Pelagic/pinnacle destinations (Socorro, Galapagos, Cocos) scraped as "reef"
- Wreck sites without "wreck" in the name scraped as "reef"
- Surf breaks (Oahu) scraped as dive sites

**Validation source**: Use local dive operator websites (highest priority for site-specific details), ScubaBoard forums (scubaboard.com), and structured dive databases. Local operators list dive sites with accurate depths, conditions, and marine life descriptions that generic databases lack. See `/validate-sites` command.

### 4. Data Integrity
- Every site must have: `name` (non-empty), `lat` (-90 to 90), `lon` (-180 to 180), `difficulty` (not None)
- No duplicate names within a destination
- No near-duplicates from overlapping gap-fill passes (e.g., "The Boiler" + "The Boiler San Benedicto")
- Minimum 8 sites per destination (gap-fill with curated data if needed)
- No surf breaks, surfing spots, or non-diving entries

### 5. Coordinate Validation
All coordinates must fall within the destination's bounding box defined in `destinations.json`.

## Slash Commands

- `/add-destinations` — Full pipeline for adding new destinations (config, scrape, clean, validate, gap-fill)
- `/quality-check` — Comprehensive data quality audit (commercial, contacts, duplicates, types, difficulty)
- `/validate-sites` — Research-driven site type validation using ScubaBoard and dive forums
- `/coverage-report` — Regional coverage analysis with gap identification

## Adding New Destinations Workflow

Use the `/add-destinations` slash command for the full agentic workflow, or follow these steps manually:

1. Add entry to `destinations.json` with: name, slug, region, center, bounds, description, countryCode
2. Run base scraper: `python3 scripts/gather_osm_all.py <slug>`
3. Run extended scraper: `python3 scripts/gather_osm_extended.py -d <slug>`
4. Run quality checks (`/quality-check`)
5. Gap-fill if < 8 sites with curated data
6. **Validate site types and descriptions** (`/validate-sites`) — research each site against ScubaBoard and dive forums, update both JSON data and markdown descriptions
7. Run `python3 scripts/generate_sites.py <slug>` to generate markdown for a new destination. By default the script SKIPS files that already exist — it is safe to re-run. The generator intentionally produces only frontmatter + a brief identifying overview + structural Site Information — no marine life, dive profile, photography, or safety claims, since those require site-specific research. Pass `--force <slug>` only if you intentionally want to overwrite existing hand-curated content for a specific destination.
8. Run `python3 scripts/sync_sites.py <slug>` after any osm_clean data changes to sync frontmatter + index.json (safe — only updates frontmatter fields, preserves description content)

## Anti-Hallucination Policy (CRITICAL)

AI-generated descriptions are the highest-risk area for data quality. These rules apply to ALL site descriptions:

1. **Never fabricate historical facts.** No invented dates, dimensions, tonnage, vessel names, or sinking narratives. Require 2+ independent sources for any historical claim. Wreck histories are the #1 hallucination risk.
2. **Never fabricate marine life.** Only attribute species to a site if a source confirms sightings at that specific site. Do not pad descriptions with regional species lists presented as site-specific.
3. **Never claim wreck penetration is "safe."** Always note it requires proper training and equipment.
4. **Flag uncertainty.** When sources conflict, note the discrepancy. "Sources report depths between 28-34 meters" is better than picking one number.
5. **Verify access claims.** Do not guess shore vs. boat, distance from shore, or typical conditions without source confirmation.
6. **No "mysterious circumstances" filler.** Either state verified facts or explicitly acknowledge what is unknown.
7. **Cross-reference wreck data.** Ship name, build date, length, tonnage, sinking cause — each must appear in 2+ sources before inclusion.

## Agentic Research Pattern

For site validation and destination research, use parallel agents:
- Launch web search agents for groups of 5-10 sites at a time
- Use Perplexity MCP tools (`perplexity_ask`, `perplexity_research`) for detailed site research
- **Dive shop website scraping** (highest priority source — see pattern below)
- Primary source: `site:scubaboard.com "[site name]" "[destination]" dive`
- Secondary: dive operator sites, DiveAdvisor, Wannadive, PADI Travel
- Always validate the destination's overall diving character BEFORE individual sites
- Cold-water destinations: minimum Intermediate difficulty
- Remote liveaboard destinations: minimum Advanced difficulty

### Dive Shop Website Scraping

Local dive shops and operators are the single best source for dive site descriptions. They list their dive sites with accurate depths, conditions, marine life, and site-specific details that generic databases lack. They typically won't have GPS coordinates, but their descriptions are invaluable for updating site types, depths, difficulty, and markdown content.

**Process:**
1. **Search for dive shops**: WebSearch for `"[destination] dive shop"`, `"[destination] dive operator"`, `"[destination] scuba diving"`, `"[destination] dive center"`
2. **Find their dive site pages**: Most dive shops have a "Dive Sites", "Our Sites", or "Where We Dive" page. Look for links like `/dive-sites`, `/sites`, `/diving`, `/our-dives` on their homepage.
3. **Fetch and extract**: Use WebFetch to load each dive shop's dive site listing page. Extract site names, descriptions, depths, site types, difficulty levels, and marine life mentions.
4. **Cross-reference with our data**: Match dive shop site names against existing sites in `data/osm_clean/{slug}.json`. Site names may differ slightly (e.g., "The Cathedral" vs "Cathedral"), so use fuzzy matching.
5. **Update from findings**: Use the descriptions to correct site_type, depth, difficulty, and to rewrite generic markdown descriptions with site-specific content.

**Tips:**
- Search in the local language too (e.g., `"[destination] centre de plongée"` for French-speaking destinations)
- Many shops list 20-40 dive sites with individual descriptions — one good shop page can validate half a destination
- If a shop's site listing page links to individual site pages, fetch those too for more detail
- Multiple shops in the same area often list the same sites — cross-referencing confirms accuracy

### Data + Description Update Flow

When validating a destination, agents must update **three things**:
1. **`data/osm_clean/{slug}.json`** — site_type, difficulty, depth, entry_type, validation tags (including `validation_source` with domain names)
2. **`divesites/{slug}/*.md`** — rewrite generic template descriptions with site-specific content from research, and **credit sources in the footer** (see Source Attribution in `/validate-sites` command)
3. **Run `python3 scripts/sync_sites.py <slug>`** — propagates frontmatter fields from osm_clean to markdown files and rebuilds index.json

The quality standard for descriptions is the hand-curated Bonaire/Curaçao files. Generic template text like "rewarding diving on healthy coral reef structures" must be replaced with specific, researched content when information is available.

### Source Attribution (REQUIRED)

Every research-updated markdown file must credit the actual sources used — not generic "compiled from regional diving knowledge" filler. The markdown footer format is:
```
*Sources: [Source Name](URL), [Source Name](URL). Last updated YYYY-MM-DD.*
```
If no site-specific source was found, say so explicitly: `*Description based on regional diving characteristics. No site-specific sources found.*`
