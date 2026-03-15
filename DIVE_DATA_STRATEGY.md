# Dive Data Strategy: Sources, Enrichment & Validation

## Additional Data Sources

Beyond OSM and Wikidata, there are several high-value sources we can integrate to build the most comprehensive and authoritative dive site dataset possible.

---

### Tier 1: Open Databases with APIs (Structured, Programmatic Access)

#### OpenDeepMap
- **URL**: https://opendeepmap.com/
- **License**: ODbL-1.0 (database), CC BY/BY-SA (media) — fully open
- **Data**: Dive site locations, access info, depths, currents, visibility, hazards, seasonality, logistics
- **Format**: WGS84/GeoJSON vector tiles
- **Access**: Open, attribution required
- **Value**: Purpose-built open dive site database with structured fields matching our schema almost exactly. This is our best complementary source to OSM.

#### The Dive API (thediveapi.com)
- **URL**: https://thediveapi.com/
- **Data**: 17,000+ dive sites with coordinates, descriptions, depths; 10,000+ dive operators with PADI/SSI/SDI affiliations
- **Access**: REST API with search by location name or GPS coordinates
- **Value**: Large coverage, includes dive operator data we don't currently track. Good for cross-referencing site names and filling coordinate gaps.

#### Diveboard API
- **URL**: https://github.com/Diveboard/Documentation/blob/master/API.md
- **License**: Free API access (register via support@diveboard.com for API key)
- **Data**: Dive spots, species observations from ~100,000 registered divers, dive logs with depth/conditions
- **Access**: Full REST API with JSON responses, CRUD operations on spots/dives
- **Value**: Real diver observations (species sightings, actual conditions) — excellent for enriching marine life sections with real data rather than generic descriptions.

#### Divesites.com API
- **URL**: http://divesites.com/ (API at api.divesites.com)
- **Data**: Dive site locations, weather, coordinates, tide stations
- **Access**: REST API — `GET /sites`, `GET /sites/{id}`, `GET /sites/search`
- **Value**: Weather and tide data integration for our "Best Time" fields.

#### Divestop (Open Source)
- **URL**: https://github.com/dulcetgnome/divestop
- **License**: Open source
- **Data**: Global dive sites as JSON with coordinates, max depth, gradient, description, aquatic life, features
- **Access**: Direct JSON download from GitHub
- **Value**: Ready-to-merge structured data. Fields like `aquatic_life` and `features` map directly to our marine life and site type fields.

---

### Tier 2: Scientific & Government Databases

