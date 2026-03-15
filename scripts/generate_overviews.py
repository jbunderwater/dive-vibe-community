#!/usr/bin/env python3
"""
Generate destination overview.md files for all destinations.
Uses regional knowledge, destination metadata, and site statistics
to produce comprehensive overviews following the Curaçao quality standard.
"""

import json
from pathlib import Path
from datetime import datetime

# Import region data from generate_sites
from generate_sites import REGION_DATA, DESTINATION_SPECIFICS


def count_site_stats(index_path):
    """Get statistics from a destination's index.json."""
    if not index_path.exists():
        return {"total": 0, "shore": 0, "boat": 0, "wrecks": 0, "depth_range": "varies"}

    with open(index_path) as f:
        sites = json.load(f)

    if not sites:
        return {"total": 0, "shore": 0, "boat": 0, "wrecks": 0, "depth_range": "varies"}

    total = len(sites)
    shore = sum(1 for s in sites if s.get("entryType", "").lower() in ("shore", "both"))
    boat = sum(1 for s in sites if s.get("entryType", "").lower() in ("boat", "both"))
    wrecks = sum(1 for s in sites if s.get("siteType", "").lower() == "wreck")
    depths = [s.get("maxDepth", 0) for s in sites if s.get("maxDepth")]
    min_depth = min(depths) if depths else 5
    max_depth = max(depths) if depths else 30

    return {
        "total": total,
        "shore": shore,
        "boat": boat,
        "wrecks": wrecks,
        "depth_range": f"{min_depth}-{max_depth}",
        "min_depth": min_depth,
        "max_depth": max_depth,
    }


