#!/usr/bin/env python3
"""
Fetch historical specimens from GBIF for Buncombe County, NC (1933-1957)
Focus on: Insects, Plants, Lepidoptera (butterflies/moths)

GBIF TaxonKeys:
- 6 = Plantae (plants)
- 212 = Insecta (insects)
- 797 = Lepidoptera (butterflies/moths)
- 1457 = Coleoptera (beetles)
- 1459 = Hymenoptera (bees, wasps, ants)
- 216 = Odonata (dragonflies, damselflies)
- 220 = Orthoptera (grasshoppers, crickets)
"""

import json
import os
import time
import requests
from datetime import datetime
from config import LOCATION, START_YEAR, END_YEAR, PROCESSED_DATA_DIR, RAW_DATA_DIR

# GBIF API configuration
GBIF_API_BASE = "https://api.gbif.org/v1"
RATE_LIMIT_DELAY = 0.5  # seconds between requests

# Buncombe County bounding box (approximate)
BUNCOMBE_BBOX = {
    "min_lat": 35.4,
    "max_lat": 35.8,
    "min_lon": -82.8,
    "max_lon": -82.2
}

# Taxa to search
TAXA = {
    "Plantae": {"key": 6, "description": "Plants"},
    "Insecta": {"key": 212, "description": "Insects"},
    "Lepidoptera": {"key": 797, "description": "Butterflies and Moths"},
    "Coleoptera": {"key": 1457, "description": "Beetles"},
    "Hymenoptera": {"key": 1459, "description": "Bees, Wasps, Ants"},
    "Odonata": {"key": 216, "description": "Dragonflies, Damselflies"},
    "Orthoptera": {"key": 220, "description": "Grasshoppers, Crickets"}
}

def fetch_gbif_occurrences(taxon_key, taxon_name, year_start, year_end, limit=300):
    """
    Fetch occurrences from GBIF for a specific taxon and year range
    Uses both county name AND bounding box for better coverage
    """
    all_records = []
    offset = 0

    print(f"\n  Fetching {taxon_name} (taxonKey={taxon_key})...")

    # Method 1: By county name
    while True:
        params = {
            "stateProvince": "North Carolina",
            "county": "Buncombe",
            "year": f"{year_start},{year_end}",
            "taxonKey": taxon_key,
            "limit": limit,
            "offset": offset,
            "hasCoordinate": "true"
        }

        try:
            response = requests.get(f"{GBIF_API_BASE}/occurrence/search", params=params)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            all_records.extend(results)
            print(f"    County search: fetched {len(results)} records (offset {offset})")

            if data.get("endOfRecords", True):
                break

            offset += limit
            time.sleep(RATE_LIMIT_DELAY)

        except requests.exceptions.RequestException as e:
            print(f"    Error fetching county data: {e}")
            break

    county_count = len(all_records)

    # Method 2: By bounding box (may catch records without county metadata)
    offset = 0
    bbox_records = []

    while True:
        params = {
            "decimalLatitude": f"{BUNCOMBE_BBOX['min_lat']},{BUNCOMBE_BBOX['max_lat']}",
            "decimalLongitude": f"{BUNCOMBE_BBOX['min_lon']},{BUNCOMBE_BBOX['max_lon']}",
            "year": f"{year_start},{year_end}",
            "taxonKey": taxon_key,
            "limit": limit,
            "offset": offset
        }

        try:
            response = requests.get(f"{GBIF_API_BASE}/occurrence/search", params=params)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            bbox_records.extend(results)

            if data.get("endOfRecords", True):
                break

            offset += limit
            time.sleep(RATE_LIMIT_DELAY)

        except requests.exceptions.RequestException as e:
            print(f"    Error fetching bbox data: {e}")
            break

    # Merge and deduplicate by GBIF key
    existing_keys = {r.get("key") for r in all_records}
    for record in bbox_records:
        if record.get("key") not in existing_keys:
            all_records.append(record)
            existing_keys.add(record.get("key"))

    print(f"    Total: {county_count} from county, {len(bbox_records)} from bbox, {len(all_records)} unique")

    return all_records

def parse_gbif_record(record):
    """Extract relevant fields from a GBIF occurrence record"""
    return {
        "gbif_key": record.get("key"),
        "species": record.get("species"),
        "scientific_name": record.get("scientificName"),
        "vernacular_name": record.get("vernacularName"),
        "kingdom": record.get("kingdom"),
        "phylum": record.get("phylum"),
        "class": record.get("class"),
        "order": record.get("order"),
        "family": record.get("family"),
        "genus": record.get("genus"),
        "year": record.get("year"),
        "month": record.get("month"),
        "day": record.get("day"),
        "event_date": record.get("eventDate"),
        "latitude": record.get("decimalLatitude"),
        "longitude": record.get("decimalLongitude"),
        "locality": record.get("locality"),
        "county": record.get("county"),
        "state_province": record.get("stateProvince"),
        "recorded_by": record.get("recordedBy"),
        "institution_code": record.get("institutionCode"),
        "collection_code": record.get("collectionCode"),
        "catalog_number": record.get("catalogNumber"),
        "basis_of_record": record.get("basisOfRecord"),
        "dataset_name": record.get("datasetName"),
        "dataset_key": record.get("datasetKey"),
        "occurrence_id": record.get("occurrenceID"),
        "gbif_url": f"https://www.gbif.org/occurrence/{record.get('key')}"
    }

def organize_by_year(records):
    """Organize records by year for yearly analysis"""
    by_year = {}
    for record in records:
        year = record.get("year")
        if year and START_YEAR <= year <= END_YEAR:
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(record)
    return by_year

