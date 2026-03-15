# Quality Check Dive Site Data

Run comprehensive quality checks on all dive site data files to catch commercial businesses, contact info, data integrity issues, and coverage gaps.

## Usage

```
/quality-check [slug or "all"]
```

Examples:
- `/quality-check` — check all destinations
- `/quality-check martinique` — check a specific destination
- `/quality-check new` — check only recently added destinations

## Checks Performed

Run ALL of these checks. Report findings grouped by category.

### 1. Commercial Business Detection

Scan `data/osm_clean/*.json` and `data/external/osm_extended/*.json` for dive shops, schools, and operators.

**Check OSM tags:**
- `amenity` = `dive_centre` or `dive_center`
- `leisure` = `sports_centre` or `sports_center`
- `building` = `yes` (without `historic` tag)
- `shop` = any value
- `tourism` = `hotel`, `hostel`, `guest_house`, `resort`

**Check names in English, French, and Spanish:**
- English: dive center/centre/shop/school/store/academy, diving center/centre/school/college, scuba diving (standalone), PADI, SSI, NAUI, CMAS
- French: centre de plongée, club de plongée, école de plongée, [Name] Plongée (operator pattern)
- Spanish: centro de buceo, escuela de buceo, club de buceo, tienda de buceo
- Business suffixes: Ltd, LLC, Inc, S.A., GmbH

**Known false positives to IGNORE:**
- "Dive Site" or "Site de Plongée" in name
- Entries with `scuba_diving:divespot=yes`
- Famous dive site names that sound commercial (e.g., "Shark Hotel")

### 2. Contact Information & URLs

Scan all tag values for:
- Email addresses (`user@domain.com` pattern)
- URLs (`http://`, `https://`, `www.`)
- Social media references (facebook, instagram, twitter, tripadvisor, whatsapp)

Check these specific tag keys which should be stripped:
`website`, `phone`, `email`, `contact:*`, `url`, `fax`, `opening_hours`, `operator`, `addr:*`, `facebook`, `instagram`, `twitter`, `verified`, `image*`, `heritage:website`

Also check `source`, `source_ref`, `note` for embedded URLs.

### 3. Near-Duplicate Detection

Scan each destination for entries that are likely the same site entered twice (e.g., from overlapping gap-fill passes):
- **Exact case-insensitive matches**: Always duplicates
- **Substring matches with close coordinates** (<500m): e.g., "The Boiler" vs "The Boiler San Benedicto"
- **EXCLUDE from duplicate detection**: Numbered variants (1/2/3), directional pairs (North/South/East/West), named sub-sections (Hall/Cathedral/Lagoon/Plateau), and depth variants (Deep/Shallow)

When removing a duplicate, prefer keeping the entry with more metadata (depth, difficulty, entry_type). For names, prefer the established/shorter name over verbose variants.

### 4. Site Type & Difficulty Validation

Verify that `site_type` and `difficulty` accurately reflect each destination's diving character. Common misclassifications to catch:

**Site type research**: Do a brief web search for any destination where >90% of sites share the same `site_type`. Many destinations have a signature diving style that differs from the default "reef":
- **Muck diving**: Lembeh Strait — site_type should be `muck`, not `reef`
- **Wall diving**: Bunaken, Bonaire, Cayman — many sites should be `wall`
- **Pelagic/pinnacles**: Socorro, Galapagos, Cocos Island — `wall` (volcanic pinnacles), not `reef`
- **Kelp forest**: Monterey, Channel Islands, San Diego — `reef` is acceptable
- **Wreck diving**: New Jersey, Chuuk, Scapa Flow, Great Lakes — check wreck names are tagged `wreck`
- **Cold water**: Alaska, BC, Puget Sound, Nova Scotia, New England — verify difficulty is at least Intermediate

**Difficulty validation**:
- No "Beginner" at remote liveaboard-only destinations (Socorro, Cocos, etc.)
- Cold-water destinations should default to Intermediate minimum (drysuit required)
- All entries should have a difficulty set (not None)

### 5. Data Integrity

For every entry in every file:
- Has non-empty `name`
- Has valid `lat` (between -90 and 90)
- Has valid `lon` (between -180 and 180)
- No duplicate names within the same destination file
- Has `difficulty` set (not None)

### 6. Coverage Assessment

Report destinations with fewer than 8 sites — these need gap-filling with curated data.

### 7. Cross-Destination Duplicates

Check if the same `osm_id` appears in multiple destination files (legitimate if a site is near a boundary, but worth flagging).

## Output Format

```
=== COMMERCIAL BUSINESSES ===
[list any found, or "None found"]

=== CONTACT INFO / URLs ===
[list any found, or "None found"]

=== DATA INTEGRITY ===
[list any issues, or "All checks passed"]

=== COVERAGE ===
[list destinations with <8 sites]

=== SUMMARY ===
Files checked: X
Total sites: X
Issues found: X
Status: CLEAN / NEEDS ATTENTION
```

## Auto-Fix

After reporting, offer to automatically:
1. Remove identified commercial entries
2. Strip contact/URL tag fields
3. Report what was removed so user can verify
