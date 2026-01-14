#!/usr/bin/env python3
"""
Merge all collected ecological data into a single comprehensive JSON file
for Black Mountain College period (1933-1957)
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

def merge_all_data():
    """Merge all processed data files into a single JSON"""

    # Load all data files
    weather_data = load_json(os.path.join(PROCESSED_DATA_DIR, "weather_1933_1957.json"))
    biodiversity_data = load_json(os.path.join(PROCESSED_DATA_DIR, "biodiversity_1933_1957.json"))
    pesticide_data = load_json(os.path.join(PROCESSED_DATA_DIR, "pesticides_1933_1957.json"))
    chestnut_data = load_json(os.path.join(PROCESSED_DATA_DIR, "chestnut_blight_1933_1957.json"))
    farm_data = load_json(os.path.join(PROCESSED_DATA_DIR, "bmc_farm_1933_1957.json"))

    # Load new data sources
    nc_parks_data = load_json(os.path.join(PROCESSED_DATA_DIR, "nc_parks_species.json"))
    coweeta_data = load_json(os.path.join(PROCESSED_DATA_DIR, "coweeta_lter_historical.json"))
    seasonal_data = load_json(os.path.join(PROCESSED_DATA_DIR, "seasonal_calendar.json"))
    inat_data = load_json(os.path.join(PROCESSED_DATA_DIR, "inaturalist_baseline.json"))
    gbif_historical = load_json(os.path.join(PROCESSED_DATA_DIR, "gbif_historical_1933_1957.json"))

    # Build the final structure
    final_data = {
        "metadata": {
            "title": "Black Mountain College Ecological Data (1933-1957)",
            "location": LOCATION["name"],
            "coordinates": [LOCATION["latitude"], LOCATION["longitude"]],
            "elevation_m": LOCATION["elevation_m"],
            "period": f"{START_YEAR}-{END_YEAR}",
            "generated": datetime.now().isoformat(),
            "sources": [
                "Open-Meteo Historical Weather API",
                "GBIF (Global Biodiversity Information Facility)",
                "iNaturalist Species Baseline",
                "NC Biodiversity Project",
                "NC Native Plant Society",
                "Coweeta Long-Term Ecological Research (LTER)",
                "US Forest Service Historical Records",
                "EPA Historical Documents",
                "USDA Agricultural Statistics",
                "American Chestnut Foundation",
                "NC Wildlife Resources Commission",
                "NC Natural Heritage Program",
                "David Silver, 'The Farm at Black Mountain College' (2024)",
                "Western Regional Archives, Asheville, NC",
                "Black Mountain College Museum + Arts Center"
            ],
            "notes": [
                "Weather data 1933-1939 is estimated from 1940-1949 averages",
                "GBIF biodiversity data is supplemented with historical records",
                "Chestnut blight was the major ecological event of this period"
            ]
        },
        "ecological_context": {
            "region": "Southern Blue Ridge Mountains",
            "ecoregion": "Southern Appalachian",
            "forest_type": "Mixed Mesophytic / Appalachian Oak Forest",
            "climate": "Humid subtropical highland (Cfb)",
            "major_events": []
        },
        "yearly_data": []
    }

    # Add major ecological events
    if chestnut_data:
        for event in chestnut_data.get("major_events", []):
            if START_YEAR <= event["year"] <= END_YEAR:
                final_data["ecological_context"]["major_events"].append({
                    "year": event["year"],
                    "type": "chestnut_blight",
                    "event": event["event"],
                    "description": event.get("description", "")
                })

    if pesticide_data:
        for event in pesticide_data.get("major_events", []):
            if START_YEAR <= event["year"] <= END_YEAR:
                final_data["ecological_context"]["major_events"].append({
                    "year": event["year"],
                    "type": "pesticide",
                    "event": event["event"],
                    "description": event.get("description", "")
                })

    # Add farm events
    if farm_data:
        for event in farm_data.get("major_events", []):
            if START_YEAR <= event["year"] <= END_YEAR:
                final_data["ecological_context"]["major_events"].append({
                    "year": event["year"],
                    "type": "farm",
                    "event": event["event"],
                    "description": event.get("description", ""),
                    "key_people": event.get("key_people", [])
                })

    # Sort events by year
    final_data["ecological_context"]["major_events"].sort(key=lambda x: x["year"])

    # Build yearly data
    for year in range(START_YEAR, END_YEAR + 1):
        year_str = str(year)

        yearly = {
            "year": year,
            "weather": None,
            "flora": {"trees": [], "notable_plants": []},
            "fauna": {"birds": [], "mammals": [], "fish": [], "amphibians": []},
            "pesticides": {"ddt_available": False, "notes": ""},
            "ecological_events": [],
            "farm": None
        }

        # Add weather data
        if weather_data and year_str in weather_data:
            w = weather_data[year_str]
            yearly["weather"] = {
                "monthly": w.get("monthly", []),
                "annual_avg_temp": w.get("annual_avg_temp"),
                "annual_avg_temp_max": w.get("annual_avg_temp_max"),
                "annual_avg_temp_min": w.get("annual_avg_temp_min"),
                "total_precip_mm": w.get("total_precip_mm"),
                "estimated": w.get("estimated", False),
                "source": w.get("source", "")
            }

        # Add biodiversity data
        if biodiversity_data:
            # Add GBIF records
            gbif = biodiversity_data.get("gbif_records", {})

            for taxon in ["birds", "mammals", "fish", "amphibians"]:
                if taxon in gbif and year_str in gbif[taxon]:
                    yearly["fauna"][taxon] = gbif[taxon][year_str].get("species", [])[:20]  # Top 20

            if "plants" in gbif and year_str in gbif["plants"]:
                plants = gbif["plants"][year_str].get("species", [])
                # Separate trees from other plants
                for plant in plants[:30]:  # Top 30
                    yearly["flora"]["notable_plants"].append(plant)

            # Add known species for context
            known = biodiversity_data.get("known_species", {})
            if not yearly["fauna"]["birds"] and "birds" in known:
                yearly["fauna"]["birds"] = known["birds"].get("common_species", [])
            if not yearly["fauna"]["mammals"] and "mammals" in known:
                yearly["fauna"]["mammals"] = known["mammals"].get("common_species", [])
            if not yearly["fauna"]["fish"] and "fish" in known:
                yearly["fauna"]["fish"] = known["fish"].get("common_species", [])
            if not yearly["fauna"]["amphibians"] and "amphibians" in known:
                yearly["fauna"]["amphibians"] = known["amphibians"].get("common_species", [])

            # Add known trees
            if "plants" in known:
                yearly["flora"]["trees"] = known["plants"].get("common_species", [])

        # Add pesticide data
        if pesticide_data and "yearly_data" in pesticide_data:
            if year in pesticide_data["yearly_data"]:
                p = pesticide_data["yearly_data"][year]
                yearly["pesticides"] = {
                    "ddt_available": p.get("ddt_available", False),
                    "ddt_agricultural_use": p.get("ddt_agricultural_use", False),
                    "common_pesticides": p.get("common_pesticides", []),
                    "estimated_regional_usage": p.get("estimated_regional_usage", "unknown"),
                    "notes": p.get("notes", "")
                }

        # Add chestnut blight status
        if chestnut_data and "yearly_status" in chestnut_data:
            if year in chestnut_data["yearly_status"]:
                c = chestnut_data["yearly_status"][year]
                yearly["ecological_events"].append({
                    "type": "chestnut_blight",
                    "species": "Castanea dentata",
                    "status": c.get("mature_tree_status", ""),
                    "survival_percent": c.get("estimated_survival_percent", 0),
                    "notes": c.get("notes", "")
                })

        # Add farm data
        if farm_data and "yearly_status" in farm_data:
            if year_str in farm_data["yearly_status"]:
                yearly["farm"] = farm_data["yearly_status"][year_str]

        final_data["yearly_data"].append(yearly)

    # Add complete farm reference data
    if farm_data:
        final_data["farm_reference"] = {
            "livestock": farm_data.get("livestock", {}),
            "crops": farm_data.get("crops", {}),
            "buildings": farm_data.get("buildings", {}),
            "equipment": farm_data.get("equipment", {}),
            "key_people": farm_data.get("key_people", {}),
            "programs": farm_data.get("programs", {}),
            "organic_practices": farm_data.get("organic_practices", {})
        }

    # Add NC Parks species data (moths, butterflies, native plants)
    if nc_parks_data:
        final_data["species_reference"] = {
            "moths": nc_parks_data.get("moths", {}),
            "butterflies": nc_parks_data.get("butterflies", {}),
            "native_plants": nc_parks_data.get("plants", {})
        }

    # Add Coweeta LTER historical context
    if coweeta_data:
        final_data["coweeta_baseline"] = {
            "forest_composition": coweeta_data.get("historical_forest_composition", {}),
            "chestnut_blight_timeline": coweeta_data.get("chestnut_blight_timeline", {}),
            "historical_wildlife": coweeta_data.get("wildlife_records", {}),
            "bmc_era_baseline": coweeta_data.get("bmc_era_baseline", {})
        }

    # Add seasonal calendar
    if seasonal_data:
        final_data["seasonal_calendar"] = {
            "summary": seasonal_data.get("summary", {}),
            "detailed_calendars": seasonal_data.get("detailed_calendars", {})
        }

    # Add iNaturalist modern baseline
    if inat_data:
        final_data["modern_species_baseline"] = {
            "summary": inat_data.get("summary", {}),
            "baseline_species": inat_data.get("baseline_species", {}),
            "seasonal_patterns": inat_data.get("seasonal_patterns", {})
        }

    # Add GBIF historical specimens
    if gbif_historical:
        final_data["historical_specimens"] = {
            "summary": gbif_historical.get("summary", {}),
            "species_by_taxon": gbif_historical.get("species_by_taxon", {})
        }

    return final_data

def main():
    """Main function"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("Merging all ecological data for BMC period (1933-1957)")
    print("=" * 60)

    final_data = merge_all_data()

    # Save to output file
    output_file = os.path.join(OUTPUT_DIR, "bmc_ecology_1933_1957.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"\nFinal data saved to: {output_file}")

    # Print summary
    print("\n=== Data Summary ===")
    print(f"Location: {final_data['metadata']['location']}")
    print(f"Period: {final_data['metadata']['period']}")
    print(f"Years of data: {len(final_data['yearly_data'])}")
    print(f"Major ecological events: {len(final_data['ecological_context']['major_events'])}")
    print(f"Sources: {len(final_data['metadata']['sources'])}")

    # File size
    file_size = os.path.getsize(output_file)
    print(f"\nOutput file size: {file_size / 1024:.1f} KB")

    return final_data

if __name__ == "__main__":
    main()
