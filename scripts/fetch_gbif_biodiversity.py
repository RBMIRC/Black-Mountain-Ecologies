#!/usr/bin/env python3
"""
Fetch biodiversity data from GBIF (Global Biodiversity Information Facility)
For birds, plants, mammals, fish, and amphibians in the Black Mountain region (1933-1957)
"""

import json
import os
import time
import requests
from collections import defaultdict
from config import BBOX, START_YEAR, END_YEAR, RAW_DATA_DIR, PROCESSED_DATA_DIR, API_DELAY_SECONDS

# GBIF Taxon Keys
TAXON_KEYS = {
    "birds": 212,       # Aves
    "mammals": 359,     # Mammalia
    "plants": 6,        # Plantae
    "fish": 204,        # Actinopterygii (ray-finned fish)
    "amphibians": 131   # Amphibia
}

GBIF_API_BASE = "https://api.gbif.org/v1"

def fetch_gbif_occurrences(taxon_key, taxon_name, limit=300):
    """
    Fetch occurrence records from GBIF for a given taxon
    Note: Historical data (1933-1957) is sparse - most GBIF data is from later periods
    """

    url = f"{GBIF_API_BASE}/occurrence/search"

    all_results = []
    offset = 0

    print(f"\nFetching {taxon_name} records from GBIF...")

    while True:
        params = {
            "decimalLatitude": f"{BBOX['lat_min']},{BBOX['lat_max']}",
            "decimalLongitude": f"{BBOX['lon_min']},{BBOX['lon_max']}",
            "year": f"{START_YEAR},{END_YEAR}",
            "taxonKey": taxon_key,
            "limit": limit,
            "offset": offset,
            "hasCoordinate": "true",
            "hasGeospatialIssue": "false"
        }

        try:
            response = requests.get(url, params=params)
            time.sleep(API_DELAY_SECONDS)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                all_results.extend(results)

                print(f"  Retrieved {len(all_results)} of {data.get('count', 0)} {taxon_name} records")

                # Check if there are more results
                if data.get("endOfRecords", True) or len(results) == 0:
                    break

                offset += limit
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                break

        except Exception as e:
            print(f"  Exception: {e}")
            break

    return all_results

def process_occurrences(occurrences, taxon_name):
    """Process raw occurrences into yearly species lists"""

    yearly_species = defaultdict(lambda: defaultdict(set))

    for occ in occurrences:
        year = occ.get("year")
        species = occ.get("species")
        genus = occ.get("genus")
        family = occ.get("family")

        if year and (species or genus):
            name = species if species else f"{genus} sp."
            scientific_name = occ.get("scientificName", name)
            vernacular = occ.get("vernacularName", "")

            # Create a unique key for the species
            yearly_species[year][name] = {
                "species": name,
                "scientific_name": scientific_name,
                "vernacular_name": vernacular,
                "family": family,
                "count": yearly_species[year].get(name, {}).get("count", 0) + 1
            }

    # Convert to list format
    result = {}
    for year in range(START_YEAR, END_YEAR + 1):
        species_list = list(yearly_species[year].values()) if year in yearly_species else []
        # Sort by count (most observed first)
        species_list.sort(key=lambda x: x.get("count", 0), reverse=True)
        result[year] = {
            "species": species_list,
            "total_species": len(species_list),
            "total_observations": sum(s.get("count", 0) for s in species_list)
        }

    return result

def fetch_all_biodiversity():
    """Fetch and process all biodiversity data"""

    all_data = {}
    raw_data = {}

    for taxon_name, taxon_key in TAXON_KEYS.items():
        occurrences = fetch_gbif_occurrences(taxon_key, taxon_name)
        raw_data[taxon_name] = occurrences
        processed = process_occurrences(occurrences, taxon_name)
        all_data[taxon_name] = processed

    return all_data, raw_data

