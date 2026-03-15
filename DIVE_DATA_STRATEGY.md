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

### Tier 2b: Marine Species & Taxonomy Databases

#### FishBase / SeaLifeBase
- **URL**: https://www.fishbase.org/ (API: https://ropensci.github.io/fishbaseapidocs/)
- **License**: CC-BY-NC
- **Data**: Species biology, ecology, morphology, distribution, common names, habitat, depth ranges, images for 30,000+ fish species. SeaLifeBase covers ~200,000 aquatic species.
- **Access**: S3/Parquet endpoints, R package (`rfishbase`), legacy REST API
- **Value**: Authoritative species detail. For every species we list under "Marine Life," we can pull depth range, habitat description, common names in multiple languages, and photos. Turns "you may see angelfish" into "French Angelfish (Pomacanthus paru) — commonly found at 5-30m on coral reefs."

#### WoRMS (World Register of Marine Species)
- **URL**: https://www.marinespecies.org/ (REST API at marinespecies.org/rest)
- **License**: CC-BY
- **Data**: Taxonomic names, classification hierarchy, synonyms, vernacular names for 247,000+ valid marine species. AphiaIDs enable cross-linking between OBIS, GBIF, and FishBase.
- **Access**: REST API, R package (`worrms`)
- **Value**: Taxonomic backbone — ensures species names are correct and standardized across all our content. Prevents misidentification errors.

#### iNaturalist
- **URL**: https://www.inaturalist.org/ (API: https://api.inaturalist.org/v1/docs/)
- **License**: Varies per observation (many CC-BY-NC); research-grade data flows to GBIF
- **Data**: Species observations with photos, coordinates, community ID verification. Growing marine content from divers/snorkelers.
- **Access**: REST API (v1/v2), Python (`pyinaturalist`). Rate limit ~1 req/sec. Bulk via GBIF export.
- **Value**: Photo-verified species sightings at specific coordinates. Supplements GBIF data with visual proof and recent observations.

---

### Tier 2c: Reef & Coral Monitoring

#### Allen Coral Atlas
- **URL**: https://allencoralatlas.org/
- **License**: Free with citation (Zenodo DOI: 10.5281/zenodo.3833242)
- **Data**: Geomorphic zonation, benthic habitat classification, reef extent, bleaching alerts, turbidity — all at **5m pixel resolution** from PlanetScope satellite imagery.
- **Access**: Direct download by country, Google Earth Engine API (`ACA/reef_habitat/v2_0`)
- **Value**: The best available global reef map. Can annotate every reef dive site with habitat type (e.g., "outer reef slope," "back reef," "lagoon") and monitor bleaching risk.

#### NOAA Coral Reef Watch
- **URL**: https://coralreefwatch.noaa.gov/
- **License**: Public domain (US government)
- **Data**: Sea surface temperature, bleaching alerts (degree heating weeks), near-real-time satellite monitoring at 5km resolution.
- **Access**: ERDDAP, data downloads, near-real-time feeds
- **Value**: Dynamic environmental context — "current bleaching risk: low" or seasonal temperature ranges for each destination.

#### NOAA ERDDAP
- **URL**: https://coastwatch.pfeg.noaa.gov/erddap/
- **License**: Public domain
- **Data**: SST, bathymetry (ETOPO), ocean currents, chlorophyll, salinity — hundreds of datasets.
- **Access**: RESTful OPeNDAP API. Outputs: JSON, CSV, NetCDF.
- **Value**: Environmental data layers for every destination — water temperature by month, current patterns, visibility proxies (chlorophyll). Makes our "Best Time to Visit" sections data-driven rather than guesswork.

#### MERMAID (Marine Ecological Research Management Aid)
- **URL**: https://datamermaid.org/
- **Data**: Coral reef survey data, fish/benthic transects, bleaching observations
- **Access**: Cloud API for data sharing
- **Value**: Standardized reef monitoring data from research sites — adds scientific credibility to reef health descriptions.

---

### Tier 2d: Dive Log & App Platforms

#### SSI MyDiveGuide
- **URL**: https://www.divessi.com/en/mydiveguide
- **Data**: **65,000+ dive sites** with GPS coordinates, wildlife lists, dive conditions
- **Access**: No public API — data locked in MySSI app. Would need partnership or reverse engineering.
- **Value**: The single largest dive site database. If access can be negotiated, it would be transformative.

#### Subsurface Dive Log (Open Source)
- **URL**: https://subsurface-divelog.org/ / https://github.com/subsurface/subsurface
- **License**: GPL (open source)
- **Data**: Dive site names, GPS coordinates, depths, temperature, dive profiles in XML format. Community-shared dive site directory.
- **Access**: XML export/import, companion website
- **Value**: Open source dive log with structured site data. XML format is easily parseable.

