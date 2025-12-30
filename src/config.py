"""Configuration settings for E-commerce Price Monitor"""

import os
from datetime import datetime

# Project directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CSV file for storing price data
PRICE_DATA_FILE = os.path.join(DATA_DIR, 'price_history.csv')

# Headers for web scraping (to avoid being blocked)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Example product URLs (will be replaced with user-defined URLs)
EXAMPLE_PRODUCTS = [
    {
        'name': 'Python Programming Book',
        'url': 'https://www.amazon.com/dp/example',
        'selector': '.a-price-whole'  # CSS selector for price
    }
]