# Validate Dive Sites

Research and validate dive sites within a destination using web sources (ScubaBoard, dive operators, Perplexity). Updates **both** the osm_clean JSON data **and** the markdown site descriptions to reflect accurate, site-specific information.

## Usage

```
/validate-sites <slug> [--all-reefs]
```

Examples:
- `/validate-sites bonaire` — validate all sites in Bonaire
- `/validate-sites raja-ampat --all-reefs` — only validate sites currently tagged as "reef"
- `/validate-sites all --all-reefs` — validate all reef-tagged sites globally (long-running)

## Why This Matters

1. **Wrong site types**: The Overpass scraper defaults `site_type=reef` for any site without explicit tags. Many wall dives, muck sites, and drift dives are mislabeled.
2. **Generic descriptions**: Template-generated markdown files have filler text like "rewarding diving on healthy coral reef structures" that doesn't describe the actual site. A wall dive shouldn't mention "reef structures". A famous wreck shouldn't have generic text when there's rich history to tell.

## Research Strategy

### Tools Available

- **Perplexity MCP** (`perplexity_search`, `perplexity_ask`, `perplexity_research`): Best for detailed site research. Use `perplexity_ask` for individual site queries and `perplexity_research` for destination-level overviews.
- **WebSearch**: Built-in web search for quick lookups
- **WebFetch**: Fetch and analyze specific URLs (ScubaBoard threads, operator sites)

### Priority Sources

1. **ScubaBoard forums** (scubaboard.com) — largest scuba diving forum. Search for site reports and dive logs.
2. **Dive operator sites** — local operators have the best site-by-site descriptions
3. **DiveAdvisor / Wannadive / PADI Travel** — structured dive site databases
4. **Wikipedia / Wikidata** — for wrecks, marine parks, and well-documented sites

### What to Research Per Site

For each site, gather as much of this as possible:

1. **site_type** — Underwater topography:
   - `reef` — Coral reef, coral garden, coral bommie
   - `wall` — Vertical drop-off, wall dive
   - `wreck` — Shipwreck, plane wreck, artificial reef (sunken structure)
   - `cave` — Cave, cavern, swim-through, lava tube, cenote, grotto
   - `muck` — Muck/sand diving, critter hunting on volcanic sand
   - `beach` — Sandy bottom, seagrass, beach entry point
   - `drift` — Primarily a drift dive (channel, pass, current-swept)
   - `pinnacle` — Submerged rock/coral pinnacle or seamount

2. **depth** — Maximum depth in meters

3. **difficulty** — Based on conditions:
   - `Beginner` — Calm, shallow (<18m), no current, easy entry
   - `Intermediate` — Moderate depth (18-30m), mild current
   - `Advanced` — Deep (>30m), strong current, cold water, or remote/technical

4. **entry_type** — `shore`, `boat`, or `both`

5. **Description details** for the markdown file:
   - What makes this specific site unique? (not generic "healthy coral reef")
   - What's the actual underwater landscape? (chimney entry, wall descent, swim-throughs, etc.)
   - What marine life is actually seen here? (not regional lists)
   - What's the typical dive profile? (real depths, navigation, key landmarks)
   - What should divers know about entry/exit? (specific conditions, landmarks)
   - Any history? (wreck stories, naming origin, significance)

### Research Process (Per Destination)

1. **Destination-level research first**: Search for the overall diving character.
   - `"[destination] diving" site:scubaboard.com`
   - `"[destination] dive sites" types wall reef wreck`
   - This tells you what the area is known for before examining individual sites.

2. **Research sites in batches of 5-10**: For each batch:
   - Search: `"[site name]" "[destination]" dive`
   - Look for: wall, drop-off, pinnacle, wreck, cave, cavern, muck, drift, channel, pass, current
   - Read forum threads and operator descriptions for site-specific details

3. **Update osm_clean JSON** with corrected fields and validation tags

4. **Update markdown files** — For each site where you found real information:
   - Read the current markdown file at `divesites/{slug}/{site-filename}.md`
   - Compare the description against your research findings
   - Rewrite sections that are generic/inaccurate with site-specific content
   - Keep the existing section structure (Overview, Site Information, Marine Life, etc.)

5. **Run sync_sites.py** to propagate frontmatter and Site Information fields:
   ```bash
   python3 scripts/sync_sites.py <slug>
   ```

### How to Update Markdown Descriptions

The quality standard is the hand-curated Bonaire/Curaçao files. Compare:

**BAD (template-generated):**
> The Bells is a reef dive site in Red Sea, Middle East.
> The Bells is a dive site in Red Sea offering rewarding diving on healthy coral reef structures.

**GOOD (research-informed):**
> The Bells is one of Dahab's most famous wall dives, named for the bell-shaped chimney entrance.
> Divers enter through a narrow vertical chimney that drops from 6m to 27m, emerging onto a dramatic wall that extends to the Blue Hole. The site features stunning hard coral growth on the wall face, with frequent sightings of Napoleon wrasse and barracuda in the blue.

When updating markdown, follow these rules:

- **Rewrite the one-liner** (line after `## Site Name`): Replace generic "X is a reef dive site in Y" with a specific sentence about what makes this site notable.
- **Rewrite the Overview**: Replace template filler with research-based description. Include what divers actually experience, specific features, and why the site matters.
- **Update Marine Life**: Replace regional species lists with site-specific observations. What do divers actually report seeing here?
- **Update Dive Profile**: Replace generic depth advice with the actual dive plan — entry point, typical route, key depths, turnaround point.
- **Update Entry and Exit**: Replace generic instructions with specific ones if known.
- **Update Tips**: Replace generic tips with site-specific advice.
- **Preserve what's good**: If a section already has accurate, specific content, keep it.
- **Don't fabricate**: Only write what your research supports. If you can't find specific marine life info for a site, keep the regional defaults rather than making things up.
- **Match existing tone**: Write like the Bonaire files — informative, specific, conversational but professional. No marketing language.

### Validation Rules

- Do NOT change a site_type unless you have a source confirming the correct type
- If a site has multiple characteristics (e.g., a wall with a wreck at the base), use the PRIMARY type
- If no information is found for a specific site, leave type as-is but do NOT mark it validated
- Wrecks should ALWAYS be tagged `wreck` regardless of what they sit on
- "Coral garden" = reef, "drop-off" = wall, "cleaning station" = reef, "channel/pass" = drift
- Pinnacles and seamounts = `pinnacle` if available, otherwise `wall`

### Batch Processing

For large destinations (50+ sites), process in batches:
1. First pass: reclassify obvious cases by name keywords
2. Second pass: web research remaining "reef" sites in groups of 5-10, updating both JSON and markdown
3. Final pass: spot-check a sample of validated sites

### Output

After validation, print a summary:
```
=== VALIDATION RESULTS: [destination] ===
Sites validated: X / Y
JSON changes:
  reef -> wall: N sites
  reef -> wreck: N sites
  reef -> cave: N sites
  reef -> drift: N sites
  reef -> muck: N sites
  difficulty updated: N sites
Markdown descriptions updated: N sites
Unresolved (no source found): N sites
```

## Important Notes

- This is a SLOW process due to web searches. Plan for ~2-3 minutes per destination.
- Focus on destinations with >80% reef tags first — most likely to have misclassifications.
- For destinations that genuinely ARE reef diving (e.g., Great Barrier Reef), a high reef percentage is correct. Confirm at the destination level first.
- Always cite your source — note it in the validation_source tag.
- After ALL changes (both JSON and markdown), run `python3 scripts/sync_sites.py <slug>` to ensure frontmatter stays consistent.
