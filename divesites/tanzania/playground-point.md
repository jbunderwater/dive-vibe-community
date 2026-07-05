---
name: Playground Point
lat: -11.6052707
lng: 34.3031882
difficulty: Intermediate
maxDepth: 22
entryType: boat
siteType: reef
ref: null
osmId: 10224564251
addedBy: osm_import
---

## Playground Point

**DATA INTEGRITY FLAG: This entry does not appear to belong in the Tanzania Indian Ocean destination.** Research strongly indicates this point is a freshwater Lake Malawi dive site near Nkhata Bay, Malawi — not a Zanzibar/coastal Tanzania coral reef, and not in Tanzanian territory.

## Overview

Cross-referencing the underlying OpenStreetMap node (id 10224564251) shows it was created on 2022-11-28 by OSM contributor "Fredo1632" in changeset 129495172, titled **"Tauchplätze Malawisee Nkhatabay"** (German for "Dive sites, Lake Malawi, Nkhata Bay"). The only tags on the raw node are `name=Playground Point` and `natural=reef` — there is no depth, difficulty, or entry-type tag in the source data; those fields in this project's dataset appear to be pipeline defaults, not sourced facts.

A reverse-geocode of the coordinates (-11.6052707, 34.3031882) against OpenStreetMap's own administrative boundaries places the point inside **Malawi** (admin boundary relation for Malawi, country_code `mw`), roughly 12-14 km north of the town of Nkhata Bay on Lake Malawi's northern shore — nowhere near Tanzania's Indian Ocean coast (which sits ~600 km east) and nowhere near the actual disputed Tanzania/Malawi lake-border zone further north. This is not a border-ambiguity case; the coordinates sit well inside undisputed Malawian territory.

No web source (dive shop, ScubaBoard, PADI, or Lake Malawi tourism site) uses the name "Playground Point" for any specific site, so beyond confirming it is very likely a Lake Malawi rocky-reef point near Nkhata Bay, no site-specific depth, visibility, or marine life claims can be verified. The previous "Marine Life," "Dive Profile," and "Photography" content in this file's earlier version (citing generic Tanzania coral-reef roundup articles as sources) was fabricated — those sources never mention Lake Malawi or this site, and have been removed.

## Site Information

- **Location**: Coordinates fall within Malawi, near Nkhata Bay on Lake Malawi's northern shore — not Tanzania.
- **Entry Type**: Unconfirmed (dataset default "boat", not sourced from OSM tags or a dive shop listing)
- **Site Type**: Unconfirmed. OSM tags it `natural=reef`; the OSM changeset comment describes it as a "dive site" on Lake Malawi, implying a freshwater rocky reef rather than a coral reef.
- **Difficulty Level**: Unconfirmed (dataset default, not sourced)
- **Maximum Depth**: Unconfirmed (22m in this dataset is not present in the source OSM tags)

## Marine Life

No site-specific source found. Do not infer species — Nkhata Bay-area Lake Malawi sites in general are known for endemic mbuna cichlids, but attributing specific species to this exact, otherwise-undocumented point would be fabrication.

## Recommendation

This site should be removed from the Tanzania destination (or migrated to a Malawi/Lake Nyasa destination file if one is created), not validated as a Tanzanian dive site. Confidence: high that it is mislocated; the German-language OSM changeset comment naming Lake Malawi and Nkhata Bay, combined with OSM's own boundary data placing the point in Malawi, leaves little ambiguity.

---
*No site-specific source found beyond the originating OpenStreetMap node/changeset metadata (openstreetmap.org). Geographic placement cross-checked against OpenStreetMap Nominatim reverse geocoding. This entry is flagged as likely out of scope for a Tanzania Indian Ocean destination — needs maintainer review of destinations.json bounds and possible removal. Last updated 2026-07-05.*
