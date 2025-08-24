# utils/config.py : This file centralizes all our settings.


# --- Target Definition ---
TARGET_CITY = "pune"
SPECIALTIES = [
    "cardiologist",
    "dermatologist",
    "neurologist",
    "oncologist",
    "general-surgeon",
    "orthopedist",
    "neurosurgeon",
    "pediatrician",
    "gynecologist-obstetrician",
    "psychiatrist",
]

# --- Scraping Parameters ---

# Delay between requests to be respectful to the websites
RATE_LIMIT_SECONDS = 2
# Number of times to retry a failed request
MAX_RETRIES = 3
# Factor for exponential backoff (e.g., delay * factor^retry_attempt)
BACKOFF_FACTOR = 0.5
# Timeout for a request in seconds
REQUEST_TIMEOUT = 20

# --- Base URLs ---

# Using string formatting to easily insert city and specialty
BASE_URLS = {
    "practo": f"https://www.practo.com/{TARGET_CITY}",
    "justdial": f"https://www.justdial.com/{TARGET_CITY.capitalize()}"
}

# --- Headers & Proxies ---

# A list of user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]


# IMPORTANT: Populate this list with your own proxies
# Example format: "http://user:pass@host:port"
PROXY_LIST = [
    # "http://proxy1.com:8080",
    # "http://user:pass@proxy2.com:1234",
]

# --- Output Configuration ---
OUTPUT_FILE_PATH = "../output/unique_doctor_urls.csv"