#### GBIF — Diveboard Citizen Science Observations
- **URL**: https://www.gbif.org/dataset/66f6192f-6cc0-45fd-a2d1-e76f5ae3eab2
- **License**: CC0 (public domain)
- **Data**: 15,000+ marine species observations from scuba divers worldwide, with exact coordinates, depth, date, and diver name
- **Access**: GBIF Occurrence API (https://techdocs.gbif.org/en/openapi/v1/occurrence)
- **Value**: Real species sighting data at specific dive sites. Query by bounding box to get actual species lists for each destination — replaces generic "you may see colorful fish" with real data like "French angelfish sighted 47 times at this location."

#### GBIF — Reef Life Survey Global Reef Fish Dataset
- **URL**: https://www.gbif.org/dataset/38f06820-08c5-42b2-94f6-47cc3e83a54a
- **License**: CC BY
- **Data**: Scientific-grade fish abundance data from 50m transects on shallow rocky and coral reefs worldwide
- **Access**: GBIF API
- **Value**: The gold standard for reef fish data — collected by trained divers using standardized methods. Gives us species abundance (not just presence) per region.

#### REEF Volunteer Fish Survey Project
- **URL**: https://www.reef.org/database-reports
- **Data**: World's largest marine fish database from volunteer diver surveys. Covers 10 global regions since 1993. Includes species sighting frequency, abundance estimates, and biodiversity indices per site.
- **Access**: Web-based report generation (no formal API). Data may also be available via OBIS/GBIF aggregation.
- **Value**: Species frequency data per named dive site. Their "Geographic Area Report" gives species lists ranked by sighting frequency — perfect for our marine life sections.

#### OBIS (Ocean Biodiversity Information System)
- **URL**: https://obis.org/
- **License**: Open access
- **Data**: Global marine species occurrence records aggregated from hundreds of institutions
- **Access**: REST API with spatial queries
- **Value**: Aggregates data from GBIF, REEF, and many other sources. Query by bounding box to get comprehensive species lists per destination.

#### WDPA (World Database on Protected Areas)
- **URL**: https://www.protectedplanet.net/
- **License**: Non-commercial use
- **Data**: Global marine protected areas with boundaries, management categories, designation dates
- **Access**: API and bulk download
- **Value**: Annotate dive sites with MPA status, conservation regulations, and protected species information.

---

### Tier 3: Community & Operator Sources

#### Wannadive.net
- **URL**: https://wannadive.net/
- **Data**: World dive site atlas with coordinates, descriptions, user reviews
- **Access**: Web scraping only (no API, site reported intermittently available)
- **Value**: Good coverage of popular destinations with community-contributed data.

#### ScubaBoard Dive Site Catalogue
- **URL**: https://scubaboard.com/community/threads/dive-sites-catalogue.620620/
- **Data**: Community-contributed site descriptions, coordinates, and reviews
- **Access**: Forum scraping
- **Value**: Experienced diver insights and tips that are hard to find elsewhere.

#### Dive Operator Websites
- **Data**: Site-specific conditions, depth profiles, marine life, access instructions
- **Access**: Web scraping (per-operator)
- **Value**: The most operationally accurate data — operators know their sites. Best used for targeted enrichment of specific destinations.

---

### Tier 4: Environmental & Bathymetry Data

#### GEBCO (General Bathymetric Chart of the Oceans)
- **URL**: https://www.gebco.net/
- **License**: Public domain
- **Data**: Global ocean depth/terrain at 15 arc-second resolution (~450m)
- **Access**: Open Topo Data API (`https://api.opentopodata.org/v1/gebco2020?locations=LAT,LON`) or local NetCDF download
- **Value**: Validates depth claims and provides bathymetric context for every site.

#### Reef Check
- **URL**: https://www.reefcheck.org/
- **Data**: Coral reef health surveys (bleaching, disease, indicator species)
- **Access**: Reports and datasets (may require request)
- **Value**: Conservation context for overview documents — reef health status per destination.

---

## GPS Coordinate Validation: Land vs. Water

Ensuring every dive site coordinate actually points to water is critical for credibility. Here's our multi-layered validation approach.

### Layer 1: Fast Bulk Screening with `global-land-mask`

The [`global-land-mask`](https://pypi.org/project/global-land-mask/) Python package uses the GLOBE dataset sampled at ~1km resolution. It's offline, vectorized (numpy), and can check thousands of points in milliseconds.

```python
from global_land_mask import globe
import numpy as np

# Check a single dive site
is_valid = globe.is_ocean(lat=12.2106, lon=-68.3217)  # True = in water

# Batch check all sites
lats = np.array([site['lat'] for site in all_sites])
lons = np.array([site['lng'] for site in all_sites])
ocean_mask = globe.is_ocean(lats, lons)
land_sites = [s for s, valid in zip(all_sites, ocean_mask) if not valid]
```

**Limitation**: ~1km resolution means shore dive sites very close to the coastline may incorrectly flag as "land." This is expected — shore dives are *supposed* to be near land.

### Layer 2: Coastline-Aware Validation with Natural Earth + Shapely

For sites flagged as "on land" by the fast check, apply a higher-resolution test using [Natural Earth 10m coastline data](https://www.naturalearthdata.com/) with Shapely/GeoPandas:

```python
import geopandas as gpd
from shapely.geometry import Point

# Load high-res land polygons (10m = highest resolution)
land = gpd.read_file("ne_10m_land.shp")

def is_near_water(lat, lon, buffer_km=0.5):
    """Check if point is in water OR within buffer_km of coastline."""
    point = Point(lon, lat)
    # Direct water check
    if not any(land.contains(point)):
        return True  # Already in water
    # Buffer check: shore dive sites are on land but near water
    buffer_deg = buffer_km / 111  # rough km to degree conversion
    buffered = point.buffer(buffer_deg)
    # If the buffer intersects water (i.e., doesn't fully overlap with land), it's near coast
    return not all(land.contains(buffered))
```

**Why two layers**: The fast check handles 99% of sites. The detailed check catches shore dives that are legitimately at the water's edge.

### Layer 3: Bathymetry Cross-Check with GEBCO

For sites that pass the water check, verify that the claimed depth is plausible using GEBCO bathymetry data:

```python
import requests

def get_ocean_depth(lat, lon):
    """Query GEBCO via Open Topo Data for ocean depth at coordinate."""
    url = f"https://api.opentopodata.org/v1/gebco2020?locations={lat},{lon}"
    resp = requests.get(url).json()
    elevation = resp["results"][0]["elevation"]
    return elevation  # Negative = underwater, positive = above sea level

# Flag sites where:
# 1. GEBCO says elevation > 5m (definitely on land, not a shore dive)
# 2. Site claims 40m depth but GEBCO shows only 10m deep at that point
```

For heavy batch processing, download the GEBCO_2025 NetCDF grid and query locally with `xarray`:

```python
import xarray as xr

ds = xr.open_dataset("GEBCO_2025.nc")
depth = ds["elevation"].sel(lat=lat, lon=lon, method="nearest").values
```

### Layer 4: Destination Bounds Check

Every dive site coordinate must fall within its destination's defined bounding box (already in `destinations.json`):

```python
def validate_within_bounds(site, destination):
    """Ensure site coordinates fall within destination bounds."""
    bounds = destination['bounds']
    south, west = bounds[0]
    north, east = bounds[1]
    return (south <= site['lat'] <= north and west <= site['lng'] <= east)
```

### Edge Cases & How to Handle Them

| Scenario | Problem | Solution |
|---|---|---|
| Shore dive entries | Coordinate is literally on the beach | Accept if within 500m of water (Layer 2 buffer) |
| Small islands / atolls | Low-res data may not show the island at all | Use Natural Earth 10m data + GEBCO combined |
| Lagoon/harbor sites | Inside land mass but actually in water | GEBCO elevation check (negative = water) |
| River/lake dives | Not ocean, but valid water | Flag for manual review (our focus is ocean diving) |
| Coordinate on reef flat | Extremely shallow, GEBCO may show ~0m | Accept if GEBCO elevation is between -1m and +2m |

### Validation Pipeline Summary

```
For each dive site coordinate:
  1. Bounds check     → Must be within destination bbox
  2. Fast land check  → global-land-mask (1km resolution)
     ├─ PASS (ocean)  → Continue to step 3
     └─ FAIL (land)   → High-res check with Natural Earth 10m
         ├─ Within 500m of coastline → Flag as "shore site", accept
         └─ More than 500m inland    → REJECT (bad coordinate)
  3. GEBCO depth      → Query bathymetry
     ├─ Elevation < -1m   → Valid underwater site
     ├─ Elevation -1 to 2m → Likely shore/shallow site, accept
     └─ Elevation > 5m    → REJECT (on land)
  4. Depth plausibility → Compare claimed maxDepth vs GEBCO depth
     └─ Flag if claimed depth > |GEBCO depth| * 1.5
```

### Recommended Implementation

Add a `validate_coordinates.py` script that:
1. Loads all `index.json` files across destinations
2. Runs the 4-layer validation pipeline
3. Produces a report: `validation_report.json` with pass/fail/warning per site
4. Can be integrated into CI to catch bad coordinates on every PR

---

## Recommended Source Priority for Implementation

| Priority | Source | Why | Effort |
|---|---|---|---|
| 1 | OpenDeepMap | Open license, structured, closest to our schema | Low |
| 2 | Divestop (GitHub) | Direct JSON merge, open source | Low |
| 3 | GBIF (Diveboard + RLS) | Real species data, public domain, good API | Medium |
| 4 | GEBCO + global-land-mask | Coordinate validation + depth verification | Medium |
| 5 | The Dive API | Large dataset, operator info | Medium |
| 6 | Diveboard API | Diver-reported conditions and species | Medium |
| 7 | OBIS | Aggregated marine species | Medium |
| 8 | WDPA | Marine protected area annotations | Medium |
| 9 | REEF | Species frequency per site | Medium-High |
| 10 | Wannadive / ScubaBoard | Community knowledge gap-filling | High (scraping) |
