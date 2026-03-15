# Validate Batch

Run site validation on a batch of destinations, with automatic commit and push after completion.

## Usage

```
/validate-batch next          # Run the next unprocessed batch
/validate-batch 3             # Run batch 3 specifically
/validate-batch status        # Show progress across all batches
/validate-batch remaining     # Run all remaining batches sequentially
```

## Batch Definitions

| Batch | Region / Theme | Destinations |
|-------|---------------|-------------|
| 1 | Specialty (wrecks, muck, pelagic) | chuuk-lagoon, silfra-fissure, lembeh-strait, galapagos-islands, socorro-islands, cocos-island, manado-bunaken, california-channel-islands, newfoundland, great-lakes, new-jersey, north-carolina, bermuda |
| 2 | Caribbean A | bahamas, cayman-islands, turks-and-caicos, cozumel, british-virgin-islands, utila, roatan, grenada, dominica, st-lucia, us-virgin-islands, tobago, aruba |
| 3 | Caribbean B | guadeloupe, barbados, dominican-republic, puerto-rico, jamaica, martinique, st-kitts-and-nevis, st-vincent-grenadines, sint-eustatius, antigua-and-barbuda, providencia-island, bocas-del-toro |
| 4 | Southeast Asia | raja-ampat, sipadan, komodo-national-park, thailand-similan-islands, bali, gili-islands, koh-tao, philippines-palawan, philippines-tubbataha-reefs, philippines-donsol, philippines-anilao, philippines-malapascua |
| 5 | Pacific & Indian Ocean | palau, fiji, french-polynesia, papua-new-guinea, solomon-islands, vanuatu, tonga, micronesia-yap, marshall-islands, okinawa, andaman-islands, sri-lanka, lombok, alor-archipelago, ambon, triton-bay |
| 6 | Europe & Middle East | malta-and-gozo, sardinia, croatia, greece, turkey, norway-lofoten-islands, azores, port-cros, ustica, svalbard, greenland, red-sea, jordan-aqaba, oman, uae-fujairah |
| 7 | Africa & Indian Ocean | mozambique, tanzania, south-africa, madagascar, zanzibar, kenya-coast, cape-town, djibouti, seychelles, mauritius, maldives, christmas-island, ningaloo-reef |
| 8 | Americas & Oceania | florida-keys, dry-tortugas, south-florida, flower-garden-banks, new-england, nova-scotia, great-barrier-reef, lord-howe-island, south-australia-neptune-islands, poor-knights-islands, alaska, puget-sound |
| 9 | West Coast, Hawaii & Final | monterey-bay, san-diego-la-jolla, vancouver-island, british-columbia, la-paz-sea-of-cortez, hawaii-big-island, hawaii-oahu, hawaii-kauai, hawaii-maui, coiba-national-park, curacao, bonaire, sudan-red-sea |

## Execution Flow

### For `status`

1. Read `logs/.validate_batch_state` to determine current batch number
2. For each batch (1-9), count validated vs total sites per destination using `data/osm_clean/{slug}.json`
3. Print a progress table showing: batch number, done/total destinations, and overall percentage

### For `next` or a specific batch number

1. **Determine batch**: Read `logs/.validate_batch_state` for `next`, or use the provided number
2. **Filter destinations**: For each slug in the batch, check `data/osm_clean/{slug}.json` — skip destinations where ALL sites already have `tags.validated = "true"`
3. **Dispatch parallel agents**: Launch up to 5 destination agents concurrently using `/validate-sites` logic:
   - Each agent: reads JSON, researches sites via Perplexity, updates JSON + markdown, runs sync_sites.py
   - Use `model: "sonnet"` for sub-agents
4. **Wait for agents to complete**, then dispatch the next group of 5 until the batch is done
5. **Commit all changes**:
   ```bash
   git add data/osm_clean/ divesites/
   git commit -m "Validate batch N: <slug-list>"
   ```
6. **Push to branch**:
   ```bash
   git push -u origin claude/dive-destinations-planning-5nbOI
   ```
7. **Update batch state**: Write `N+1` to `logs/.validate_batch_state`
8. **Print summary**: Show validation counts per destination

### For `remaining`

Run the above flow for each batch from the current state through batch 9, sequentially. Commit and push after each batch.

## Agent Task Template

Each per-destination agent should receive this task:

```
Research and validate all dive sites for [DESTINATION_NAME] ([SLUG]).

Files to update:
- data/osm_clean/{slug}.json — site_type, difficulty, depth, entry_type, validation tags
- divesites/{slug}/*.md — rewrite generic descriptions with researched content

Steps:
1. Read data/osm_clean/{slug}.json to get the full site list
2. Research the destination's overall diving character using perplexity_ask
3. For each site (batch of 5-10 for large destinations):
   a. Research: perplexity_ask "[site name] [destination] dive site type depth"
   b. Update site_type, depth, difficulty, entry_type in JSON
   c. Add tags: validated="true", validation_source="[source]"
   d. Read the corresponding markdown file
   e. Rewrite generic template text with site-specific researched content
4. Write updated JSON to data/osm_clean/{slug}.json
5. Run: python3 scripts/sync_sites.py {slug}
6. Return a summary of all changes made

Quality standard: See the hand-curated Bonaire/Curaçao files and validated Scapa Flow files.
Rules: Cold-water = min Intermediate. Remote liveaboard = min Advanced.
Do NOT mark a site validated unless you found a real source for it.
```

## Scheduling

This command is designed for use with `/loop` or manual invocation:

```
/loop 45m /validate-batch next
```

Or run all remaining batches:
```
/validate-batch remaining
```

## Important Notes

- Always commit and push after each batch — don't lose work if a later batch fails
- The branch is `claude/dive-destinations-planning-5nbOI`
- Each batch takes ~30-60 minutes depending on destination count and site count
- If a batch fails partway, re-running it will skip already-validated destinations
