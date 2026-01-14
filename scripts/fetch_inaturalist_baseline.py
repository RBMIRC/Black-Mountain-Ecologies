#!/usr/bin/env python3
"""
Fetch species baseline from iNaturalist for Buncombe County, NC
This gives us modern observations to establish which species ARE present in the area.

iNaturalist API: https://api.inaturalist.org/v1/docs/
Rate limit: 60 requests/minute max

Buncombe County place_id: 1267 (to verify)
"""

import json
import os
import time
import requests
from datetime import datetime
from config import LOCATION, PROCESSED_DATA_DIR, RAW_DATA_DIR

# iNaturalist API
INAT_API_BASE = "https://api.inaturalist.org/v1"
RATE_LIMIT_DELAY = 1.1  # seconds between requests (safe for 60/min limit)

# Buncombe County place_id - we'll verify this first
BUNCOMBE_PLACE_ID = None  # Will be found dynamically

# Taxa to search (iNaturalist iconic taxa)
ICONIC_TAXA = [
    {"name": "Insecta", "taxon_id": 47158, "description": "Insects"},
    {"name": "Lepidoptera", "taxon_id": 47157, "description": "Butterflies and Moths"},
    {"name": "Plantae", "taxon_id": 47126, "description": "Plants"},
    {"name": "Odonata", "taxon_id": 47792, "description": "Dragonflies and Damselflies"},
    {"name": "Coleoptera", "taxon_id": 47208, "description": "Beetles"},
    {"name": "Hymenoptera", "taxon_id": 47201, "description": "Bees, Wasps, Ants"},
]

def find_buncombe_place_id():
    """Find the iNaturalist place_id for Buncombe County"""
    print("Finding Buncombe County place_id...")

    params = {
        "q": "Buncombe County",
        "admin_level": 2  # County level
    }

    try:
        response = requests.get(f"{INAT_API_BASE}/places/autocomplete", params=params)
        response.raise_for_status()
        data = response.json()

        for result in data.get("results", []):
            if "Buncombe" in result.get("display_name", "") and "North Carolina" in result.get("display_name", ""):
                print(f"  Found: {result['display_name']} (id={result['id']})")
                return result["id"]

        # Fallback: search by coordinates
        print("  Trying coordinate-based search...")
        params = {
            "lat": LOCATION["latitude"],
            "lng": LOCATION["longitude"]
        }
        response = requests.get(f"{INAT_API_BASE}/places/nearby", params=params)
        response.raise_for_status()
        data = response.json()

        for result in data.get("results", {}).get("standard", []):
            if result.get("admin_level") == 2:  # County
                print(f"  Found via coordinates: {result['display_name']} (id={result['id']})")
                return result["id"]

    except Exception as e:
        print(f"  Error finding place: {e}")

    # Known fallback
    print("  Using known Buncombe County place_id: 1267")
    return 1267

def fetch_species_counts(place_id, taxon_id, taxon_name):
    """Fetch species counts for a taxon in Buncombe County"""
    print(f"\n  Fetching {taxon_name} species counts...")

    all_species = []
    page = 1
    per_page = 500

    while True:
        params = {
            "place_id": place_id,
            "taxon_id": taxon_id,
            "per_page": per_page,
            "page": page,
            "verifiable": "true",
            "quality_grade": "research,needs_id"
        }

        try:
            response = requests.get(f"{INAT_API_BASE}/observations/species_counts", params=params)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            all_species.extend(results)
            print(f"    Page {page}: {len(results)} species")

            # Check if we've gotten all
            total_results = data.get("total_results", 0)
            if len(all_species) >= total_results:
                break

            page += 1
            time.sleep(RATE_LIMIT_DELAY)

        except requests.exceptions.RequestException as e:
            print(f"    Error: {e}")
            break

    return all_species