#### dive.io API
- **URL**: https://dive.io/api
- **Data**: Dive sites, dive logs
- **Access**: REST API with documentation
- **Value**: Additional cross-reference source for site data.

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

#### The Dive Atlas
- **URL**: https://thediveatlas.com/
- **Data**: Map-based dive site locations, community-contributed
- **Access**: Web scraping (no API)
- **Value**: Additional community pins for cross-referencing coordinates.

#### Open Dive Sites (ODS)
- **URL**: https://opendivesites.org/
- **Data**: Dive site descriptions, dive maps, community wiki
- **Access**: Wiki-style (no API)
- **Value**: Detailed for California coast; limited elsewhere but growing.

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

**Limitation**: ~1km resolution means shore dive sites very close to the coastline may incorrectly flag as "land." This is expected — shore dives are *supposed* to be near land. Lakes are also classified as "land."

### Layer 1b (Alternative): OSM Water Polygons — Highest Free Resolution

[OSM water polygons](https://osmdata.openstreetmap.de/data/water-polygons.html) are pre-built coastline shapefiles regenerated daily from OSM `natural=coastline` ways. Significantly higher resolution (~10-50m) than Natural Earth or global-land-mask.

```python
import geopandas as gpd
from shapely.geometry import Point

# Load OSM water polygons (download from osmdata.openstreetmap.de)
water = gpd.read_file("water-polygons-split-4326/water_polygons.shp")

# Build spatial index for fast batch queries
sindex = water.sindex

def is_in_water(lat, lon):
    point = Point(lon, lat)
    possible_matches = list(sindex.intersection(point.bounds))
    return any(water.iloc[i].geometry.contains(point) for i in possible_matches)
```

**Trade-off**: Larger file size than global-land-mask but much more accurate near coastlines. Best for the high-res recheck layer.

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

### Phase 1: Foundation (Site Discovery + Validation)
| Priority | Source | Why | Effort |
|---|---|---|---|
| 1 | OpenDeepMap | Open license, structured, closest to our schema | Low |
| 2 | Divestop (GitHub) | Direct JSON merge, open source | Low |
| 3 | The Dive API | 17,000+ sites, REST API, operator data | Medium |
| 4 | GEBCO + global-land-mask + OSM Water Polygons | Coordinate validation + depth verification | Medium |
| 5 | Divesites.com API | Weather/tide data for "Best Time" fields | Low-Medium |

### Phase 2: Enrichment (Species + Environment)
| Priority | Source | Why | Effort |
|---|---|---|---|
| 6 | GBIF (Diveboard + RLS) | Real species data, public domain, good API | Medium |
| 7 | FishBase / WoRMS | Species detail + taxonomic standardization | Medium |
| 8 | OBIS | Aggregated marine species occurrences | Medium |
| 9 | Allen Coral Atlas | 5m-resolution reef habitat classification | Medium |
| 10 | NOAA ERDDAP / Coral Reef Watch | SST, currents, bleaching risk | Medium |

### Phase 3: Deep Enrichment (Community + MPA)
| Priority | Source | Why | Effort |
|---|---|---|---|
| 11 | Diveboard API | Diver-reported conditions and species | Medium |
| 12 | WDPA / Protected Planet | Marine protected area annotations | Medium |
| 13 | REEF | Species frequency per named site | Medium-High |
| 14 | iNaturalist | Photo-verified recent sightings | Medium |
| 15 | Subsurface (open source) | Dive profiles, temperatures | Medium |

### Phase 4: Gap-Filling (Scraping + Partnerships)
| Priority | Source | Why | Effort |
|---|---|---|---|
| 16 | Wannadive / ScubaBoard / Dive Atlas | Community knowledge for gaps | High (scraping) |
| 17 | SSI MyDiveGuide | 65,000+ sites — largest single DB | High (partnership needed) |
| 18 | Dive operator websites | Most operationally accurate site data | High (per-operator) |

---

## Total Source Count: 30+ Data Sources

| Category | Sources | Combined Sites |
|---|---|---|
| Dive site databases (APIs) | 6 | ~20,000+ unique sites |
| Scientific marine databases | 5 | Species data for all sites |
| Reef & coral monitoring | 4 | Habitat + health data |
| Government (NOAA) | 3 | Environmental context |
| Marine protected areas | 1 | Regulatory annotations |
| Community/wiki sources | 4 | Gap-filling |
| Dive apps/platforms | 3 | 65,000+ (if SSI accessible) |
| Bathymetry/validation | 3 | Validation for all sites |
