"""
E-commerce Price Scraper
Collects product prices from various e-commerce websites
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import time
from config import HEADERS, PRICE_DATA_FILE, DATA_DIR
import os

class PriceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
    def extract_price(self, text):
        """Extract numeric price from text string"""
        # Remove currency symbols and extract numbers
        price_pattern = r'[\d,]+\.?\d*'
        matches = re.findall(price_pattern, text)
        if matches:
            # Take the first match and remove commas
            price_str = matches[0].replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                return None
        return None
    
    def scrape_generic_product(self, url, price_selector=None):
        """
        Scrape product information from a generic e-commerce page
        
        Args:
            url: Product page URL
            price_selector: CSS selector for price element (optional)
        
        Returns:
            dict with product info or None if scraping fails
        """
        try:
            print(f"🔍 Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Try to extract price using common patterns
            price = None
            price_text = None
            
            # Common price selectors for various e-commerce sites
            common_selectors = [
                '.price',
                '.a-price-whole',  # Amazon
                '[data-price]',
                '.product-price',
                '#priceblock_dealprice',
                '#priceblock_ourprice',
                '.price-current',
                '[itemprop="price"]'
            ]
            
            if price_selector:
                common_selectors.insert(0, price_selector)
            
            for selector in common_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    price = self.extract_price(price_text)
                    if price:
                        break
            
            # Try to get product title
            title = None
            title_selectors = ['h1', '.product-title', '#productTitle', '[itemprop="name"]']
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    break
            
            if not title:
                title = url.split('/')[-1][:50]  # Use URL as fallback
            
            return {
                'title': title,
                'url': url,
                'price': price,
                'price_text': price_text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'success' if price else 'price_not_found'
            }
            
        except requests.RequestException as e:
            print(f"❌ Error scraping {url}: {e}")
            return {
                'title': url,
                'url': url,
                'price': None,
                'price_text': None,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': f'error: {str(e)}'
            }
    
    def scrape_demo_data(self):
        """
        Generate demo price data for testing without actual scraping
        """
        import random
        
        products = [
            {'name': 'Laptop Computer', 'base_price': 899.99},
            {'name': 'Wireless Mouse', 'base_price': 29.99},
            {'name': 'Mechanical Keyboard', 'base_price': 89.99},
            {'name': 'USB-C Hub', 'base_price': 49.99},
            {'name': '27" Monitor', 'base_price': 299.99}
        ]
        
        print("📊 Generating demo price data...")
        
        data = []
        base_date = datetime.now()
        
        # Generate 30 days of historical data
        for day_offset in range(30, 0, -1):
            timestamp = base_date - timedelta(days=day_offset)
            timestamp = timestamp.replace(hour=12, minute=0, second=0, microsecond=0)
            
            for product in products:
                # Add random price fluctuation (±10%)
                variation = random.uniform(-0.10, 0.10)
                price = round(product['base_price'] * (1 + variation), 2)
                
                data.append({
                    'title': product['name'],
                    'url': f'https://example.com/{product["name"].lower().replace(" ", "-")}',
                    'price': price,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'success'
                })
        
        print(f"✅ Generated {len(data)} demo records")
        return data
    
    def save_to_csv(self, data):
        """Save scraped data to CSV file"""
        df_new = pd.DataFrame(data)
        
        # Load existing data if file exists
        if os.path.exists(PRICE_DATA_FILE):
            df_existing = pd.read_csv(PRICE_DATA_FILE)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        # Remove duplicates
        df_combined = df_combined.drop_duplicates(
            subset=['url', 'timestamp'], 
            keep='last'
        )
        
        df_combined.to_csv(PRICE_DATA_FILE, index=False)
        print(f"✅ Saved data to {PRICE_DATA_FILE}")
        return df_combined


def main():
    """Main execution function"""
    scraper = PriceScraper()
    
    # For demo purposes, generate sample data
    print("🚀 E-commerce Price Monitor - Demo Mode")
    print("=" * 60)
    
    demo_data = scraper.scrape_demo_data()
    df = scraper.save_to_csv(demo_data)
    
    print(f"\n📊 Collected {len(demo_data)} price records")
    print(f"📁 Data saved to: {PRICE_DATA_FILE}")
    print("\n" + "=" * 60)
    print("✅ Demo data generation complete!")
    print("\nNext step: Run analyzer.py to visualize price trends")


if __name__ == "__main__":
    main()