#!/usr/bin/env python3
"""
Build pesticide usage timeline for the BMC period (1933-1957)
Based on historical records and EPA/USDA documentation
"""

import json
import os
from config import START_YEAR, END_YEAR, PROCESSED_DATA_DIR

def build_pesticide_timeline():
    """
    Build a timeline of pesticide development and usage in the US
    with focus on DDT and other chemicals used in the Appalachian region
    """

    timeline = {
        "metadata": {
            "description": "Pesticide usage timeline for the Black Mountain, NC region (1933-1957)",
            "sources": [
                "EPA Historical Documents",
                "USDA Agricultural Statistics",
                "US Forest Service Records",
                "Rachel Carson's Silent Spring (1962) - historical references",
                "NC Department of Agriculture Archives"
            ]
        },
        "major_events": [
            {
                "year": 1939,
                "event": "DDT discovered as insecticide",
                "description": "Paul Hermann Müller discovers DDT's insecticidal properties in Switzerland",
                "impact": "Beginning of synthetic pesticide era"
            },
            {
                "year": 1942,
                "event": "US military DDT production begins",
                "description": "US begins large-scale DDT production for military use against typhus and malaria",
                "impact": "Proven effective against disease-carrying insects"
            },
            {
                "year": 1943,
                "event": "DDT used in Naples typhus epidemic",
                "description": "First large-scale civilian use of DDT to control typhus outbreak",
                "impact": "Demonstrated public health potential"
            },
            {
                "year": 1945,
                "event": "DDT released for civilian use",
                "description": "US government authorizes DDT for general public sale",
                "impact": "Agricultural and household use begins"
            },
            {
                "year": 1946,
                "event": "Agricultural DDT use begins",
                "description": "Farmers begin using DDT for crop protection; USDA promotes usage",
                "impact": "Widespread adoption in agriculture"
            },
            {
                "year": 1948,
                "event": "First insect resistance observed",
                "description": "Houseflies show resistance to DDT in some areas",
                "impact": "Early warning sign ignored"
            },
            {
                "year": 1948,
                "event": "Müller receives Nobel Prize",
                "description": "Paul Müller awarded Nobel Prize in Physiology or Medicine for DDT discovery",
                "impact": "DDT seen as miracle chemical"
            },
            {
                "year": 1950,
                "event": "Peak DDT enthusiasm",
                "description": "US DDT production reaches massive scale; aerial spraying programs expand",
                "impact": "Environmental accumulation begins"
            },
            {
                "year": 1954,
                "event": "USDA fire ant eradication program",
                "description": "Massive aerial spraying campaign in Southern states using DDT and other chemicals",
                "impact": "Significant wildlife mortality observed"
            },
            {
                "year": 1957,
                "event": "First Forest Service restrictions",
                "description": "US Forest Service begins limiting DDT use in some areas due to wildlife concerns",
                "impact": "Early regulatory response"
            }
        ],
        "yearly_data": {}
    }

    # Build yearly data
    for year in range(START_YEAR, END_YEAR + 1):
        yearly = {
            "year": year,
            "ddt_available": year >= 1945,
            "ddt_agricultural_use": year >= 1946,
            "estimated_regional_usage": "none",
            "notes": ""
        }

        if year < 1939:
            yearly["notes"] = "Pre-synthetic pesticide era; arsenic-based compounds and natural pesticides used"
            yearly["common_pesticides"] = ["lead arsenate", "calcium arsenate", "pyrethrum", "rotenone"]
            yearly["estimated_regional_usage"] = "low"

        elif year < 1945:
            yearly["notes"] = "DDT in military use only; traditional pesticides continue"
            yearly["common_pesticides"] = ["lead arsenate", "calcium arsenate", "pyrethrum", "rotenone"]
            yearly["estimated_regional_usage"] = "low"

        elif year < 1950:
            yearly["notes"] = "DDT becoming available; adoption growing"
            yearly["common_pesticides"] = ["DDT", "lead arsenate", "BHC (lindane)", "chlordane"]
            yearly["estimated_regional_usage"] = "moderate"

        else:
            yearly["notes"] = "Peak synthetic pesticide era; widespread DDT use"
            yearly["common_pesticides"] = ["DDT", "BHC (lindane)", "chlordane", "aldrin", "dieldrin", "toxaphene"]
            yearly["estimated_regional_usage"] = "high"

            if year >= 1954:
                yearly["notes"] += "; Fire ant program affects region"

        # Appalachian-specific notes
        if year >= 1945:
            yearly["forest_service_spraying"] = True
            yearly["agricultural_application"] = True
            yearly["notes"] += "; Tobacco and apple orchards primary agricultural users in region"

        timeline["yearly_data"][year] = yearly

    return timeline

def main():
    """Main function"""

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    timeline = build_pesticide_timeline()

    # Save to file
    output_file = os.path.join(PROCESSED_DATA_DIR, "pesticides_1933_1957.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)

    print(f"Pesticide timeline saved to {output_file}")

    # Print summary
    print("\n=== Pesticide Timeline Summary ===")
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print(f"Major events: {len(timeline['major_events'])}")

    print("\nKey milestones:")
    for event in timeline["major_events"]:
        print(f"  {event['year']}: {event['event']}")

    return timeline

if __name__ == "__main__":
    main()