def parse_species_result(result):
    """Parse iNaturalist species count result"""
    taxon = result.get("taxon", {})
    return {
        "taxon_id": taxon.get("id"),
        "scientific_name": taxon.get("name"),
        "common_name": taxon.get("preferred_common_name"),
        "rank": taxon.get("rank"),
        "iconic_taxon": taxon.get("iconic_taxon_name"),
        "family": None,  # Would need additional API call
        "observation_count": result.get("count", 0),
        "wikipedia_url": taxon.get("wikipedia_url"),
        "inat_url": f"https://www.inaturalist.org/taxa/{taxon.get('id')}" if taxon.get("id") else None,
        "photo_url": taxon.get("default_photo", {}).get("medium_url") if taxon.get("default_photo") else None,
        "conservation_status": taxon.get("conservation_status", {}).get("status") if taxon.get("conservation_status") else None
    }

def fetch_seasonal_data(place_id, taxon_id, taxon_name):
    """Fetch monthly observation patterns for seasonal calendar"""
    print(f"\n  Fetching seasonal data for {taxon_name}...")

    monthly_counts = {}

    for month in range(1, 13):
        params = {
            "place_id": place_id,
            "taxon_id": taxon_id,
            "month": month,
            "verifiable": "true",
            "per_page": 0  # Just want count
        }

        try:
            response = requests.get(f"{INAT_API_BASE}/observations", params=params)
            response.raise_for_status()
            data = response.json()
            monthly_counts[month] = data.get("total_results", 0)
            time.sleep(RATE_LIMIT_DELAY)

        except Exception as e:
            print(f"    Error for month {month}: {e}")
            monthly_counts[month] = 0

    return monthly_counts

def get_butterflies_detailed(place_id):
    """Get detailed butterfly species with flight periods"""
    print("\n  Fetching detailed butterfly data...")

    # Butterflies specifically (not moths)
    butterfly_superfamilies = [
        {"name": "Papilionoidea", "taxon_id": 47223},  # True butterflies
    ]

    all_butterflies = []

    for sf in butterfly_superfamilies:
        species = fetch_species_counts(place_id, sf["taxon_id"], sf["name"])
        for sp in species:
            parsed = parse_species_result(sp)
            parsed["group"] = "butterfly"
            all_butterflies.append(parsed)

    return all_butterflies

