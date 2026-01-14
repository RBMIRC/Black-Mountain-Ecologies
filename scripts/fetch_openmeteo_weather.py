#!/usr/bin/env python3
"""
Fetch historical weather data from Open-Meteo API
Data available from 1940 onwards
For 1933-1939, estimates will be generated based on regional climate averages
"""

import json
import os
import time
from datetime import datetime
import requests
from config import LOCATION, START_YEAR, END_YEAR, RAW_DATA_DIR, PROCESSED_DATA_DIR, API_DELAY_SECONDS

# Open-Meteo Historical API only has data from 1940
OPENMETEO_START_YEAR = 1940

def fetch_openmeteo_data(start_year, end_year):
    """Fetch daily weather data from Open-Meteo Historical API"""

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": LOCATION["latitude"],
        "longitude": LOCATION["longitude"],
        "start_date": f"{start_year}-01-01",
        "end_date": f"{end_year}-12-31",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,snowfall_sum",
        "timezone": "America/New_York"
    }

    print(f"Fetching Open-Meteo data for {start_year}-{end_year}...")

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def process_daily_to_monthly(raw_data):
    """Aggregate daily data to monthly summaries"""

    if not raw_data or "daily" not in raw_data:
        return None

    daily = raw_data["daily"]
    dates = daily["time"]
    temp_max = daily["temperature_2m_max"]
    temp_min = daily["temperature_2m_min"]
    precip = daily["precipitation_sum"]

    # Organize by year and month
    monthly_data = {}

    for i, date_str in enumerate(dates):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        year = date.year
        month = date.month

        key = (year, month)
        if key not in monthly_data:
            monthly_data[key] = {
                "temp_max": [],
                "temp_min": [],
                "precip": []
            }

        if temp_max[i] is not None:
            monthly_data[key]["temp_max"].append(temp_max[i])
        if temp_min[i] is not None:
            monthly_data[key]["temp_min"].append(temp_min[i])
        if precip[i] is not None:
            monthly_data[key]["precip"].append(precip[i])

    # Calculate monthly averages
    result = {}
    for (year, month), data in monthly_data.items():
        if year not in result:
            result[year] = {"monthly": [], "source": "Open-Meteo Historical API"}

        month_record = {
            "month": month,
            "temp_max_avg": round(sum(data["temp_max"]) / len(data["temp_max"]), 1) if data["temp_max"] else None,
            "temp_min_avg": round(sum(data["temp_min"]) / len(data["temp_min"]), 1) if data["temp_min"] else None,
            "precip_mm": round(sum(data["precip"]), 1) if data["precip"] else None,
            "days_recorded": len(data["temp_max"])
        }
        result[year]["monthly"].append(month_record)

    # Sort monthly data and calculate annual summaries
    for year in result:
        result[year]["monthly"].sort(key=lambda x: x["month"])

        # Calculate annual averages
        all_temp_max = [m["temp_max_avg"] for m in result[year]["monthly"] if m["temp_max_avg"] is not None]
        all_temp_min = [m["temp_min_avg"] for m in result[year]["monthly"] if m["temp_min_avg"] is not None]
        all_precip = [m["precip_mm"] for m in result[year]["monthly"] if m["precip_mm"] is not None]

        result[year]["annual_avg_temp_max"] = round(sum(all_temp_max) / len(all_temp_max), 1) if all_temp_max else None
        result[year]["annual_avg_temp_min"] = round(sum(all_temp_min) / len(all_temp_min), 1) if all_temp_min else None
        result[year]["annual_avg_temp"] = round((result[year]["annual_avg_temp_max"] + result[year]["annual_avg_temp_min"]) / 2, 1) if result[year]["annual_avg_temp_max"] and result[year]["annual_avg_temp_min"] else None
        result[year]["total_precip_mm"] = round(sum(all_precip), 1) if all_precip else None

    return result