def get_species_summary(records):
    """Get unique species list with counts"""
    species_counts = {}
    for record in records:
        species = record.get("species") or record.get("scientific_name")
        if species:
            if species not in species_counts:
                species_counts[species] = {
                    "count": 0,
                    "scientific_name": record.get("scientific_name"),
                    "vernacular_name": record.get("vernacular_name"),
                    "family": record.get("family"),
                    "years_recorded": set()
                }
            species_counts[species]["count"] += 1
            if record.get("year"):
                species_counts[species]["years_recorded"].add(record.get("year"))

    # Convert sets to sorted lists
    for species in species_counts:
        species_counts[species]["years_recorded"] = sorted(list(species_counts[species]["years_recorded"]))

    return species_counts

def main():
    """Main function to fetch all historical GBIF data"""

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    print("=" * 70)
    print("GBIF Historical Specimens Fetch")
    print(f"Location: Buncombe County, NC (Black Mountain region)")
    print(f"Period: {START_YEAR}-{END_YEAR}")
    print("=" * 70)

    all_data = {
        "metadata": {
            "source": "GBIF (Global Biodiversity Information Facility)",
            "api": "https://api.gbif.org/v1",
            "location": {
                "county": "Buncombe",
                "state": "North Carolina",
                "region": "Black Mountain / Lake Eden",
                "bounding_box": BUNCOMBE_BBOX,
                "center_coordinates": [LOCATION["latitude"], LOCATION["longitude"]]
            },
            "period": f"{START_YEAR}-{END_YEAR}",
            "fetched": datetime.now().isoformat(),
            "taxa_searched": list(TAXA.keys())
        },
        "summary": {
            "total_records": 0,
            "records_by_taxon": {},
            "records_by_year": {},
            "unique_species_count": 0
        },
        "taxa": {},
        "all_specimens": []
    }

    # Fetch each taxon
    for taxon_name, taxon_info in TAXA.items():
        print(f"\n{'='*50}")
        print(f"Taxon: {taxon_name} ({taxon_info['description']})")
        print(f"{'='*50}")

        raw_records = fetch_gbif_occurrences(
            taxon_info["key"],
            taxon_name,
            START_YEAR,
            END_YEAR
        )

        # Parse records
        parsed_records = [parse_gbif_record(r) for r in raw_records]

        # Get species summary
        species_summary = get_species_summary(parsed_records)

        # Organize by year
        by_year = organize_by_year(parsed_records)

        # Store in all_data
        all_data["taxa"][taxon_name] = {
            "description": taxon_info["description"],
            "taxon_key": taxon_info["key"],
            "total_records": len(parsed_records),
            "unique_species": len(species_summary),
            "species_list": species_summary,
            "records_by_year": {str(y): len(recs) for y, recs in by_year.items()},
            "specimens": parsed_records
        }

        # Add to all specimens
        all_data["all_specimens"].extend(parsed_records)

        # Update summary
        all_data["summary"]["records_by_taxon"][taxon_name] = len(parsed_records)

        print(f"  Records found: {len(parsed_records)}")
        print(f"  Unique species: {len(species_summary)}")

        # Show top species
        if species_summary:
            sorted_species = sorted(species_summary.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
            print(f"  Top species:")
            for sp, info in sorted_species:
                print(f"    - {sp}: {info['count']} records")

    # Final summary
    all_data["summary"]["total_records"] = len(all_data["all_specimens"])

    # Count records by year across all taxa
    year_counts = {}
    for record in all_data["all_specimens"]:
        year = record.get("year")
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1
    all_data["summary"]["records_by_year"] = {str(y): c for y, c in sorted(year_counts.items())}

    # Count unique species across all taxa
    all_species = set()
    for record in all_data["all_specimens"]:
        sp = record.get("species") or record.get("scientific_name")
        if sp:
            all_species.add(sp)
    all_data["summary"]["unique_species_count"] = len(all_species)

    # Save raw data
    raw_file = os.path.join(RAW_DATA_DIR, "gbif_historical_raw.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRaw data saved to: {raw_file}")

    # Create processed summary
    processed_data = {
        "metadata": all_data["metadata"],
        "summary": all_data["summary"],
        "species_by_taxon": {}
    }

    for taxon_name, taxon_data in all_data["taxa"].items():
        processed_data["species_by_taxon"][taxon_name] = {
            "description": taxon_data["description"],
            "total_records": taxon_data["total_records"],
            "unique_species": taxon_data["unique_species"],
            "species": [
                {
                    "species": sp,
                    "scientific_name": info["scientific_name"],
                    "vernacular_name": info["vernacular_name"],
                    "family": info["family"],
                    "specimen_count": info["count"],
                    "years_recorded": info["years_recorded"]
                }
                for sp, info in sorted(taxon_data["species_list"].items(), key=lambda x: x[1]["count"], reverse=True)
            ]
        }

    processed_file = os.path.join(PROCESSED_DATA_DIR, "gbif_historical_1933_1957.json")
    with open(processed_file, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    print(f"Processed data saved to: {processed_file}")

    # Print final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total records: {all_data['summary']['total_records']}")
    print(f"Unique species: {all_data['summary']['unique_species_count']}")
    print(f"\nRecords by taxon:")
    for taxon, count in all_data["summary"]["records_by_taxon"].items():
        print(f"  {taxon}: {count}")
    print(f"\nRecords by year:")
    for year, count in sorted(all_data["summary"]["records_by_year"].items()):
        print(f"  {year}: {count}")

    return all_data

if __name__ == "__main__":
    main()
