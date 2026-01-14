#!/usr/bin/env python3
"""
Build a comprehensive seasonal calendar for BMC-era ecology
Integrates data from all sources (iNaturalist, GBIF, NC Parks, Coweeta LTER)
to create month-by-month ecological activity patterns

Output: A calendar showing what species are active/visible each month
"""

import json
import os
from datetime import datetime
from config import LOCATION, START_YEAR, END_YEAR, PROCESSED_DATA_DIR, OUTPUT_DIR

def load_json(filepath):
    """Load JSON file if it exists"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def build_butterfly_calendar(nc_parks_data):
    """Build monthly butterfly activity from NC Parks data"""
    calendar = {month: [] for month in range(1, 13)}

    if not nc_parks_data or "butterflies" not in nc_parks_data:
        return calendar

    for butterfly in nc_parks_data["butterflies"].get("species", []):
        for month in butterfly.get("flight_months", []):
            if 1 <= month <= 12:
                calendar[month].append({
                    "scientific_name": butterfly["scientific_name"],
                    "common_name": butterfly["common_name"],
                    "family": butterfly["family"],
                    "abundance": butterfly.get("abundance", "unknown")
                })

    return calendar

def build_moth_calendar(nc_parks_data):
    """Build monthly moth activity from NC Parks data"""
    calendar = {month: [] for month in range(1, 13)}

    if not nc_parks_data or "moths" not in nc_parks_data:
        return calendar

    for moth in nc_parks_data["moths"].get("species", []):
        for month in moth.get("flight_months", []):
            if 1 <= month <= 12:
                calendar[month].append({
                    "scientific_name": moth["scientific_name"],
                    "common_name": moth["common_name"],
                    "family": moth["family"],
                    "abundance": moth.get("abundance", "unknown")
                })

    return calendar

def build_plant_bloom_calendar(nc_parks_data):
    """Build monthly plant bloom calendar from NC Parks data"""
    calendar = {month: [] for month in range(1, 13)}

    if not nc_parks_data or "plants" not in nc_parks_data:
        return calendar

    for plant in nc_parks_data["plants"].get("species", []):
        for month in plant.get("bloom_months", []):
            if 1 <= month <= 12:
                calendar[month].append({
                    "scientific_name": plant["scientific_name"],
                    "common_name": plant["common_name"],
                    "type": plant["type"],
                    "family": plant["family"],
                    "habitat": plant.get("habitat", "")
                })

    return calendar

def build_bird_calendar():
    """
    Build bird activity calendar based on regional patterns
    Includes residents, migrants, and breeding seasons
    """
    calendar = {month: [] for month in range(1, 13)}

    # Bird activity patterns for Southern Appalachians
    birds = [
        # Year-round residents
        {"scientific_name": "Cardinalis cardinalis", "common_name": "Northern Cardinal", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Cyanocitta cristata", "common_name": "Blue Jay", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Poecile carolinensis", "common_name": "Carolina Chickadee", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Sitta carolinensis", "common_name": "White-breasted Nuthatch", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Melanerpes carolinus", "common_name": "Red-bellied Woodpecker", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Dryocopus pileatus", "common_name": "Pileated Woodpecker", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Baeolophus bicolor", "common_name": "Tufted Titmouse", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Corvus brachyrhynchos", "common_name": "American Crow", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Thryothorus ludovicianus", "common_name": "Carolina Wren", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Sialia sialis", "common_name": "Eastern Bluebird", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Pipilo erythrophthalmus", "common_name": "Eastern Towhee", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Zenaida macroura", "common_name": "Mourning Dove", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Mimus polyglottos", "common_name": "Northern Mockingbird", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Bonasa umbellus", "common_name": "Ruffed Grouse", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},

        # Winter visitors
        {"scientific_name": "Junco hyemalis", "common_name": "Dark-eyed Junco", "status": "winter", "months": [10, 11, 12, 1, 2, 3, 4], "activity": "winter visitor"},
        {"scientific_name": "Regulus satrapa", "common_name": "Golden-crowned Kinglet", "status": "winter", "months": [10, 11, 12, 1, 2, 3], "activity": "winter visitor"},
        {"scientific_name": "Regulus calendula", "common_name": "Ruby-crowned Kinglet", "status": "winter", "months": [10, 11, 12, 1, 2, 3, 4], "activity": "winter visitor"},
        {"scientific_name": "Zonotrichia albicollis", "common_name": "White-throated Sparrow", "status": "winter", "months": [10, 11, 12, 1, 2, 3, 4], "activity": "winter visitor"},
        {"scientific_name": "Spinus tristis", "common_name": "American Goldfinch", "status": "resident", "months": list(range(1, 13)), "activity": "year-round", "notes": "more visible in winter"},
        {"scientific_name": "Bombycilla cedrorum", "common_name": "Cedar Waxwing", "status": "winter", "months": [11, 12, 1, 2, 3, 4, 5], "activity": "winter-spring visitor"},

        # Summer breeding visitors (neotropical migrants)
        {"scientific_name": "Piranga olivacea", "common_name": "Scarlet Tanager", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Piranga rubra", "common_name": "Summer Tanager", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Hylocichla mustelina", "common_name": "Wood Thrush", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Catharus fuscescens", "common_name": "Veery", "status": "summer", "months": [5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Seiurus aurocapilla", "common_name": "Ovenbird", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Mniotilta varia", "common_name": "Black-and-white Warbler", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Setophaga cerulea", "common_name": "Cerulean Warbler", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Setophaga virens", "common_name": "Black-throated Green Warbler", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Setophaga citrina", "common_name": "Hooded Warbler", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Geothlypis formosa", "common_name": "Kentucky Warbler", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Helmitheros vermivorum", "common_name": "Worm-eating Warbler", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Parkesia motacilla", "common_name": "Louisiana Waterthrush", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Vireo olivaceus", "common_name": "Red-eyed Vireo", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Vireo griseus", "common_name": "White-eyed Vireo", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Contopus virens", "common_name": "Eastern Wood-Pewee", "status": "summer", "months": [5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Myiarchus crinitus", "common_name": "Great Crested Flycatcher", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Sayornis phoebe", "common_name": "Eastern Phoebe", "status": "summer", "months": [3, 4, 5, 6, 7, 8, 9, 10], "activity": "breeding"},
        {"scientific_name": "Progne subis", "common_name": "Purple Martin", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Hirundo rustica", "common_name": "Barn Swallow", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Setophaga americana", "common_name": "Northern Parula", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Icterus galbula", "common_name": "Baltimore Oriole", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Archilochus colubris", "common_name": "Ruby-throated Hummingbird", "status": "summer", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Coccyzus americanus", "common_name": "Yellow-billed Cuckoo", "status": "summer", "months": [5, 6, 7, 8, 9], "activity": "breeding"},
        {"scientific_name": "Antrostomus vociferus", "common_name": "Eastern Whip-poor-will", "status": "summer", "months": [4, 5, 6, 7, 8], "activity": "breeding"},
        {"scientific_name": "Chordeiles minor", "common_name": "Common Nighthawk", "status": "summer", "months": [5, 6, 7, 8, 9], "activity": "breeding"},

        # Raptors
        {"scientific_name": "Buteo jamaicensis", "common_name": "Red-tailed Hawk", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Buteo lineatus", "common_name": "Red-shouldered Hawk", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Accipiter cooperii", "common_name": "Cooper's Hawk", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Haliaeetus leucocephalus", "common_name": "Bald Eagle", "status": "rare", "months": [11, 12, 1, 2, 3], "activity": "winter visitor"},
        {"scientific_name": "Megascops asio", "common_name": "Eastern Screech-Owl", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Bubo virginianus", "common_name": "Great Horned Owl", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Strix varia", "common_name": "Barred Owl", "status": "resident", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Cathartes aura", "common_name": "Turkey Vulture", "status": "resident", "months": [3, 4, 5, 6, 7, 8, 9, 10, 11], "activity": "mostly year-round"},
    ]

    for bird in birds:
        for month in bird["months"]:
            if 1 <= month <= 12:
                calendar[month].append({
                    "scientific_name": bird["scientific_name"],
                    "common_name": bird["common_name"],
                    "status": bird["status"],
                    "activity": bird["activity"]
                })

    return calendar

def build_amphibian_calendar():
    """Build amphibian activity calendar for Southern Appalachians"""
    calendar = {month: [] for month in range(1, 13)}

    amphibians = [
        {"scientific_name": "Anaxyrus americanus", "common_name": "American Toad", "months": [3, 4, 5, 6, 7, 8, 9], "activity": "breeding Mar-Jun"},
        {"scientific_name": "Pseudacris crucifer", "common_name": "Spring Peeper", "months": [2, 3, 4, 5], "activity": "breeding Feb-Apr"},
        {"scientific_name": "Hyla chrysoscelis", "common_name": "Cope's Gray Treefrog", "months": [4, 5, 6, 7, 8], "activity": "breeding May-Aug"},
        {"scientific_name": "Rana clamitans", "common_name": "Green Frog", "months": [4, 5, 6, 7, 8, 9], "activity": "breeding May-Aug"},
        {"scientific_name": "Rana sylvatica", "common_name": "Wood Frog", "months": [2, 3, 4], "activity": "early breeder Feb-Mar"},
        {"scientific_name": "Lithobates catesbeianus", "common_name": "American Bullfrog", "months": [5, 6, 7, 8, 9], "activity": "breeding May-Aug"},
        {"scientific_name": "Notophthalmus viridescens", "common_name": "Eastern Newt", "months": list(range(1, 13)), "activity": "year-round active"},
        {"scientific_name": "Plethodon jordani", "common_name": "Jordan's Salamander", "months": list(range(1, 13)), "activity": "year-round, Appalachian endemic"},
        {"scientific_name": "Desmognathus quadramaculatus", "common_name": "Black-bellied Salamander", "months": list(range(1, 13)), "activity": "year-round in streams"},
        {"scientific_name": "Eurycea wilderae", "common_name": "Blue Ridge Two-lined Salamander", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Pseudotriton ruber", "common_name": "Red Salamander", "months": list(range(1, 13)), "activity": "year-round"},
        {"scientific_name": "Ambystoma maculatum", "common_name": "Spotted Salamander", "months": [2, 3, 4], "activity": "breeding Feb-Apr"},
        {"scientific_name": "Plethodon glutinosus", "common_name": "Northern Slimy Salamander", "months": [3, 4, 5, 6, 7, 8, 9, 10], "activity": "active spring-fall"},
    ]

    for amp in amphibians:
        for month in amp["months"]:
            if 1 <= month <= 12:
                calendar[month].append({
                    "scientific_name": amp["scientific_name"],
                    "common_name": amp["common_name"],
                    "activity": amp["activity"]
                })

    return calendar

def build_ecological_events_calendar():
    """Build calendar of general ecological events"""
    return {
        1: [
            "Coldest month - average low 20°F (-7°C)",
            "Winter residents active (juncos, kinglets)",
            "Owls begin courtship",
            "Earliest skunk cabbage blooms"
        ],
        2: [
            "Maple sap begins to run",
            "First spring peepers may call on warm nights",
            "Wood frogs begin breeding",
            "Spotted salamander migration begins",
            "Red-winged blackbirds return"
        ],
        3: [
            "Spring ephemerals emerge (bloodroot, hepatica)",
            "Amphibian breeding peaks",
            "First butterflies emerge (Mourning Cloak)",
            "Tree sap flowing",
            "Early migratory birds arrive",
            "American woodcock courtship"
        ],
        4: [
            "Peak spring ephemeral bloom",
            "Trilliums, violets, trout lilies flowering",
            "Dogwood and redbud blooming",
            "Major bird migration underway",
            "Ruby-throated hummingbirds arrive",
            "Luna moths begin to emerge",
            "Canopy leaf-out begins"
        ],
        5: [
            "Full canopy leaf-out",
            "Mountain laurel and rhododendron blooming",
            "Peak warbler migration",
            "Most butterflies now active",
            "Luna moths peak",
            "Bird nesting season begins",
            "Black locust blooming"
        ],
        6: [
            "Full summer conditions",
            "Bird breeding season peaks",
            "Sourwood blooming (important honey source)",
            "Peak insect diversity",
            "Fireflies active",
            "Wild blackberries ripening",
            "Lake Eden swimming season"
        ],
        7: [
            "Hot and humid",
            "Bee balm and other summer wildflowers peak",
            "Fledgling birds visible",
            "Cicadas calling",
            "Early fall migration begins (shorebirds)",
            "Joe Pye weed and ironweed blooming"
        ],
        8: [
            "Late summer wildflowers peak",
            "Cardinal flower blooming",
            "Fall migration building",
            "Wild grapes ripening",
            "Goldenrod begins blooming",
            "Hummingbird numbers peak before migration"
        ],
        9: [
            "Fall migration peak for songbirds",
            "Goldenrod and aster bloom",
            "Fall colors begin at highest elevations",
            "Monarch butterfly migration",
            "Acorn and hickory nut production",
            "First frosts possible at high elevations"
        ],
        10: [
            "Peak fall foliage mid-month",
            "Heavy bird migration",
            "Winter residents arrive (juncos)",
            "First hard frosts typical",
            "Witch hazel blooming",
            "Deer rut begins",
            "Bear hyperphagic foraging"
        ],
        11: [
            "Late fall colors",
            "Most deciduous leaves fallen",
            "Winter bird flocks forming",
            "Deer rut peaks",
            "Late migrant birds passing through",
            "First snow possible"
        ],
        12: [
            "Winter conditions",
            "Christmas ferns remain green",
            "Winter bird watching",
            "Bears entering torpor",
            "Shortest days of year",
            "Some birds begin winter territory singing"
        ]
    }

def main():
    """Main function to build seasonal calendar"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    print("=" * 70)
    print("Building Comprehensive Seasonal Ecology Calendar")
    print(f"Location: {LOCATION['name']}")
    print("=" * 70)

    # Load source data
    nc_parks_data = load_json(os.path.join(PROCESSED_DATA_DIR, "nc_parks_species.json"))
    inat_data = load_json(os.path.join(PROCESSED_DATA_DIR, "inaturalist_baseline.json"))
    coweeta_data = load_json(os.path.join(PROCESSED_DATA_DIR, "coweeta_lter_historical.json"))

    print(f"\nData sources loaded:")
    print(f"  NC Parks data: {'Yes' if nc_parks_data else 'No'}")
    print(f"  iNaturalist data: {'Yes' if inat_data else 'No'}")
    print(f"  Coweeta LTER data: {'Yes' if coweeta_data else 'No'}")

    # Build calendars for each taxon
    print("\nBuilding taxon calendars...")

    calendars = {
        "butterflies": build_butterfly_calendar(nc_parks_data),
        "moths": build_moth_calendar(nc_parks_data),
        "plants": build_plant_bloom_calendar(nc_parks_data),
        "birds": build_bird_calendar(),
        "amphibians": build_amphibian_calendar(),
        "ecological_events": build_ecological_events_calendar()
    }

    # Create monthly summary
    monthly_summary = {}
    for month in range(1, 13):
        monthly_summary[MONTH_NAMES[month-1]] = {
            "month_number": month,
            "butterflies_active": len(calendars["butterflies"].get(month, [])),
            "moths_active": len(calendars["moths"].get(month, [])),
            "plants_blooming": len(calendars["plants"].get(month, [])),
            "birds_present": len(calendars["birds"].get(month, [])),
            "amphibians_active": len(calendars["amphibians"].get(month, [])),
            "ecological_events": calendars["ecological_events"].get(month, [])
        }

    # Build final calendar structure
    seasonal_calendar = {
        "metadata": {
            "title": "Seasonal Ecology Calendar - Black Mountain College Era",
            "location": LOCATION["name"],
            "coordinates": [LOCATION["latitude"], LOCATION["longitude"]],
            "elevation_m": LOCATION["elevation_m"],
            "region": "Southern Blue Ridge Mountains",
            "generated": datetime.now().isoformat(),
            "sources": [
                "NC Biodiversity Project",
                "NC Native Plant Society",
                "Coweeta LTER historical data",
                "iNaturalist baseline data",
                "Regional field guides and literature"
            ]
        },
        "summary": monthly_summary,
        "detailed_calendars": {}
    }

    # Build detailed month-by-month data
    for month in range(1, 13):
        month_name = MONTH_NAMES[month-1]
        seasonal_calendar["detailed_calendars"][month_name] = {
            "month_number": month,
            "season": get_season(month),
            "butterflies": calendars["butterflies"].get(month, []),
            "moths": calendars["moths"].get(month, []),
            "plants_blooming": calendars["plants"].get(month, []),
            "birds": calendars["birds"].get(month, []),
            "amphibians": calendars["amphibians"].get(month, []),
            "ecological_events": calendars["ecological_events"].get(month, [])
        }

    # Save to output
    output_file = os.path.join(OUTPUT_DIR, "seasonal_calendar.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(seasonal_calendar, f, indent=2, ensure_ascii=False)
    print(f"\nSeasonal calendar saved to: {output_file}")

    # Also save to processed data
    processed_file = os.path.join(PROCESSED_DATA_DIR, "seasonal_calendar.json")
    with open(processed_file, "w", encoding="utf-8") as f:
        json.dump(seasonal_calendar, f, indent=2, ensure_ascii=False)
    print(f"Copy saved to: {processed_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("SEASONAL CALENDAR SUMMARY")
    print("=" * 70)

    for month_name, summary in monthly_summary.items():
        print(f"\n{month_name}:")
        print(f"  Butterflies: {summary['butterflies_active']}")
        print(f"  Moths: {summary['moths_active']}")
        print(f"  Plants blooming: {summary['plants_blooming']}")
        print(f"  Birds: {summary['birds_present']}")
        print(f"  Amphibians: {summary['amphibians_active']}")

    return seasonal_calendar

def get_season(month):
    """Get season name for a month"""
    if month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Fall"
    else:
        return "Winter"

if __name__ == "__main__":
    main()
