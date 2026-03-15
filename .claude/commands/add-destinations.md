# Add Dive Destinations

Add new dive destinations to the database with full data pipeline and quality control.

## Usage

```
/add-destinations <region or destination list>
```

Examples:
- `/add-destinations Caribbean: Anguilla, St. Barths, Montserrat`
- `/add-destinations Southeast Asia`
- `/add-destinations hawaii-lanai`

## Workflow

Execute these steps in order. Use the TodoWrite tool to track progress.

### Step 1: Configure Destinations

Add entries to `destinations.json` for each new destination:
```json
{
  "name": "Human Readable Name",
  "slug": "url-friendly-slug",
  "region": "Region Name",
  "center": [lat, lon],
  "bounds": [[south, west], [north, east]],
  "description": "Brief description of diving highlights.",
  "overviewFile": "overview.md",
  "countryCode": "XX"
}
```

**Bounds must be tight** — just enough to cover the dive area. Overly large bounds cause Overpass API timeouts and pull irrelevant data.

Regions used: North America, Caribbean, Pacific, Asia, Europe, Africa, Middle East, Central America, South America, Oceania.

### Step 2: Scrape OpenStreetMap Data

Run both scrapers. Use `sleep` between batches to avoid Overpass API rate limits (429/504 errors). Retry failures after 10-15 seconds.

```bash
# Base scraper (accepts multiple slugs)
python3 scripts/gather_osm_all.py slug1 slug2 slug3

# Extended scraper (one at a time)
python3 scripts/gather_osm_extended.py -d slug1
```

If a scrape returns 0 results, it may be a timeout — retry once after waiting.

### Step 3: Quality Control — Remove Commercial Entries

This is CRITICAL. OSM data frequently includes dive shops, dive schools, and operators mixed in with actual dive sites. Check in English, French, and Spanish.

**Remove entries matching ANY of these:**

#### By OSM Tags
- `amenity=dive_centre` or `amenity=dive_center`
- `leisure=sports_centre` or `leisure=sports_center`
- `building=yes` (UNLESS also tagged `historic=wreck` — shipwrecks are legitimate)
- `shop=*` (any shop)
- `tourism=hotel|hostel|guest_house|resort`

#### By Name Pattern (case-insensitive, all languages)
- English: `dive center/centre/shop/school/store/academy`, `diving center/centre/school/college`, `scuba diving` (standalone), `PADI`, `SSI`
- French: `centre de plongée`, `club de plongée`, `école de plongée`, `[Name] Plongée` (e.g., "Alpha Plongée", "Plongée Passion")
- Spanish: `centro de buceo`, `escuela de buceo`, `club de buceo`, `tienda de buceo`
- Croatian/other: `ronilački centar`, `potapljanje`

#### Known False Positives (KEEP these)
- Names containing "Dive Site" or "Site de Plongée" — these are actual sites
- "Shark Hotel", "Montaña Rusa", "La Francesa" — legitimate dive site names
- Entries tagged `scuba_diving:divespot=yes` — verified dive spots
- Entries with `historic=wreck` even if also tagged `building=yes`

### Step 4: Strip Contact Information

Remove these tag fields from ALL entries:
- `website`, `phone`, `email`, `contact:*`, `url`, `fax`
- `opening_hours`, `operator`
- `addr:street`, `addr:city`, `addr:postcode`, `addr:housenumber`
- `facebook`, `instagram`, `twitter`, `tripadvisor`
- `verified`, `image`, `image1-9`
- `heritage:website`
- `source`, `source_ref`, `note` — only if they contain URLs (keep non-URL values like `source=curated`)

### Step 5: Data Validation

Run validation checks on all new data:
1. Every entry has non-empty `name`, valid `lat` (-90 to 90), valid `lon` (-180 to 180)
2. No duplicate names within any destination file
3. No remaining commercial tags or contact info
4. No URLs or email addresses anywhere in tag values

### Step 6: Gap-Fill Low-Coverage Destinations

If a destination has fewer than 8 sites after scraping and cleaning:
- Add well-known dive sites as curated entries with `tags: {"source": "curated", "addedBy": "gap_fill"}`
- Research real dive sites for the area — use well-established, widely-known sites
- Each curated entry needs: `name`, `lat`, `lon`, `depth`, `site_type` (reef/wreck/wall/cave/beach), `entry_type` (shore/boat), `difficulty` (Beginner/Intermediate/Advanced)

### Step 7: Final Summary

Print a summary table showing:
- Each new destination
- Site count
- Data sources (OSM / extended / curated)
- Any remaining concerns

### Step 8: Commit and Push

Stage all changed files and commit with a descriptive message listing all new destinations and their site counts.
