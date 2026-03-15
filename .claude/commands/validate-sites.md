# Validate Dive Sites

Research and validate individual dive sites within a destination using web sources (especially dive forums like ScubaBoard). Updates site_type, difficulty, depth, and entry_type based on real diver reports.

## Usage

```
/validate-sites <slug> [--all-reefs]
```

Examples:
- `/validate-sites bonaire` — validate all sites in Bonaire
- `/validate-sites raja-ampat --all-reefs` — only validate sites currently tagged as "reef"
- `/validate-sites all --all-reefs` — validate all reef-tagged sites globally (long-running)

## Why This Matters

The Overpass scraper defaults `site_type=reef` for any site without explicit wreck/cave/beach/wall tags. This means ~71% of all sites are tagged "reef" — many incorrectly. A wall dive, a muck dive, a drift over a pinnacle, and a kelp forest dive all get the same generic label.

## Research Strategy

### Priority Sources

1. **ScubaBoard forums** (scubaboard.com) — the largest scuba diving forum. Search for destination-specific threads, site reports, and dive logs. Example searches:
   - `site:scubaboard.com "site name" dive`
   - `site:scubaboard.com "destination name" dive sites`

2. **Dive operator sites** — local dive shops often have the best site-by-site descriptions with depth, type, and conditions

3. **DiveAdvisor / Wannadive / PADI Travel** — structured dive site databases

4. **Wikipedia / Wikidata** — for wrecks, marine parks, and well-documented sites

### What to Look For

For each site, determine:

1. **site_type** — What is the underwater topography?
   - `reef` — Coral reef, coral garden, coral bommie
   - `wall` — Vertical drop-off, wall dive, volcanic pinnacle, seamount
   - `wreck` — Shipwreck, plane wreck, artificial reef (sunken structure)
   - `cave` — Cave, cavern, swim-through, lava tube, cenote, grotto
   - `muck` — Muck/sand diving, critter hunting on volcanic sand
   - `beach` — Sandy bottom, seagrass, beach entry point
   - `drift` — Primarily a drift dive (channel, pass, current-swept)
   - `pinnacle` — Submerged rock/coral pinnacle or seamount

2. **depth** — Maximum depth in meters (from dive reports)

3. **difficulty** — Based on conditions described:
   - `Beginner` — Calm, shallow (<18m), no current, easy entry
   - `Intermediate` — Moderate depth (18-30m), mild current, some experience needed
   - `Advanced` — Deep (>30m), strong current, cold water, or remote/technical

4. **entry_type** — `shore`, `boat`, or both

### Research Process (Per Destination)

1. **Start with a destination-level search** to understand the overall diving character:
   - Web search: `"[destination] diving" site:scubaboard.com`
   - Web search: `"[destination] dive sites" types wall reef wreck`

2. **For sites currently tagged "reef"**, search individually:
   - Web search: `"[site name]" "[destination]" dive`
   - Look for keywords: wall, drop-off, pinnacle, wreck, cave, cavern, muck, drift, channel, pass, current

3. **Batch similar sites** — if a forum thread describes multiple sites at once, extract info for all of them

4. **Update the data** with corrections, setting tags to track the source:
   ```json
   {
     "site_type": "wall",
     "tags": {
       "validated": "true",
       "validation_source": "scubaboard"
     }
   }
   ```

### Validation Rules

- Do NOT change a site_type unless you have a source confirming the correct type
- If a site has multiple characteristics (e.g., a wall with a wreck at the base), use the PRIMARY type
- If no information is found for a specific site, leave it as-is but do NOT mark it validated
- Wrecks should ALWAYS be tagged `wreck` regardless of what they sit on
- "Coral garden" = reef, "drop-off" = wall, "cleaning station" = reef, "channel/pass" = drift
- Pinnacles and seamounts = `wall` (closest match in our schema)

### Batch Processing

For large destinations (50+ sites), process in batches:
1. First pass: reclassify obvious cases by name keywords (wall, wreck, cave, pinnacle, channel, pass, drift, muck)
2. Second pass: web research the remaining "reef" sites in groups of 5-10
3. Final pass: spot-check a sample of validated sites

### Output

After validation, print a summary:
```
=== VALIDATION RESULTS: [destination] ===
Sites validated: X / Y
Changes made:
  reef -> wall: N sites
  reef -> wreck: N sites
  reef -> cave: N sites
  reef -> drift: N sites
  reef -> muck: N sites
  difficulty updated: N sites
  depth added: N sites
Unresolved (no source found): N sites
```

## Important Notes

- This is a SLOW process due to web searches. Plan for ~1-2 minutes per destination.
- Focus on destinations with >80% reef tags first — these are most likely to have misclassifications.
- For destinations that genuinely ARE reef diving (e.g., Great Barrier Reef, Ningaloo), a high reef percentage is correct. Use the destination-level search to confirm before changing individual sites.
- Always cite your source — if ScubaBoard says it's a wall dive, note that in the validation_source tag.
