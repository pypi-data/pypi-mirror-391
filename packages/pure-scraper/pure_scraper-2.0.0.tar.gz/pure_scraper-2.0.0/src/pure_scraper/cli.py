# src/pure_scraper/cli.py

import sys
from pure_scraper.parser import PureScraper
from pure_scraper.fetcher import fetch_html

def main():
    if len(sys.argv) < 2:
        print("Usage: pure-scraper <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"🔍 Fetching: {url}")
    html = fetch_html(url)
    scraper = PureScraper(html)
    print("✅ Page fetched successfully. Parsed title:")
    print(scraper.get_title() if hasattr(scraper, "get_title") else "No title method found.")

if __name__ == "__main__":
    main()
