"""
AI Rundown Scraper
Scrapes latest AI news articles from The Rundown AI (therundown.ai)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
from dateutil import parser as date_parser

# Configuration
SOURCE_NAME = "ai_rundown"
BASE_URL = "https://www.therundown.ai"
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
    """Parse articles from AI Rundown HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    
    # Find article links (pattern: /p/{slug})
    # Look for H3 headings or article cards
    article_links = soup.find_all('a', href=lambda x: x and '/p/' in x)
    
    cutoff = get_cutoff_time()
    seen_urls = set()  # Deduplicate
    
    for link in article_links:
        try:
            url = link.get('href')
            
            # Skip if already processed
            if url in seen_urls:
                continue
            
            # Ensure absolute URL
            if url and not url.startswith('http'):
                url = BASE_URL + url
            
            seen_urls.add(url)
            
            # Get title - try multiple approaches
            title = None
            
            # Try getting text from link itself
            if link.get_text(strip=True):
                title = link.get_text(strip=True)
            
            # Try finding H3 within or near link
            h3 = link.find('h3') or link.find_parent().find('h3')
            if h3:
                title = h3.get_text(strip=True)
            
            if not title:
                continue  # Skip if no title found
            
            # Try to find published date
            date_elem = link.find_parent().find('time')
            published_date = None
            
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                try:
                    published_date = date_parser.parse(date_text)
                except:
                    pass
            
            # Extract summary if available (PLUS section)
            summary = None
            parent = link.find_parent()
            if parent:
                # Look for description or summary text
                desc = parent.find('p')
                if desc:
                    summary = desc.get_text(strip=True)
            
            # If no date found or date is within 24h, include article
            if not published_date or published_date >= cutoff:
                article = {
                    "title": title,
                    "url": url,
                    "published_date": published_date.isoformat() if published_date else None,
                    "summary": summary,
                    "content": None
                }
                articles.append(article)
                
        except Exception as e:
            print(f"Error parsing article: {e}")
            continue
    
    return articles

def scrape_airundown():
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
    data = scrape_airundown()
    
    # Save to .tmp directory
    output_path = ".tmp/airundown_articles.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[{SOURCE_NAME}] Saved to {output_path}")
