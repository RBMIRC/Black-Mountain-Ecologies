"""
Configuration for BMC Ecology Data Collection
Black Mountain College (1933-1957)
"""

# Location
LOCATION = {
    "name": "Black Mountain, NC",
    "latitude": 35.5951,
    "longitude": -82.5515,
    "elevation_m": 670
}

# Time period
START_YEAR = 1933
END_YEAR = 1957

# Bounding box for biodiversity queries (approximate region)
BBOX = {
    "lat_min": 35.0,
    "lat_max": 36.0,
    "lon_min": -83.0,
    "lon_max": -82.0
}

# API configurations
NOAA_API_KEY = None  # Set via environment variable NOAA_API_KEY
NOAA_STATION = "GHCND:USW00003812"  # Asheville Regional Airport

# Rate limiting
API_DELAY_SECONDS = 0.5  # Delay between API calls

# Paths
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