def main():
    """Main function to fetch iNaturalist baseline data"""

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    print("=" * 70)
    print("iNaturalist Baseline Species Fetch")
    print(f"Location: Buncombe County, NC (Black Mountain region)")
    print("=" * 70)

    # Find place ID
    global BUNCOMBE_PLACE_ID
    BUNCOMBE_PLACE_ID = find_buncombe_place_id()

    all_data = {
        "metadata": {
            "source": "iNaturalist",
            "api": "https://api.inaturalist.org/v1",
            "place_id": BUNCOMBE_PLACE_ID,
            "location": "Buncombe County, North Carolina",
            "purpose": "Baseline species list for ecological reconstruction",
            "fetched": datetime.now().isoformat(),
            "notes": [
                "Modern observations used to establish species presence",
                "Historical presence inferred for native species",
                "Seasonal patterns based on observation dates"
            ]
        },
        "summary": {
            "total_species": 0,
            "species_by_taxon": {}
        },
        "taxa": {},
        "seasonal_patterns": {}
    }

    # Fetch each taxon
    for taxon_info in ICONIC_TAXA:
        taxon_name = taxon_info["name"]
        taxon_id = taxon_info["taxon_id"]

        print(f"\n{'='*50}")
        print(f"Taxon: {taxon_name} ({taxon_info['description']})")
        print(f"{'='*50}")

        # Get species counts
        species_results = fetch_species_counts(BUNCOMBE_PLACE_ID, taxon_id, taxon_name)

        # Parse results
        parsed_species = [parse_species_result(r) for r in species_results]

        # Sort by observation count
        parsed_species.sort(key=lambda x: x["observation_count"], reverse=True)

        # Get seasonal data
        seasonal = fetch_seasonal_data(BUNCOMBE_PLACE_ID, taxon_id, taxon_name)

        # Store
        all_data["taxa"][taxon_name] = {
            "description": taxon_info["description"],
            "taxon_id": taxon_id,
            "total_species": len(parsed_species),
            "total_observations": sum(sp["observation_count"] for sp in parsed_species),
            "species": parsed_species
        }

        all_data["seasonal_patterns"][taxon_name] = seasonal
        all_data["summary"]["species_by_taxon"][taxon_name] = len(parsed_species)

        print(f"  Species found: {len(parsed_species)}")
        print(f"  Total observations: {sum(sp['observation_count'] for sp in parsed_species)}")

        # Show top species
        if parsed_species:
            print(f"  Top 5 species:")
            for sp in parsed_species[:5]:
                name = sp["common_name"] or sp["scientific_name"]
                print(f"    - {name}: {sp['observation_count']} obs")

    # Get detailed butterflies
    print("\n" + "=" * 50)
    print("Fetching detailed butterfly data...")
    print("=" * 50)
    butterflies = get_butterflies_detailed(BUNCOMBE_PLACE_ID)
    all_data["butterflies_detailed"] = butterflies
    print(f"  Butterfly species: {len(butterflies)}")

    # Calculate totals
    all_data["summary"]["total_species"] = sum(all_data["summary"]["species_by_taxon"].values())

    # Save raw data
    raw_file = os.path.join(RAW_DATA_DIR, "inaturalist_baseline_raw.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"\nRaw data saved to: {raw_file}")

    # Create processed summary for easy integration
    processed_data = {
        "metadata": all_data["metadata"],
        "summary": all_data["summary"],
        "baseline_species": {
            "butterflies": [
                {
                    "scientific_name": sp["scientific_name"],
                    "common_name": sp["common_name"],
                    "observations": sp["observation_count"],
                    "inat_url": sp["inat_url"]
                }
                for sp in all_data.get("butterflies_detailed", [])[:100]
            ],
            "moths": [
                {
                    "scientific_name": sp["scientific_name"],
                    "common_name": sp["common_name"],
                    "observations": sp["observation_count"]
                }
                for sp in all_data["taxa"].get("Lepidoptera", {}).get("species", [])
                if sp.get("common_name") and "moth" in sp.get("common_name", "").lower()
            ][:100],
            "insects_other": [
                {
                    "scientific_name": sp["scientific_name"],
                    "common_name": sp["common_name"],
                    "observations": sp["observation_count"]
                }
                for sp in all_data["taxa"].get("Insecta", {}).get("species", [])[:100]
            ],
            "dragonflies": [
                {
                    "scientific_name": sp["scientific_name"],
                    "common_name": sp["common_name"],
                    "observations": sp["observation_count"]
                }
                for sp in all_data["taxa"].get("Odonata", {}).get("species", [])[:50]
            ],
            "bees_wasps": [
                {
                    "scientific_name": sp["scientific_name"],
                    "common_name": sp["common_name"],
                    "observations": sp["observation_count"]
                }
                for sp in all_data["taxa"].get("Hymenoptera", {}).get("species", [])[:50]
            ],
            "plants": [
                {
                    "scientific_name": sp["scientific_name"],
                    "common_name": sp["common_name"],
                    "observations": sp["observation_count"]
                }
                for sp in all_data["taxa"].get("Plantae", {}).get("species", [])[:200]
            ]
        },
        "seasonal_patterns": all_data["seasonal_patterns"]
    }

    processed_file = os.path.join(PROCESSED_DATA_DIR, "inaturalist_baseline.json")
    with open(processed_file, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    print(f"Processed data saved to: {processed_file}")

    # Print final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total species across all taxa: {all_data['summary']['total_species']}")
    for taxon, count in all_data["summary"]["species_by_taxon"].items():
        print(f"  {taxon}: {count} species")

    return all_data

if __name__ == "__main__":
    main()
