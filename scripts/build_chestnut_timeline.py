#!/usr/bin/env python3
"""
Build American Chestnut (Castanea dentata) blight timeline
The chestnut blight was the most significant ecological event in the Appalachians
during the BMC period, fundamentally transforming the forest ecosystem.
"""

import json
import os
from config import START_YEAR, END_YEAR, PROCESSED_DATA_DIR

def build_chestnut_timeline():
    """
    Build a timeline of the American Chestnut blight's impact on the
    Black Mountain/Southern Appalachian region
    """

    timeline = {
        "metadata": {
            "species": "Castanea dentata",
            "common_name": "American Chestnut",
            "pathogen": "Cryphonectria parasitica (formerly Endothia parasitica)",
            "common_name_pathogen": "Chestnut blight fungus",
            "origin": "Introduced from Asian chestnut trees imported to New York",
            "description": "The American chestnut was once the dominant tree of Eastern forests, comprising up to 25% of hardwood trees. The blight killed an estimated 3-4 billion trees.",
            "sources": [
                "US Forest Service Historical Records",
                "American Chestnut Foundation",
                "Freinkel, Susan. 'American Chestnut: The Life, Death, and Rebirth of a Perfect Tree' (2007)",
                "Anagnostakis, Sandra L. 'Chestnut Blight: The Classical Problem of an Introduced Pathogen' (1987)",
                "NC Forest Service Archives"
            ]
        },
        "pre_blight_ecology": {
            "forest_composition": "American chestnut comprised 25-30% of Southern Appalachian hardwood forests",
            "economic_importance": [
                "Primary source of tannin for leather industry",
                "Rot-resistant lumber for construction, fencing, railroad ties",
                "Nuts as food source for humans, livestock, and wildlife",
                "Reliable annual nut crop (unlike oaks which mast irregularly)"
            ],
            "ecological_role": [
                "Major food source for deer, bear, turkey, squirrels, and other wildlife",
                "Consistent annual mast crop provided reliable food",
                "Dominant canopy tree in mixed hardwood forests",
                "Supported unique insect and fungal communities"
            ]
        },
        "major_events": [
            {
                "year": 1904,
                "location": "Bronx Zoo, New York City",
                "event": "Chestnut blight first discovered",
                "description": "Forester Hermann Merkel identifies unusual cankers killing chestnut trees at the Bronx Zoo"
            },
            {
                "year": 1905,
                "location": "New York",
                "event": "Pathogen identified",
                "description": "Mycologist William Murrill identifies the fungus causing the blight"
            },
            {
                "year": 1908,
                "location": "Pennsylvania",
                "event": "Rapid spread documented",
                "description": "Blight spreading rapidly through Pennsylvania forests"
            },
            {
                "year": 1911,
                "location": "Pennsylvania",
                "event": "Pennsylvania Blight Commission formed",
                "description": "First organized scientific effort to combat the blight"
            },
            {
                "year": 1912,
                "location": "Virginia",
                "event": "Blight reaches Virginia",
                "description": "Southern spread accelerating down the Appalachian chain"
            },
            {
                "year": 1920,
                "location": "Virginia/Tennessee border",
                "event": "Blight approaching Southern Appalachians",
                "description": "Scientists tracking southward progression of blight front"
            },
            {
                "year": 1923,
                "location": "North Carolina",
                "event": "First blight cases in NC mountains",
                "description": "Chestnut blight confirmed in North Carolina mountain counties"
            },
            {
                "year": 1926,
                "location": "Western NC",
                "event": "Blight widespread in region",
                "description": "Blight established throughout the Black Mountain region"
            },
            {
                "year": 1930,
                "location": "Southern Appalachians",
                "event": "Mass mortality begins",
                "description": "Large-scale death of chestnut trees accelerating"
            },
            {
                "year": 1933,
                "location": "Black Mountain region",
                "event": "BMC opens amid dying forest",
                "description": "Black Mountain College opens as chestnut blight transforms surrounding forests"
            },
            {
                "year": 1938,
                "location": "Southern Appalachians",
                "event": "Peak mortality",
                "description": "Majority of mature American chestnuts dead or dying"
            },
            {
                "year": 1940,
                "location": "Southern Appalachians",
                "event": "Near-complete extinction of mature trees",
                "description": "American chestnut functionally extinct as a canopy tree in Southern Appalachians"
            },
            {
                "year": 1950,
                "location": "Eastern US",
                "event": "Blight reaches Gulf Coast",
                "description": "Entire native range affected; estimated 3-4 billion trees dead"
            }
        ],
        "yearly_status": {},
        "ecological_consequences": {
            "forest_composition_change": [
                "Oaks (Quercus spp.) became dominant canopy trees",
                "Red maple (Acer rubrum) increased significantly",
                "Hickories (Carya spp.) expanded",
                "Tulip poplar (Liriodendron tulipifera) increased"
            ],
            "wildlife_impacts": [
                "Loss of reliable annual mast crop",
                "Black bear and wild turkey populations declined",
                "Shift to oak mast with irregular production years",
                "Some insect species dependent on chestnut went extinct"
            ],
            "economic_impacts": [
                "Loss of tannin industry",
                "Loss of valuable lumber source",
                "Loss of subsistence nut crop for rural communities",
                "CCC programs employed workers to salvage dead trees"
            ]
        }
    }

    # Build yearly status for BMC period
    for year in range(START_YEAR, END_YEAR + 1):
        status = {
            "year": year,
            "blight_present": True,
            "mature_tree_status": "",
            "estimated_survival_percent": 0,
            "notes": ""
        }

        if year <= 1933:
            status["mature_tree_status"] = "dying"
            status["estimated_survival_percent"] = 40
            status["notes"] = "Active blight spread; many trees infected but still standing"

        elif year <= 1938:
            status["mature_tree_status"] = "mass_mortality"
            status["estimated_survival_percent"] = 15
            status["notes"] = "Peak mortality period; dead and dying trees throughout forest"

        elif year <= 1945:
            status["mature_tree_status"] = "functionally_extinct"
            status["estimated_survival_percent"] = 2
            status["notes"] = "Mature trees essentially gone; some root sprouts surviving"

        else:
            status["mature_tree_status"] = "extinct_as_canopy"
            status["estimated_survival_percent"] = 0
            status["notes"] = "Only root sprouts remain; forest composition shift complete"

        status["root_sprouts"] = "present" if year >= 1935 else "emerging"
        status["salvage_logging"] = year >= 1935 and year <= 1945

        timeline["yearly_status"][year] = status

    return timeline

def main():
    """Main function"""

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    timeline = build_chestnut_timeline()

    # Save to file
    output_file = os.path.join(PROCESSED_DATA_DIR, "chestnut_blight_1933_1957.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)

    print(f"Chestnut blight timeline saved to {output_file}")

    # Print summary
    print("\n=== American Chestnut Blight Timeline ===")
    print("Species: Castanea dentata (American Chestnut)")
    print(f"Period covered: {START_YEAR}-{END_YEAR}")

    print("\nKey events:")
    for event in timeline["major_events"]:
        if START_YEAR - 10 <= event["year"] <= END_YEAR:
            print(f"  {event['year']}: {event['event']}")

    print("\nBMC period status:")
    for year in [1933, 1940, 1950, 1957]:
        status = timeline["yearly_status"][year]
        print(f"  {year}: {status['mature_tree_status']} ({status['estimated_survival_percent']}% survival)")

    return timeline

if __name__ == "__main__":
    main()
