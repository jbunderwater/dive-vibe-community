---
name: Tawasal
lat: -2.2579059
lng: 40.9093621
difficulty: Intermediate
maxDepth: 20
entryType: boat
siteType: wreck
ref: null
osmId: 666532608
addedBy: osm_import
---

## Tawasal

## DATA INTEGRITY NOTICE — GEOGRAPHIC MISMATCH: THIS SITE IS NOT IN TANZANIA

**This record's coordinates (-2.2579059, 40.9093621) do not belong in the Tanzania destination file and should not be treated as a validated Tanzania dive site.** They sit almost exactly on Manda Island / the Lamu Archipelago in Lamu County, **Kenya** — roughly 250 km north of Tanzania's northernmost coastal point near the Kenya border (around -4.6°S, Horohoro/Tanga). The underlying OpenStreetMap record itself (way id 666532608, `historic=wreck`) carries the description: **"A wreck of the dhow 'Tawasal,' formerly owned by the Tawasal Institute of Lamu, located on Manda Island in Lamu County, Kenya."** This is the object's own source description, not an inference from coordinates alone — it directly states Kenya. This appears to be a data-import error where a Kenyan wreck near the Lamu/Kiunga area was swept into the Tanzania dataset because the destination's bounding box in `destinations.json` extends far enough north (to cover Zanzibar/Pemba) that it also captured this unrelated Kenyan coordinate.

**Recommendation: remove this record from the Tanzania destination, or relocate it to a Kenya destination file if one exists or is created. Do not mark `validated="true"` for this record under the Tanzania destination, regardless of how well-documented the wreck itself turns out to be — the jurisdiction/location problem is disqualifying on its own.** The remainder of this page is retained only for the record of what could be found about the wreck itself, in case that research is useful if/when the site is relocated to the correct country file.

## What is known about the wreck itself

Research specifically targeting "Tawasal wreck," "Tawasal Lamu," "Tawasal Kenya dive," and "Tawasal dhow wreck" turned up no secondary sources (no ScubaBoard threads, dive-operator listings, or news coverage) describing this wreck. The only source found is OSM's own object description quoted above, which is a single, unverified, uncited claim — it does not meet the 2+ independent source bar this project requires for historical/vessel facts, so per the anti-hallucination policy no build date, tonnage, dimensions, or cause of sinking can be reported. What OSM's description gives us:

- It is a **dhow** (traditional East African/Arabian coastal sailing vessel), not a large cargo ship
- Name: **Tawasal**
- Reported former owner: "the Tawasal Institute of Lamu" (unverified elsewhere)
- Location: Manda Island, Lamu Archipelago, Lamu County, Kenya
- OSM tags mark it `wreck:visible_at_high_tide=yes` and `wreck:visible_at_low_tide=yes` (hull visible above water at all tide states) and `seamark:wreck:category=hull_visible`

General background (not Tawasal-specific, offered only as regional context): the Lamu Archipelago and adjoining Kiunga Marine National Reserve are a known area for historic dhow activity and reef/wreck diving, with Kiwayu, Manda Toto, and Pate islands cited as established dive/snorkel spots, though no source found ties Tawasal specifically into that operator ecosystem.

## Site Information (unverified, and out of scope for Tanzania regardless)

- **Location**: Manda Island, Lamu County, Kenya — not Tanzania
- **Site Type**: Wreck (dhow) — this part of the classification is consistent with the OSM description
- **Depth/difficulty/entry type/visibility/current**: No independent source found; carried over unverified from the existing dataset and not to be relied on

## Marine Life

No source confirms any marine life specific to this wreck. The previous version's claims (lionfish, batfish, moray eels, reef sharks) were generic wreck-diving boilerplate, not site-specific findings, and have been removed rather than replaced with new speculation. Per policy, wreck penetration is never to be described as "safe" regardless of location, and no penetration guidance is offered here.

---
*Sources: [OpenStreetMap way 666532608 — "Tawasal"](https://www.openstreetmap.org/way/666532608) (primary source for the Kenya/Manda Island identification). No independent secondary source corroborating the wreck's history was found; per the 2+ source rule for historical claims, no vessel history beyond the above is reported. Last updated 2026-07-05.*
