"""
Ben's Bites Scraper (RSS)
Scrapes latest AI news articles from Ben's Bites via RSS Feed
"""

import feedparser
from datetime import datetime, timedelta
import json
import time
from dateutil import parser as date_parser

# Configuration
SOURCE_NAME = "bens_bites"
RSS_URL = "https://www.bensbites.com/feed"
USER_AGENT = "AI-News-Dashboard/1.0 (Educational Project)"

def get_cutoff_time():
    """Calculate 24-hour cutoff time"""
    return datetime.now() - timedelta(hours=24)

def scrape_bensbites():
    """Main scraper function using RSS"""
    print(f"[{SOURCE_NAME}] Starting RSS scrape from {RSS_URL}...")
    
    try:
        # Parse RSS Feed
        feed = feedparser.parse(RSS_URL)
        
        if feed.bozo:
            print(f"[{SOURCE_NAME}] Warning: Feed parsing error: {feed.bozo_exception}")
            # Continue anyway as feedparser often parses despite errors
            
        if not feed.entries:
            print(f"[{SOURCE_NAME}] No entries found in feed.")
            return {"source": SOURCE_NAME, "scrape_timestamp": datetime.now().isoformat(), "articles": []}
            
        cutoff = get_cutoff_time()
        articles = []
        
        print(f"[{SOURCE_NAME}] Processing {len(feed.entries)} entries...")
        
        for entry in feed.entries:
            try:
                # Extract fields
                title = entry.get('title', 'No Title')
                url = entry.get('link', '')
                published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                summary = entry.get('summary', '') or entry.get('description', '')
                
                # Parse date
                published_date = None
                if published_parsed:
                    published_date = datetime(*published_parsed[:6])
                elif entry.get('published'):
                    published_date = date_parser.parse(entry['published'])
                
                # Check date cutoff (defaults to inclusion if no date found, to be safe)
                if not published_date or published_date >= cutoff:
                    # Clean summary (remove HTML tags if simple display needed, or keep for rich text)
                    # For now, we'll keep it raw or truncate
                    clean_summary = summary.split('<')[0] if '<' in summary else summary
                    clean_summary = clean_summary[:200] + "..." if len(clean_summary) > 200 else clean_summary

                    article = {
                        "title": title,
                        "url": url,
                        "published_date": published_date.isoformat() if published_date else None,
                        "summary": clean_summary,
                        "source": SOURCE_NAME
                    }
                    articles.append(article)
            except Exception as e:
                print(f"[{SOURCE_NAME}] Error processing entry: {e}")
                continue
        
        result = {
            "source": SOURCE_NAME,
            "scrape_timestamp": datetime.now().isoformat(),
            "articles": articles
        }
        
        print(f"[{SOURCE_NAME}] Found {len(articles)} articles from last 24h")
        return result

    except Exception as e:
        print(f"[{SOURCE_NAME}] Fatal error: {e}")
        return {"source": SOURCE_NAME, "scrape_timestamp": datetime.now().isoformat(), "articles": []}

if __name__ == "__main__":
    # Run scraper
    data = scrape_bensbites()
    
    # Save to .tmp directory
    output_path = ".tmp/bensbites_articles.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[{SOURCE_NAME}] Saved to {output_path}")
