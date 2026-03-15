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

### 3. Data Integrity

For every entry in every file:
- Has non-empty `name`
- Has valid `lat` (between -90 and 90)
- Has valid `lon` (between -180 and 180)
- No duplicate names within the same destination file

### 4. Coverage Assessment

Report destinations with fewer than 8 sites — these need gap-filling with curated data.

### 5. Cross-Destination Duplicates

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