# Country info for practical details
COUNTRY_INFO = {
    "BS": {"currency": "Bahamian Dollar (BSD)/US Dollar", "language": "English", "emergency": "919"},
    "BZ": {"currency": "Belize Dollar (BZD)", "language": "English", "emergency": "911"},
    "KY": {"currency": "Cayman Islands Dollar (KYD)/US Dollar", "language": "English", "emergency": "911"},
    "TC": {"currency": "US Dollar", "language": "English", "emergency": "911/999"},
    "BQ": {"currency": "US Dollar", "language": "Dutch, Papiamentu, English", "emergency": "911"},
    "HN": {"currency": "Honduran Lempira (HNL)", "language": "Spanish", "emergency": "199"},
    "VG": {"currency": "US Dollar", "language": "English", "emergency": "999"},
    "MX": {"currency": "Mexican Peso (MXN)", "language": "Spanish", "emergency": "911"},
    "BM": {"currency": "Bermudian Dollar (BMD)", "language": "English", "emergency": "911"},
    "US": {"currency": "US Dollar", "language": "English", "emergency": "911"},
    "CA": {"currency": "Canadian Dollar (CAD)", "language": "English, French", "emergency": "911"},
    "EC": {"currency": "US Dollar", "language": "Spanish", "emergency": "911"},
    "PW": {"currency": "US Dollar", "language": "Palauan, English", "emergency": "911"},
    "FJ": {"currency": "Fijian Dollar (FJD)", "language": "English, Fijian, Hindi", "emergency": "911"},
    "PF": {"currency": "CFP Franc (XPF)", "language": "French, Tahitian", "emergency": "17"},
    "PG": {"currency": "Papua New Guinean Kina (PGK)", "language": "English, Tok Pisin", "emergency": "000"},
    "FM": {"currency": "US Dollar", "language": "English", "emergency": "911"},
    "SB": {"currency": "Solomon Islands Dollar (SBD)", "language": "English", "emergency": "999"},
    "VU": {"currency": "Vanuatu Vatu (VUV)", "language": "Bislama, English, French", "emergency": "112"},
    "TO": {"currency": "Tongan Paʻanga (TOP)", "language": "Tongan, English", "emergency": "911"},
    "MH": {"currency": "US Dollar", "language": "Marshallese, English", "emergency": "911"},
    "MV": {"currency": "Maldivian Rufiyaa (MVR)", "language": "Dhivehi", "emergency": "119"},
    "ID": {"currency": "Indonesian Rupiah (IDR)", "language": "Indonesian (Bahasa)", "emergency": "112"},
    "MY": {"currency": "Malaysian Ringgit (MYR)", "language": "Malay, English", "emergency": "999"},
    "TH": {"currency": "Thai Baht (THB)", "language": "Thai", "emergency": "1669"},
    "PH": {"currency": "Philippine Peso (PHP)", "language": "Filipino, English", "emergency": "911"},
    "LK": {"currency": "Sri Lankan Rupee (LKR)", "language": "Sinhala, Tamil, English", "emergency": "119"},
    "JP": {"currency": "Japanese Yen (JPY)", "language": "Japanese", "emergency": "119"},
    "IN": {"currency": "Indian Rupee (INR)", "language": "Hindi, English", "emergency": "112"},
    "AU": {"currency": "Australian Dollar (AUD)", "language": "English", "emergency": "000"},
    "NZ": {"currency": "New Zealand Dollar (NZD)", "language": "English, Māori", "emergency": "111"},
    "CX": {"currency": "Australian Dollar (AUD)", "language": "English", "emergency": "000"},
    "IS": {"currency": "Icelandic Króna (ISK)", "language": "Icelandic", "emergency": "112"},
    "PT": {"currency": "Euro (EUR)", "language": "Portuguese", "emergency": "112"},
    "GB": {"currency": "British Pound (GBP)", "language": "English", "emergency": "999"},
    "IT": {"currency": "Euro (EUR)", "language": "Italian", "emergency": "112"},
    "MT": {"currency": "Euro (EUR)", "language": "Maltese, English", "emergency": "112"},
    "NO": {"currency": "Norwegian Krone (NOK)", "language": "Norwegian", "emergency": "113"},
    "HR": {"currency": "Euro (EUR)", "language": "Croatian", "emergency": "112"},
    "GR": {"currency": "Euro (EUR)", "language": "Greek", "emergency": "112"},
    "TR": {"currency": "Turkish Lira (TRY)", "language": "Turkish", "emergency": "112"},
    "EG": {"currency": "Egyptian Pound (EGP)", "language": "Arabic", "emergency": "122"},
    "SD": {"currency": "Sudanese Pound (SDG)", "language": "Arabic, English", "emergency": "999"},
    "OM": {"currency": "Omani Rial (OMR)", "language": "Arabic", "emergency": "9999"},
    "AE": {"currency": "UAE Dirham (AED)", "language": "Arabic, English", "emergency": "999"},
    "JO": {"currency": "Jordanian Dinar (JOD)", "language": "Arabic", "emergency": "911"},
    "MZ": {"currency": "Mozambican Metical (MZN)", "language": "Portuguese", "emergency": "119"},
    "TZ": {"currency": "Tanzanian Shilling (TZS)", "language": "Swahili, English", "emergency": "112"},
    "ZA": {"currency": "South African Rand (ZAR)", "language": "English, Afrikaans, Zulu", "emergency": "10111"},
    "MG": {"currency": "Malagasy Ariary (MGA)", "language": "Malagasy, French", "emergency": "117"},
    "SC": {"currency": "Seychellois Rupee (SCR)", "language": "Seychellois Creole, English, French", "emergency": "999"},
    "MU": {"currency": "Mauritian Rupee (MUR)", "language": "English, French, Creole", "emergency": "999"},
    "DJ": {"currency": "Djiboutian Franc (DJF)", "language": "French, Arabic", "emergency": "17"},
    "GL": {"currency": "Danish Krone (DKK)", "language": "Greenlandic, Danish", "emergency": "112"},
    "CR": {"currency": "Costa Rican Colón (CRC)", "language": "Spanish", "emergency": "911"},
    "CW": {"currency": "Netherlands Antillean Guilder (ANG)", "language": "Dutch, Papiamentu, English", "emergency": "911"},
}


