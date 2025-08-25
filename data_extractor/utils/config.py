# data_extractor/utils/config.py

# --- File Paths ---
# --- THIS IS THE NEW, MORE ROBUST CODE ---
INPUT_URL_FILE = "output/unique_doctor_urls.csv"
OUTPUT_PROCESSED_FILE = "output/structured_doctor_data.json"
OUTPUT_RAW_FILE = "output/raw_scraped_data.json"

# --- Scraping Parameters ---
# We can reuse some parameters from Module 1's config if needed,
# but it's good practice to keep them separate.
RATE_LIMIT_SECONDS = 1.5
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5
REQUEST_TIMEOUT = 25

# --- Geolocation Validation ---
# A bounding box for Pune city limits. We will check if a doctor's
# coordinates fall within this box.
# You can get these values from sites like https://boundingbox.klokantech.com/
PUNE_BOUNDING_BOX = {
    "min_lat": 18.40,
    "max_lat": 18.64,
    "min_lon": 73.75,
    "max_lon": 74.00,
}

# --- Clinic Name Standardization ---
# A list of standardized names for major hospitals/clinics in Pune.
# The fuzzy matching algorithm will match scraped names against this list.
STANDARDIZED_CLINIC_NAMES = [
    "Jehangir Hospital",
    "Ruby Hall Clinic",
    "Sahyadri Super Speciality Hospital",
    "Manipal Hospital",
    "Deenanath Mangeshkar Hospital",
    "KEM Hospital",
    "Noble Hospital",
    "Aditya Birla Memorial Hospital",
    "Inamdar Multispeciality Hospital",
    "Poona Hospital and Research Centre"
]
FUZZY_MATCH_THRESHOLD = 85  # Score out of 100 for a name to be considered a match

# --- Headers & Proxies (can be copied from Module 1's config) ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
]

# IMPORTANT: Populate this list with your own proxies
PROXY_LIST = []

# Add or update:
EXPORT_CSV_FILE   = "output/doctors_data.csv"
EXPORT_EXCEL_FILE = "output/doctors_data.xlsx"

TEST_LIMIT = None
