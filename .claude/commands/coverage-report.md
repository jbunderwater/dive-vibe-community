# Dive Site Coverage Report

Generate a comprehensive coverage report showing site counts by region, country, and destination, with gap analysis.

## Usage

```
/coverage-report [region or country]
```

Examples:
- `/coverage-report` — full global report
- `/coverage-report US` — US destinations only
- `/coverage-report Caribbean` — Caribbean region

## Report Contents

### 1. Regional Summary Table

Group all destinations by region and show:
- Destination name
- Country code
- Site count from `data/osm_clean/{slug}.json`
- Extended OSM data available (yes/no, from `data/external/osm_extended/`)
- Data sources breakdown (OSM vs curated)

### 2. Coverage Gaps

Identify:
- Destinations with < 8 sites (need curated data)
- Destinations with no extended OSM data
- Regions with limited representation
- Major dive areas not yet in the database

### 3. Data Source Breakdown

For each destination, count entries by `tags.addedBy` or `tags.source`:
- `osm` — from base Overpass scraper
- `extended_overpass` / `osm_extended` — from extended scraper
- `curated` / `gap_fill` — manually added

### 4. Skew Analysis

Flag destinations with disproportionately high counts (e.g., Newfoundland at 110, British Columbia at 184) that may need review for quality vs quantity.

### 5. Recommendations

Suggest:
- New destinations to add for underrepresented regions
- Destinations that would benefit from extended scraping
- Destinations needing curated data supplementation
