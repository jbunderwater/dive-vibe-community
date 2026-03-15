#!/usr/bin/env python3
"""
Generate dive site markdown files and index.json for all destinations
using OSM data as the structured foundation. Produces destination-specific,
high-quality content following the Curaçao quality standard.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime

# Regional knowledge database for generating accurate, specific content
REGION_DATA = {
    "Caribbean": {
        "water_temp": "26-29°C (79-84°F)",
        "visibility": "20-40 meters (65-130 feet)",
        "best_season": "December to April (dry season)",
        "year_round": True,
        "typical_marine_life": [
            "sea turtles (green, hawksbill)", "southern stingrays", "eagle rays",
            "nurse sharks", "reef sharks", "barracuda", "parrotfish", "angelfish",
            "blue tangs", "trumpetfish", "moray eels", "lobsters",
            "brain corals", "elkhorn corals", "sea fans", "barrel sponges"
        ],
        "wreck_marine_life": ["groupers", "snappers", "soldierfish", "glassy sweepers", "coral growth", "sponge encrustation"],
        "hazards": ["boat traffic", "fire coral", "sea urchins", "occasional strong currents"],
        "current": "Light to moderate",
    },
    "Atlantic": {
        "water_temp": "20-28°C (68-82°F)",
        "visibility": "15-30 meters (50-100 feet)",
        "best_season": "May to October",
        "year_round": True,
        "typical_marine_life": [
            "sea turtles", "reef sharks", "groupers", "snappers",
            "parrotfish", "angelfish", "moray eels", "lobsters",
            "brain corals", "sea fans", "barrel sponges"
        ],
        "wreck_marine_life": ["groupers", "snappers", "barracuda", "coral encrustation"],
        "hazards": ["boat traffic", "currents", "occasional swells"],
        "current": "Light to moderate",
    },
    "North America": {
        "water_temp": "7-24°C (45-75°F)",
        "visibility": "5-25 meters (15-80 feet)",
        "best_season": "June to October",
        "year_round": False,
        "typical_marine_life": [
            "sea lions", "harbor seals", "garibaldi", "sheephead",
            "kelp bass", "giant sea bass", "bat rays", "horn sharks",
            "giant kelp", "sea urchins", "anemones", "nudibranchs"
        ],
        "wreck_marine_life": ["lingcod", "rockfish", "cabezon", "wolf eels"],
        "hazards": ["cold water", "surge", "limited visibility", "boat traffic", "currents"],
        "current": "Variable, can be strong",
    },
    "South America": {
        "water_temp": "15-26°C (59-79°F)",
        "visibility": "10-25 meters (30-80 feet)",
        "best_season": "June to November",
        "year_round": False,
        "typical_marine_life": [
            "hammerhead sharks", "whale sharks", "sea lions",
            "marine iguanas", "manta rays", "eagle rays",
            "sea turtles", "dolphins", "penguins", "moray eels"
        ],
        "wreck_marine_life": ["groupers", "snappers", "barracuda"],
        "hazards": ["strong currents", "cold thermoclines", "surge", "remote locations"],
        "current": "Moderate to strong",
    },
    "Pacific": {
        "water_temp": "24-30°C (75-86°F)",
        "visibility": "20-50 meters (65-160 feet)",
        "best_season": "April to November",
        "year_round": True,
        "typical_marine_life": [
            "manta rays", "reef sharks (grey, whitetip, blacktip)", "hammerhead sharks",
            "sea turtles", "napoleon wrasse", "barracuda", "tuna",
            "clownfish", "butterflyfish", "groupers", "moray eels",
            "hard corals", "soft corals", "sea fans", "giant clams"
        ],
        "wreck_marine_life": ["coral growth", "anemones", "lionfish", "scorpionfish", "glassy sweepers"],
        "hazards": ["strong currents", "remote locations", "jellyfish", "boat traffic"],
        "current": "Moderate to strong",
    },
    "Asia": {
        "water_temp": "26-30°C (79-86°F)",
        "visibility": "10-40 meters (30-130 feet)",
        "best_season": "October to April (varies by location)",
        "year_round": True,
        "typical_marine_life": [
            "manta rays", "whale sharks", "reef sharks", "sea turtles",
            "barracuda", "trevally", "napoleon wrasse", "clownfish",
            "nudibranchs", "frogfish", "seahorses", "pygmy seahorses",
            "hard corals", "soft corals", "sea fans", "sponges"
        ],
        "wreck_marine_life": ["batfish", "lionfish", "sweetlips", "coral growth", "soft corals"],
        "hazards": ["strong currents", "jellyfish", "sea urchins", "lionfish stings"],
        "current": "Variable, can be very strong",
    },
    "Oceania": {
        "water_temp": "20-29°C (68-84°F)",
        "visibility": "15-40 meters (50-130 feet)",
        "best_season": "September to February",
        "year_round": True,
        "typical_marine_life": [
            "great white sharks", "grey nurse sharks", "whale sharks",
            "manta rays", "sea turtles", "dolphins", "dugongs",
            "potato cod", "maori wrasse", "giant trevally",
            "hard corals", "soft corals", "sea fans", "giant clams"
        ],
        "wreck_marine_life": ["wobbegong sharks", "groupers", "coral growth"],
        "hazards": ["strong currents", "jellyfish (box jellyfish in summer)", "crocodiles (north)", "boat traffic"],
        "current": "Variable",
    },
    "Europe": {
        "water_temp": "10-25°C (50-77°F)",
        "visibility": "10-40 meters (30-130 feet)",
        "best_season": "May to October",
        "year_round": False,
        "typical_marine_life": [
            "groupers", "moray eels", "octopus", "barracuda",
            "sea bream", "amberjack", "nudibranchs", "seahorses",
            "posidonia seagrass", "red coral", "sea fans", "sponges"
        ],
        "wreck_marine_life": ["conger eels", "lobsters", "crabs", "anemones", "coral encrustation"],
        "hazards": ["cold water (north)", "currents", "boat traffic", "fishing nets"],
        "current": "Light to moderate",
    },
    "Middle East": {
        "water_temp": "22-30°C (72-86°F)",
        "visibility": "20-40 meters (65-130 feet)",
        "best_season": "September to May",
        "year_round": True,
        "typical_marine_life": [
            "whale sharks", "manta rays", "hammerhead sharks", "oceanic whitetip sharks",
            "sea turtles", "dolphins", "napoleon wrasse", "giant moray eels",
            "lionfish", "clownfish", "butterflyfish", "anthias",
            "hard corals", "soft corals", "sea fans", "fire coral"
        ],
        "wreck_marine_life": ["glassy sweepers", "lionfish", "groupers", "coral growth", "soft corals"],
        "hazards": ["strong currents", "fire coral", "lionfish stings", "boat traffic", "extreme heat"],
        "current": "Moderate to strong",
    },
    "Africa": {
        "water_temp": "20-29°C (68-84°F)",
        "visibility": "10-30 meters (30-100 feet)",
        "best_season": "October to March (East Africa), varies by location",
        "year_round": True,
        "typical_marine_life": [
            "whale sharks", "manta rays", "humpback whales",
            "sea turtles", "dolphins", "reef sharks",
            "potato bass", "giant trevally", "kingfish",
            "hard corals", "soft corals", "sea fans"
        ],
        "wreck_marine_life": ["groupers", "batfish", "coral growth", "lionfish"],
        "hazards": ["strong currents", "jellyfish", "remote locations", "limited medical facilities"],
        "current": "Moderate to strong",
    },
    "Arctic": {
        "water_temp": "-1 to 8°C (30-46°F)",
        "visibility": "10-30 meters (30-100 feet)",
        "best_season": "June to September",
        "year_round": False,
        "typical_marine_life": [
            "seals (harbor, bearded, ringed)", "walruses",
            "beluga whales", "narwhals", "polar cod",
            "sea anemones", "soft corals", "kelp forests",
            "sea urchins", "starfish", "crabs"
        ],
        "wreck_marine_life": ["kelp growth", "anemones", "crabs"],
        "hazards": ["extreme cold", "hypothermia risk", "ice", "limited visibility", "remote locations", "polar bears (Svalbard)"],
        "current": "Variable, tidal currents",
    },
}

# Destination-specific knowledge for enhanced content
DESTINATION_SPECIFICS = {
    "bahamas": {"highlights": ["blue holes", "shark dives at Tiger Beach", "shallow reef systems"], "famous_sites": ["Dean's Blue Hole", "Tiger Beach", "Thunderball Grotto"]},
    "belize-barrier-reef": {"highlights": ["Great Blue Hole", "Belize Barrier Reef (UNESCO)", "wall dives"], "famous_sites": ["Great Blue Hole", "Half Moon Caye Wall", "Hol Chan Marine Reserve"]},
    "cayman-islands": {"highlights": ["Stingray City", "wall diving", "excellent visibility"], "famous_sites": ["Stingray City", "Bloody Bay Wall", "USS Kittiwake"]},
    "cozumel": {"highlights": ["drift diving", "Palancar Reef system", "crystal-clear visibility"], "famous_sites": ["Palancar Reef", "Santa Rosa Wall", "Columbia Reef"]},
    "red-sea": {"highlights": ["pristine coral reefs", "WWII wrecks", "big pelagic encounters"], "famous_sites": ["SS Thistlegorm", "Ras Mohammed", "Brothers Islands", "Elphinstone Reef"]},
    "maldives": {"highlights": ["manta ray cleaning stations", "whale shark encounters", "channel dives"], "famous_sites": ["Manta Point", "Fish Head", "Banana Reef"]},
    "raja-ampat": {"highlights": ["highest marine biodiversity on earth", "pristine reefs", "manta rays"], "famous_sites": ["Cape Kri", "Manta Sandy", "Blue Magic"]},
    "great-barrier-reef": {"highlights": ["world's largest coral reef system", "incredible biodiversity", "liveaboard diving"], "famous_sites": ["Cod Hole", "Ribbon Reefs", "SS Yongala"]},
    "palau": {"highlights": ["Blue Corner drift dive", "WWII wrecks", "shark encounters"], "famous_sites": ["Blue Corner", "German Channel", "Jellyfish Lake"]},
    "galapagos-islands": {"highlights": ["hammerhead schools", "marine iguanas", "whale sharks"], "famous_sites": ["Gordon Rocks", "Wolf Island", "Darwin's Arch"]},
    "malta-and-gozo": {"highlights": ["cavern and cave diving", "historic wrecks", "Blue Hole"], "famous_sites": ["Blue Hole (Gozo)", "HMS Maori", "Um El Faroud"]},
    "scapa-flow": {"highlights": ["WWI German High Seas Fleet wrecks", "historic diving"], "famous_sites": ["SMS Karlsruhe", "SMS König", "SMS Markgraf"]},
    "croatia": {"highlights": ["Adriatic wrecks", "underwater caves", "crystal-clear waters"], "famous_sites": ["Baron Gautsch", "Vis Island wrecks", "Blue Cave"]},
    "gili-islands": {"highlights": ["turtle encounters", "easy shore diving", "coral gardens"], "famous_sites": ["Shark Point", "Turtle Heaven", "Manta Point"]},
    "bali": {"highlights": ["USAT Liberty wreck", "mola mola encounters", "manta rays at Nusa Penida"], "famous_sites": ["USAT Liberty", "Crystal Bay", "Manta Point"]},
    "komodo-national-park": {"highlights": ["manta ray cleaning stations", "strong current diving", "incredible biodiversity"], "famous_sites": ["Batu Bolong", "Castle Rock", "Manta Alley"]},
    "koh-tao": {"highlights": ["affordable diving", "beginner-friendly", "whale shark sightings"], "famous_sites": ["Chumphon Pinnacle", "Sail Rock", "Southwest Pinnacle"]},
    "french-polynesia": {"highlights": ["shark walls", "drift diving through passes", "humpback whales"], "famous_sites": ["Tiputa Pass", "Avatoru Pass", "The Wall of Sharks"]},
    "chuuk-lagoon": {"highlights": ["world's greatest wreck diving", "WWII Ghost Fleet", "Japanese naval vessels"], "famous_sites": ["Fujikawa Maru", "Shinkoku Maru", "San Francisco Maru"]},
    "florida-keys": {"highlights": ["coral reefs", "wreck trail", "marine sanctuary"], "famous_sites": ["John Pennekamp Coral Reef", "USS Vandenberg", "Spiegel Grove"]},
    "great-lakes": {"highlights": ["freshwater wreck diving", "pristine preservation", "cold clear water"], "famous_sites": ["Edmund Fitzgerald area", "Thunder Bay", "Fathom Five"]},
    "jordan-aqaba": {"highlights": ["accessible Red Sea diving", "military wrecks", "healthy reefs"], "famous_sites": ["Cedar Pride", "Tank wreck", "Japanese Garden"]},
    "north-carolina": {"highlights": ["WWII U-boat wrecks", "sand tiger sharks", "Graveyard of the Atlantic"], "famous_sites": ["U-352", "Caribsea", "Papoose"]},
    "okinawa": {"highlights": ["WWII wrecks", "unique Japanese marine life", "coral reefs"], "famous_sites": ["USS Emmons", "Kerama Islands", "Blue Cave"]},
    "lombok": {"highlights": ["muck diving", "coral reefs", "hammerhead encounters at Belongas Bay"], "famous_sites": ["Belongas Bay", "Magnet", "The Playground"]},
    "manado-bunaken": {"highlights": ["spectacular wall diving", "macro diving", "coral biodiversity"], "famous_sites": ["Bunaken Wall", "Lekuan", "Mandolin"]},
    "silfra-fissure": {"highlights": ["diving between tectonic plates", "100m+ visibility", "glacial water"], "famous_sites": ["Silfra Cathedral", "Silfra Hall", "Silfra Lagoon"]},
}


def sanitize_filename(name):
    """Convert site name to a valid filename."""
    sanitized = re.sub(r'[^\w\s-]', '', name.lower())
    sanitized = re.sub(r'[-\s]+', '-', sanitized)
    return sanitized.strip('-')


def get_region_data(region):
    """Get regional knowledge or fall back to defaults."""
    return REGION_DATA.get(region, REGION_DATA["Pacific"])


def determine_visibility(region_data, site_type):
    """Estimate visibility based on region and site type."""
    return region_data["visibility"]


def determine_current(region_data, tags):
    """Determine current strength."""
    osm_current = tags.get("scuba_diving:current", "")
    if osm_current:
        return osm_current.title()
    return region_data["current"]


def get_marine_life_text(region_data, site_type, dest_name):
    """Generate marine life description based on region and site type."""
    if site_type == "wreck":
        species = region_data["wreck_marine_life"] + region_data["typical_marine_life"][:6]
    else:
        species = region_data["typical_marine_life"]

    species_text = ", ".join(species[:8])
    additional = ", ".join(species[8:12]) if len(species) > 8 else ""

    text = f"Divers at this site can expect to encounter {species_text}."
    if additional:
        text += f" Additional species commonly sighted include {additional}."
    if site_type == "wreck":
        text += " The wreck structure provides shelter and habitat for a thriving marine ecosystem, attracting both resident and transient species."
    elif site_type == "wall":
        text += " The wall structure creates a vertical ecosystem with different species at varying depths, often with pelagic visitors in the blue water beyond the wall."
    elif site_type == "cave":
        text += " The cave environment shelters species adapted to low-light conditions, including crustaceans and small fish that seek protection in the overhangs."

    return text


def generate_site_markdown(site, dest, region_data):
    """Generate high-quality markdown content for a dive site."""
    name = site["name"]
    lat = site["lat"]
    lon = site["lon"]
    tags = site.get("tags", {})
    dest_name = dest["name"]
    slug = dest["slug"]

    # Determine site attributes
    site_type = site.get("site_type", "reef")
    entry_type = site.get("entry_type") or "shore"
    difficulty = site.get("difficulty") or "Intermediate"
    depth = site.get("depth") or 25
    osm_id = site.get("osm_id")

    # Get destination-specific info
    dest_info = DESTINATION_SPECIFICS.get(slug, {})

    # Build site information
    visibility = determine_visibility(region_data, site_type)
    current = determine_current(region_data, tags)
    best_time = region_data["best_season"]

    # Entry type display
    entry_display = entry_type.title()
    if entry_type == "shore":
        entry_display = "Shore entry"
    elif entry_type == "boat":
        entry_display = "Boat dive"
    elif entry_type == "both":
        entry_display = "Shore and boat access"

    # Site type display
    type_display = site_type.title()
    if site_type == "reef":
        type_display = "Coral reef"
    elif site_type == "wreck":
        wreck_name = tags.get("wreck:name", "")
        type_display = f"Wreck{' (' + wreck_name + ')' if wreck_name else ''}"
    elif site_type == "wall":
        type_display = "Wall dive"
    elif site_type == "cave":
        type_display = "Cave/Cavern"

    # Generate overview
    overview_parts = [f"{name} is a {'renowned ' if name in str(dest_info.get('famous_sites', '')) else ''}dive site in {dest_name}"]
    if site_type == "wreck":
        sunk_date = tags.get("wreck:date_sunk", "")
        overview_parts.append(f"featuring {'the wreck of the ' + name if not name.lower().startswith(('wreck', 'ss ', 'hms ', 'uss ', 'mv ')) else 'a historic wreck'}")
        if sunk_date:
            overview_parts.append(f"which sank in {sunk_date}")
    elif site_type == "wall":
        overview_parts.append("featuring a dramatic vertical wall that drops into the deep blue")
    elif site_type == "cave":
        overview_parts.append("featuring underwater cave and cavern formations")
    else:
        overview_parts.append(f"offering {'excellent' if difficulty == 'Beginner' else 'rewarding'} diving on healthy coral reef structures")

    note = tags.get("description", tags.get("note", ""))
    if note and len(note) < 200:
        overview_parts.append(f". {note}")

    overview = " ".join(overview_parts) + "."
    overview += f" Located in the {dest['region']} region, this site offers {visibility.split('(')[0].strip()} of visibility"
    overview += f" with water temperatures averaging {region_data['water_temp'].split('(')[0].strip()}."

    # Marine life text
    marine_life = get_marine_life_text(region_data, site_type, dest_name)

    # Dive profile
    if site_type == "wreck":
        dive_profile = (
            f"The dive typically begins with a descent to the top of the wreck structure. "
            f"Plan for a maximum depth of {depth} meters with appropriate bottom time for your certification level. "
            f"Explore the exterior features and any accessible penetration points while monitoring air supply and depth. "
            f"Begin your ascent with adequate reserve for a safety stop at 5 meters."
        )
    elif site_type == "wall":
        dive_profile = (
            f"Begin along the reef top at shallower depths before descending along the wall. "
            f"The wall descends to significant depths, so careful depth management is essential. "
            f"Most of the interesting features and marine life are found between 10-{depth} meters. "
            f"Maintain good buoyancy control and monitor your depth gauge regularly."
        )
    else:
        dive_profile = (
            f"The site offers diving at depths ranging from shallow reef areas down to approximately {depth} meters. "
            f"Begin your dive in the shallower sections and gradually work deeper as conditions allow. "
            f"The most abundant marine life is typically found between 5-{min(depth, 20)} meters. "
            f"Plan your dive within your certification limits and allow adequate air for a safety stop."
        )

    # Entry and exit
    if entry_type == "shore":
        entry_exit = (
            f"Enter from the shore following established entry points. Check conditions before entering "
            f"and be mindful of waves, surge, and underwater obstacles. Navigate to the dive site using "
            f"natural landmarks or compass bearings. Exit at the same location, approaching the shore "
            f"carefully to avoid surge zones."
        )
    elif entry_type == "boat":
        entry_exit = (
            f"Access is by dive boat from local operators. Entry is typically via giant stride or back roll. "
            f"Follow the dive briefing for descent and ascent procedures. Deploy a surface marker buoy (SMB) "
            f"during your safety stop for boat pickup. Coordinate with the boat crew for exit procedures."
        )
    else:
        entry_exit = (
            f"This site can be accessed from shore or by boat. Shore entry follows established paths to the water. "
            f"Boat access is available through local dive operators. Check conditions and choose the most "
            f"appropriate entry method based on weather and sea state."
        )

    # Tips
    tips = []
    if difficulty == "Beginner":
        tips.append("Excellent site for newer divers — calm conditions and easy navigation")
    if site_type == "wreck":
        tips.extend([
            "Bring a dive torch to illuminate wreck interiors and dark overhangs",
            "Maintain proper buoyancy to avoid disturbing silt inside the wreck",
            "Do not attempt penetration without proper training and equipment",
        ])
    if site_type == "wall":
        tips.extend([
            "Watch your depth carefully — wall dives can lead to unintentional deep descents",
            "Look in crevices and overhangs for hidden marine life",
        ])
    if entry_type == "boat":
        tips.append("Book with reputable local dive operators who know the site conditions")
    tips.extend([
        "Bring an underwater camera — this site offers excellent photography opportunities",
        "Check local weather and sea conditions before diving",
        "Respect marine life and maintain proper buoyancy to protect the reef",
    ])
    if "strong" in current.lower():
        tips.append("Carry a surface marker buoy (SMB) and be prepared for current changes")

    # Safety
    hazards_text = ", ".join(region_data["hazards"][:3])
    safety = (
        f"Be aware of {hazards_text} in this area. "
        f"Dive within your certification limits and experience level. "
    )
    if difficulty == "Advanced":
        safety += "This site is recommended for experienced divers only. "
    if "strong" in current.lower() or "strong" in region_data["current"].lower():
        safety += "Strong currents are possible — carry appropriate signaling devices and be prepared to abort the dive if conditions deteriorate. "
    safety += "Always dive with a buddy and carry a safety sausage (SMB)."

    # Photography
    if site_type == "wreck":
        photography = (
            f"The wreck structure provides dramatic wide-angle subjects with natural light filtering through openings. "
            f"A torch is essential for illuminating interior details and bringing out colors. "
            f"Macro opportunities abound on the encrusted surfaces."
        )
    elif site_type == "wall":
        photography = (
            f"Wall dives offer stunning wide-angle opportunities with dramatic depth perspectives. "
            f"The interplay of light and shadow along the wall creates compelling compositions. "
            f"Look for macro subjects in wall crevices and overhangs."
        )
    else:
        photography = (
            f"This site offers excellent opportunities for both wide-angle and macro photography. "
            f"The reef structures and marine life provide diverse subjects. "
            f"Natural light conditions are typically best during morning hours."
        )

    # Build the markdown
    tips_text = "\n".join([f"- {tip}" for tip in tips[:6]])

    ref = tags.get("ref", "")
    website = tags.get("website", "")

    resources = ""
    if website:
        resources += f"- **Website**: {website}\n"
    if ref:
        resources += f"- **Reference**: Site #{ref}\n"
    resources += f"- **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}"

    content = f"""---