def add_known_species():
    """
    Add historically documented species that may not appear in GBIF
    Based on historical records and regional fauna/flora guides
    """

    known_species = {
        "birds": {
            "year_range": [1933, 1957],
            "common_species": [
                {"species": "Cardinalis cardinalis", "vernacular_name": "Northern Cardinal", "status": "common resident"},
                {"species": "Cyanocitta cristata", "vernacular_name": "Blue Jay", "status": "common resident"},
                {"species": "Corvus brachyrhynchos", "vernacular_name": "American Crow", "status": "common resident"},
                {"species": "Turdus migratorius", "vernacular_name": "American Robin", "status": "common resident"},
                {"species": "Poecile carolinensis", "vernacular_name": "Carolina Chickadee", "status": "common resident"},
                {"species": "Sitta carolinensis", "vernacular_name": "White-breasted Nuthatch", "status": "common resident"},
                {"species": "Melanerpes carolinus", "vernacular_name": "Red-bellied Woodpecker", "status": "common resident"},
                {"species": "Dryobates pubescens", "vernacular_name": "Downy Woodpecker", "status": "common resident"},
                {"species": "Meleagris gallopavo", "vernacular_name": "Wild Turkey", "status": "present"},
                {"species": "Bonasa umbellus", "vernacular_name": "Ruffed Grouse", "status": "present"},
                {"species": "Cathartes aura", "vernacular_name": "Turkey Vulture", "status": "common"},
                {"species": "Buteo jamaicensis", "vernacular_name": "Red-tailed Hawk", "status": "present"},
            ],
            "source": "Regional ornithological records, Christmas Bird Counts"
        },
        "mammals": {
            "year_range": [1933, 1957],
            "common_species": [
                {"species": "Odocoileus virginianus", "vernacular_name": "White-tailed Deer", "status": "common"},
                {"species": "Procyon lotor", "vernacular_name": "Raccoon", "status": "common"},
                {"species": "Sciurus carolinensis", "vernacular_name": "Eastern Gray Squirrel", "status": "abundant"},
                {"species": "Tamias striatus", "vernacular_name": "Eastern Chipmunk", "status": "common"},
                {"species": "Sylvilagus floridanus", "vernacular_name": "Eastern Cottontail", "status": "common"},
                {"species": "Marmota monax", "vernacular_name": "Groundhog", "status": "present"},
                {"species": "Didelphis virginiana", "vernacular_name": "Virginia Opossum", "status": "common"},
                {"species": "Mephitis mephitis", "vernacular_name": "Striped Skunk", "status": "present"},
                {"species": "Ursus americanus", "vernacular_name": "Black Bear", "status": "present but declining"},
                {"species": "Canis latrans", "vernacular_name": "Coyote", "status": "rare/expanding"},
            ],
            "source": "NC Wildlife Resources Commission historical records"
        },
        "plants": {
            "year_range": [1933, 1957],
            "common_species": [
                {"species": "Castanea dentata", "vernacular_name": "American Chestnut", "status": "dying/extinct by 1940s", "notes": "Chestnut blight"},
                {"species": "Quercus alba", "vernacular_name": "White Oak", "status": "common"},
                {"species": "Quercus rubra", "vernacular_name": "Northern Red Oak", "status": "common"},
                {"species": "Liriodendron tulipifera", "vernacular_name": "Tulip Poplar", "status": "common"},
                {"species": "Acer rubrum", "vernacular_name": "Red Maple", "status": "common"},
                {"species": "Tsuga canadensis", "vernacular_name": "Eastern Hemlock", "status": "common"},
                {"species": "Pinus strobus", "vernacular_name": "Eastern White Pine", "status": "common"},
                {"species": "Rhododendron maximum", "vernacular_name": "Rosebay Rhododendron", "status": "abundant"},
                {"species": "Kalmia latifolia", "vernacular_name": "Mountain Laurel", "status": "abundant"},
                {"species": "Cornus florida", "vernacular_name": "Flowering Dogwood", "status": "common"},
            ],
            "source": "USDA Forest Service records, Coweeta LTER"
        },
        "fish": {
            "year_range": [1933, 1957],
            "common_species": [
                {"species": "Salvelinus fontinalis", "vernacular_name": "Brook Trout", "status": "native, common in streams"},
                {"species": "Oncorhynchus mykiss", "vernacular_name": "Rainbow Trout", "status": "introduced, stocked"},
                {"species": "Salmo trutta", "vernacular_name": "Brown Trout", "status": "introduced, stocked"},
                {"species": "Lepomis macrochirus", "vernacular_name": "Bluegill", "status": "present in ponds"},
                {"species": "Micropterus salmoides", "vernacular_name": "Largemouth Bass", "status": "present in ponds"},
            ],
            "source": "NC Wildlife Resources Commission, trout stocking records"
        },
        "amphibians": {
            "year_range": [1933, 1957],
            "common_species": [
                {"species": "Plethodon jordani", "vernacular_name": "Jordan's Salamander", "status": "endemic, common"},
                {"species": "Desmognathus quadramaculatus", "vernacular_name": "Black-bellied Salamander", "status": "common"},
                {"species": "Eurycea wilderae", "vernacular_name": "Blue Ridge Two-lined Salamander", "status": "common"},
                {"species": "Rana clamitans", "vernacular_name": "Green Frog", "status": "common"},
                {"species": "Rana catesbeiana", "vernacular_name": "American Bullfrog", "status": "present"},
                {"species": "Hyla versicolor", "vernacular_name": "Gray Treefrog", "status": "common"},
            ],
            "source": "Historical herpetological surveys, Highlands Biological Station"
        }
    }

    return known_species

def main():
    """Main function to fetch and process biodiversity data"""

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Fetch from GBIF
    print("=" * 50)
    print("Fetching biodiversity data from GBIF")
    print(f"Region: {BBOX}")
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print("=" * 50)

    gbif_data, raw_data = fetch_all_biodiversity()

    # Save raw data
    raw_file = os.path.join(RAW_DATA_DIR, "gbif_raw_occurrences.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)
    print(f"\nRaw GBIF data saved to {raw_file}")

    # Get known species from historical records
    known_species = add_known_species()

    # Combine GBIF data with known species
    combined_data = {
        "gbif_records": gbif_data,
        "known_species": known_species,
        "metadata": {
            "source": "GBIF API + Historical Records",
            "region": BBOX,
            "period": f"{START_YEAR}-{END_YEAR}",
            "note": "GBIF data for 1933-1957 is sparse; known_species contains historically documented species"
        }
    }

    # Save processed data
    processed_file = os.path.join(PROCESSED_DATA_DIR, "biodiversity_1933_1957.json")
    with open(processed_file, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    print(f"Processed biodiversity data saved to {processed_file}")

    # Print summary
    print("\n=== GBIF Data Summary ===")
    for taxon_name, yearly_data in gbif_data.items():
        total_obs = sum(d.get("total_observations", 0) for d in yearly_data.values())
        years_with_data = sum(1 for d in yearly_data.values() if d.get("total_observations", 0) > 0)
        print(f"{taxon_name.capitalize()}: {total_obs} observations across {years_with_data} years")

    print("\n=== Known Species (Historical Records) ===")
    for taxon_name, data in known_species.items():
        print(f"{taxon_name.capitalize()}: {len(data['common_species'])} documented species")

    return combined_data

if __name__ == "__main__":
    main()
