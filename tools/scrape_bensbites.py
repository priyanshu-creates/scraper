"""
Ben's Bites Scraper
Scrapes latest AI news articles from Ben's Bites (Substack)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
from dateutil import parser as date_parser

# Configuration
SOURCE_NAME = "bens_bites"
BASE_URL = "https://www.bensbites.com"
USER_AGENT = "AI-News-Dashboard/1.0 (Educational Project)"
RATE_LIMIT_DELAY = 1  # seconds between requests
MAX_RETRIES = 3

def get_cutoff_time():
    """Calculate 24-hour cutoff time"""
    return datetime.now() - timedelta(hours=24)

def fetch_page(url, retries=0):
    """Fetch page with retry logic"""
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        if retries < MAX_RETRIES:
            wait_time = 2 ** retries  # Exponential backoff
            print(f"Error fetching {url}: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return fetch_page(url, retries + 1)
        else:
            print(f"Failed to fetch {url} after {MAX_RETRIES} retries: {e}")
            return None

def parse_articles(html):
    """Parse articles from Ben's Bites HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    
    # Find article links (Substack structure)
    # Look for post listings - adjust selectors based on actual structure
    post_links = soup.find_all('a', class_='post-preview-title')
    
    if not post_links:
        # Fallback: try finding any links in article containers
        post_links = soup.find_all('a', href=lambda x: x and '/p/' in x)
    
    cutoff = get_cutoff_time()
    
    for link in post_links:
        try:
            title = link.get_text(strip=True)
            url = link.get('href')
            
            # Ensure absolute URL
            if url and not url.startswith('http'):
                url = BASE_URL + url
            
            # Try to find published date (may need adjustment)
            date_elem = link.find_parent().find('time')
            published_date = None
            
            if date_elem and date_elem.get('datetime'):
                try:
                    published_date = date_parser.parse(date_elem['datetime'])
                except:
                    pass
            
            # If no date found or date is within 24h, include article
            if not published_date or published_date >= cutoff:
                article = {
                    "title": title,
                    "url": url,
                    "published_date": published_date.isoformat() if published_date else None,
                    "summary": None,  # Could extract if available
                    "content": None
                }
                articles.append(article)
                
        except Exception as e:
            print(f"Error parsing article: {e}")
            continue
    
    return articles

def scrape_bensbites():
    """Main scraper function"""
    print(f"[{SOURCE_NAME}] Starting scrape...")
    
    html = fetch_page(BASE_URL)
    if not html:
        print(f"[{SOURCE_NAME}] Failed to fetch page")
        return {"source": SOURCE_NAME, "scrape_timestamp": datetime.now().isoformat(), "articles": []}
    
    articles = parse_articles(html)
    
    result = {
        "source": SOURCE_NAME,
        "scrape_timestamp": datetime.now().isoformat(),
        "articles": articles
    }
    
    print(f"[{SOURCE_NAME}] Found {len(articles)} articles")
    return result

if __name__ == "__main__":
    # Run scraper
    data = scrape_bensbites()
    
    # Save to .tmp directory
    output_path = ".tmp/bensbites_articles.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[{SOURCE_NAME}] Saved to {output_path}")