def generate_estimates_1933_1939(processed_1940_1957):
    """
    Generate estimates for 1933-1939 based on 1940-1949 averages
    These are marked as estimated
    """

    # Calculate average patterns from 1940-1949
    reference_years = [y for y in range(1940, 1950) if y in processed_1940_1957]

    if not reference_years:
        print("No reference data available for estimates")
        return {}

    # Calculate average monthly patterns
    monthly_averages = {m: {"temp_max": [], "temp_min": [], "precip": []} for m in range(1, 13)}

    for year in reference_years:
        for month_data in processed_1940_1957[year]["monthly"]:
            m = month_data["month"]
            if month_data["temp_max_avg"]:
                monthly_averages[m]["temp_max"].append(month_data["temp_max_avg"])
            if month_data["temp_min_avg"]:
                monthly_averages[m]["temp_min"].append(month_data["temp_min_avg"])
            if month_data["precip_mm"]:
                monthly_averages[m]["precip"].append(month_data["precip_mm"])

    # Generate estimates for 1933-1939
    estimates = {}
    for year in range(1933, 1940):
        estimates[year] = {
            "monthly": [],
            "source": "Estimated from 1940-1949 regional averages",
            "estimated": True
        }

        for m in range(1, 13):
            avg_temp_max = round(sum(monthly_averages[m]["temp_max"]) / len(monthly_averages[m]["temp_max"]), 1) if monthly_averages[m]["temp_max"] else None
            avg_temp_min = round(sum(monthly_averages[m]["temp_min"]) / len(monthly_averages[m]["temp_min"]), 1) if monthly_averages[m]["temp_min"] else None
            avg_precip = round(sum(monthly_averages[m]["precip"]) / len(monthly_averages[m]["precip"]), 1) if monthly_averages[m]["precip"] else None

            estimates[year]["monthly"].append({
                "month": m,
                "temp_max_avg": avg_temp_max,
                "temp_min_avg": avg_temp_min,
                "precip_mm": avg_precip,
                "estimated": True
            })

        # Calculate annual summaries
        all_temp_max = [m["temp_max_avg"] for m in estimates[year]["monthly"] if m["temp_max_avg"]]
        all_temp_min = [m["temp_min_avg"] for m in estimates[year]["monthly"] if m["temp_min_avg"]]
        all_precip = [m["precip_mm"] for m in estimates[year]["monthly"] if m["precip_mm"]]

        estimates[year]["annual_avg_temp_max"] = round(sum(all_temp_max) / len(all_temp_max), 1) if all_temp_max else None
        estimates[year]["annual_avg_temp_min"] = round(sum(all_temp_min) / len(all_temp_min), 1) if all_temp_min else None
        estimates[year]["annual_avg_temp"] = round((estimates[year]["annual_avg_temp_max"] + estimates[year]["annual_avg_temp_min"]) / 2, 1) if estimates[year]["annual_avg_temp_max"] and estimates[year]["annual_avg_temp_min"] else None
        estimates[year]["total_precip_mm"] = round(sum(all_precip), 1) if all_precip else None

    return estimates

def main():
    """Main function to fetch and process weather data"""

    # Create directories if they don't exist
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Fetch data from Open-Meteo (1940-1957)
    raw_data = fetch_openmeteo_data(OPENMETEO_START_YEAR, END_YEAR)

    if raw_data:
        # Save raw data
        raw_file = os.path.join(RAW_DATA_DIR, "openmeteo_raw_1940_1957.json")
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2)
        print(f"Raw data saved to {raw_file}")

        # Process to monthly data
        processed = process_daily_to_monthly(raw_data)

        if processed:
            # Generate estimates for 1933-1939
            estimates = generate_estimates_1933_1939(processed)

            # Merge estimates with actual data
            all_weather = {**estimates, **processed}

            # Save processed data
            processed_file = os.path.join(PROCESSED_DATA_DIR, "weather_1933_1957.json")
            with open(processed_file, "w", encoding="utf-8") as f:
                json.dump(all_weather, f, indent=2, ensure_ascii=False)
            print(f"Processed weather data saved to {processed_file}")

            # Print summary
            print("\n=== Weather Data Summary ===")
            for year in sorted(all_weather.keys()):
                data = all_weather[year]
                est = " (estimated)" if data.get("estimated") else ""
                print(f"{year}: Avg temp {data.get('annual_avg_temp')}°C, Precip {data.get('total_precip_mm')}mm{est}")

            return all_weather

    return None

if __name__ == "__main__":
    main()
