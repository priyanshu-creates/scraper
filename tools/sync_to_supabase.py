"""
Sync to Supabase
Uploads merged articles to Supabase database
"""

import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    print("Please set these variables to sync with Supabase")
    # Don't crash if credentials missing, just exit gracefully
    exit(0)

supabase: Client = create_client(url, key)

def sync_articles():
    """Sync articles from .tmp/all_articles.json to Supabase"""
    print("[sync] Starting sync to Supabase...")
    
    try:
        with open(".tmp/all_articles.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            articles = data.get("articles", [])
            
        if not articles:
            print("[sync] No articles to sync")
            return

        print(f"[sync] Found {len(articles)} articles to sync")
        
        count = 0
        errors = 0
        
        for article in articles:
            try:
                # Prepare payload matches schema
                payload = {
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "source": article.get("source"),
                    "published_date": article.get("published_date"),
                    "summary": article.get("summary"),
                    "scraped_at": article.get("scraped_at")
                    # created_at is auto-generated
                }
                
                # Upsert based on URL (unique constraint)
                # usage: supabase.table("articles").upsert(payload, on_conflict="url").execute()
                response = supabase.table("articles").upsert(
                    payload, 
                    on_conflict="url"
                ).execute()
                
                count += 1
                
            except Exception as e:
                print(f"[sync] Error syncing article {article.get('url')}: {e}")
                errors += 1
                
        print(f"[sync] Completed: {count} upserted, {errors} errors")
        
    except FileNotFoundError:
        print("[sync] .tmp/all_articles.json not found. Run scrapers first.")
    except Exception as e:
        print(f"[sync] Unexpected error: {e}")

if __name__ == "__main__":
    sync_articles()