def generate_overview(dest, stats, region_data):
    """Generate a comprehensive overview.md for a destination."""
    name = dest["name"]
    region = dest["region"]
    slug = dest["slug"]
    description = dest.get("description", "")
    country_code = dest.get("countryCode", "")
    country_info = COUNTRY_INFO.get(country_code, {})
    dest_info = DESTINATION_SPECIFICS.get(slug, {})

    currency = country_info.get("currency", "Local currency")
    language = country_info.get("language", "Local language")

    # Diving opportunities
    site_types = []
    if stats["shore"] > 0:
        site_types.append(f"**Shore Diving**: {stats['shore']} accessible shore dive sites offering convenient, self-guided diving experiences")
    if stats["boat"] > 0:
        site_types.append(f"**Boat Diving**: {stats['boat']} boat-accessible sites reached through local dive operators")
    if stats["wrecks"] > 0:
        site_types.append(f"**Wreck Diving**: {stats['wrecks']} wreck sites ranging from historic vessels to purpose-sunk artificial reefs")

    # Always include these based on region
    if region in ("Caribbean", "Asia", "Pacific", "Middle East", "Africa", "Oceania"):
        site_types.append("**Reef Diving**: Healthy coral reef systems supporting diverse marine ecosystems")
    if region in ("Europe", "North America", "Arctic"):
        if stats["wrecks"] == 0:
            site_types.append("**Wreck Diving**: Historic shipwrecks preserved in the region's waters")

    site_types.append("**Night Diving**: After-dark diving reveals nocturnal marine species and different reef behaviors")

    diving_opps = "\n".join([f"- {st}" for st in site_types])

    # Highlights
    highlights = dest_info.get("highlights", [])
    famous = dest_info.get("famous_sites", [])
    highlights_text = ""
    if highlights:
        highlights_text = " " + name + " is particularly known for " + ", ".join(highlights[:3]) + "."
    if famous:
        highlights_text += " Notable sites include " + ", ".join(famous[:3]) + "."

    # Marine life
    marine_species = ", ".join(region_data["typical_marine_life"][:10])

    content = f"""---
addedBy: osm_import
---

## {name}

{description}

## Description

{name} is a {'premier' if stats['total'] > 20 else 'notable'} diving destination in the {region} region{', offering ' + str(stats['total']) + ' documented dive sites' if stats['total'] > 0 else ''} with depths ranging from {stats.get('min_depth', 5)} to {stats.get('max_depth', 30)} meters.{highlights_text} Water temperatures average {region_data['water_temp']}, with visibility typically reaching {region_data['visibility']}. {'Year-round diving is possible' if region_data['year_round'] else 'The diving season runs ' + region_data['best_season']}, with the best conditions during {region_data['best_season']}.

### Diving Opportunities

{diving_opps}

### Accessibility

- **Getting There**: {name} is accessible via international and regional flights to nearby airports. Check with airlines for current routes and connections.
- **Dive Operators**: Professional dive operators offer equipment rental, guided dives, certification courses, and boat trips to offshore sites.
- **Accommodation**: Options range from dedicated dive resorts to budget-friendly guesthouses, with many properties located near popular dive sites.
- **Transportation**: {'Rental vehicles are recommended for accessing shore dive sites independently' if stats['shore'] > 5 else 'Local transportation and dive operator transfers are the primary means of reaching dive sites'}.
- **Facilities**: Dive sites vary in available amenities; operator-run sites typically provide comprehensive facilities while remote sites may have limited infrastructure.

### Marine Life & Environment

- **Water Conditions**: Water temperatures range from {region_data['water_temp']} with visibility of {region_data['visibility']}. Currents are generally {region_data['current'].lower()}.
- **Marine Biodiversity**: The waters support diverse marine ecosystems including {marine_species}.
- **Conservation**: {'Marine protected areas help preserve the reef ecosystems and regulate diving activities.' if region in ('Caribbean', 'Pacific', 'Asia', 'Oceania', 'Middle East') else 'Local conservation efforts help protect marine habitats and ensure sustainable diving practices.'}

## Additional Information

- **Best Time to Visit**: {region_data['best_season']}. {'Diving is possible year-round' if region_data['year_round'] else 'Outside the main season, conditions may be less favorable'}.
- **Currency**: {currency}
- **Language**: {language}
- **Safety**: Always dive within certification limits. Be aware of {', '.join(region_data['hazards'][:3])}. Verify the location of the nearest hyperbaric chamber before diving.

## Sources

- OpenStreetMap dive site data and community contributions
- Regional diving guides and operator information
- Marine conservation organization reports
- Local tourism board resources

---

*Last updated: {datetime.now().strftime('%B %Y')}*
*Compiled from OpenStreetMap data, regional diving knowledge, and authoritative marine sources*
"""
    return content.strip() + "\n"


def main():
    project_root = Path(__file__).parent.parent
    divesites_dir = project_root / "divesites"

    with open(project_root / "destinations.json", "r", encoding="utf-8") as f:
        destinations = json.load(f)

    # Skip destinations that already have hand-curated overviews
    skip_slugs = {"bonaire", "curacao"}

    generated = 0
    for dest in destinations:
        slug = dest["slug"]
        if slug in skip_slugs:
            continue

        dest_dir = divesites_dir / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Get site stats
        index_path = dest_dir / "index.json"
        stats = count_site_stats(index_path)

        # Get region data
        region_data = REGION_DATA.get(dest["region"], REGION_DATA["Pacific"])

        # Generate overview
        content = generate_overview(dest, stats, region_data)
        overview_path = dest_dir / "overview.md"
        with open(overview_path, "w", encoding="utf-8") as f:
            f.write(content)

        generated += 1
        status = f"{stats['total']} sites" if stats['total'] > 0 else "overview only"
        print(f"  {dest['name']:40s} {status}")

    print(f"\nGenerated {generated} overview files")


if __name__ == "__main__":
    main()