name: {name}
lat: {lat}
lng: {lon}
difficulty: {difficulty}
maxDepth: {depth}
entryType: {entry_type}
siteType: {site_type}
ref: {ref if ref else 'null'}
osmId: {osm_id if osm_id else 'null'}
addedBy: osm_import
---

## {name}

{name} is {'a historic wreck dive' if site_type == 'wreck' else 'a ' + site_type + ' dive site'} in {dest_name}, {dest['region']}.

## Overview

{overview}

## Site Information

- **Location**: {dest_name}, {dest['region']}
- **Entry Type**: {entry_display}
- **Site Type**: {type_display}
- **Difficulty Level**: {difficulty}
- **Maximum Depth**: {depth} meters
- **Typical Visibility**: {visibility}
- **Current**: {current}
- **Best Time**: {best_time}

## Marine Life

{marine_life}

## Dive Profile

{dive_profile}

## Entry and Exit

{entry_exit}

## Tips and Recommendations

{tips_text}

## Safety Considerations

{safety}

## Photography

{photography}

## Additional Resources

{resources}

---
*This dive site information was compiled from OpenStreetMap data and regional diving knowledge. Last updated {datetime.now().strftime('%Y-%m-%d')}.*
"""
    return content.strip() + "\n"


def generate_index_entry(site, filename):
    """Generate an index.json entry for a dive site."""
    return {
        "name": site["name"],
        "filename": f"{filename}.md",
        "lat": site["lat"],
        "lng": site["lon"],
        "difficulty": site.get("difficulty") or "Intermediate",
        "maxDepth": site.get("depth") or 25,
        "entryType": site.get("entry_type") or "shore",
        "siteType": site.get("site_type") or "reef",
        "ref": site.get("tags", {}).get("ref", ""),
        "osmId": site.get("osm_id"),
    }


def process_destination(dest, osm_data, divesites_dir):
    """Process a single destination: generate markdown files and index.json."""
    slug = dest["slug"]
    region = dest["region"]
    region_data = get_region_data(region)

    output_dir = divesites_dir / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    index_entries = []
    created = 0
    seen_filenames = set()

    for site in osm_data:
        filename = sanitize_filename(site["name"])
        if not filename or filename in seen_filenames:
            continue
        seen_filenames.add(filename)

        # Generate markdown
        content = generate_site_markdown(site, dest, region_data)
        md_path = output_dir / f"{filename}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Generate index entry
        entry = generate_index_entry(site, filename)
        index_entries.append(entry)
        created += 1

    # Write index.json
    if index_entries:
        index_path = output_dir / "index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_entries, f, indent=2, ensure_ascii=False)

    return created


def main():
    project_root = Path(__file__).parent.parent
    osm_dir = project_root / "data" / "osm_clean"
    divesites_dir = project_root / "divesites"

    # Load destinations
    with open(project_root / "destinations.json", "r", encoding="utf-8") as f:
        destinations = json.load(f)

    dest_by_slug = {d["slug"]: d for d in destinations}

    # Skip destinations that already have hand-curated content
    skip_slugs = {"bonaire", "curacao"}

    total_created = 0
    results = []

    for osm_file in sorted(osm_dir.glob("*.json")):
        if osm_file.name == "_summary.json":
            continue

        slug = osm_file.stem
        if slug in skip_slugs:
            continue

        dest = dest_by_slug.get(slug)
        if not dest:
            print(f"Warning: No destination found for {slug}")
            continue

        # Load OSM data
        with open(osm_file, "r", encoding="utf-8") as f:
            osm_data = json.load(f)

        if not osm_data:
            # Create empty directory with just overview placeholder
            output_dir = divesites_dir / slug
            output_dir.mkdir(parents=True, exist_ok=True)
            # Write empty index
            with open(output_dir / "index.json", "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
            results.append({"name": dest["name"], "slug": slug, "sites": 0})
            continue

        created = process_destination(dest, osm_data, divesites_dir)
        total_created += created
        results.append({"name": dest["name"], "slug": slug, "sites": created})
        print(f"  {dest['name']:40s} {created} sites")

    print(f"\n{'='*60}")
    print(f"Total: {total_created} dive site files generated")
    print(f"Destinations processed: {len(results)}")
    print(f"Destinations with sites: {sum(1 for r in results if r['sites'] > 0)}")


if __name__ == "__main__":
    main()
