
"""
Modal App for AI News Scraper
Runs every 24 hours to scrape, merge, and sync articles to Supabase.
"""

import modal
import sys
import os
import datetime

# Define the image with dependencies
# We install from requirements.txt and add local tools
image = (
    modal.Image.debian_slim()
    .pip_install(
        "requests",
        "beautifulsoup4",
        "python-dateutil",
        "feedparser",
        "supabase",
        "python-dotenv"
    )
    .add_local_dir("tools", remote_path="/root/tools")
)

app = modal.App("ai-news-scraper")

# Define schema for the secret we need
# User must create this secret in Modal dashboard or CLI:
# modal secret create supabase-secret SUPABASE_URL=... SUPABASE_KEY=...
supabase_secret = modal.Secret.from_name("supabase-secret")

@app.function(
    image=image,
    secrets=[supabase_secret],
    schedule=modal.Period(days=1),
    timeout=900  # 15 minutes timeout
)
def run_daily_scrape():
    print(f"[Modal] Starting daily scrape at {datetime.datetime.now()}")
    
    # Ensure tools can be imported
    if "/root" not in sys.path:
        sys.path.append("/root")
        
    try:
        # 1. Scrape Ben's Bites
        from tools.scrape_bensbites import scrape_bensbites
        print("[Modal] Running Ben's Bites scraper...")
        bb_data = scrape_bensbites()
        
        # 2. Scrape AI Rundown
        from tools.scrape_airundown import scrape_airundown
        print("[Modal] Running AI Rundown scraper...")
        ar_data = scrape_airundown()
        
        # 3. Merge Articles
        # We need to simulate the file writing/reading if tools rely on it,
        # OR we can pass data in memory if we refactor tools.
        # Since tools currently write to .tmp, we should check if they return data too.
        # Yes, they return data!
        
        # However, merge_articles usually reads from files.
        # Let's import merge_articles and see if we can pass data.
        from tools.merge_articles import merge_articles
        # merge_articles currently reads from .tmp json files.
        # In Modal, the filesystem is ephemeral, so we can write to .tmp there.
        
        os.makedirs(".tmp", exist_ok=True)
        import json
        
        with open(".tmp/bensbites_articles.json", "w") as f:
            json.dump(bb_data, f)
            
        with open(".tmp/airundown_articles.json", "w") as f:
            json.dump(ar_data, f)
            
        print("[Modal] Merging articles...")
        merged_data = merge_articles() # This reads from .tmp and writes to .tmp/all_articles.json
        
        # 4. Sync to Supabase
        from tools.sync_to_supabase import sync_articles
        print("[Modal] Syncing to Supabase...")
        # sync_articles reads from .tmp/all_articles.json
        sync_articles()
        
        print("[Modal] Daily scrape completed successfully!")
        
    except Exception as e:
        print(f"[Modal] Scrape failed: {e}")
        raise e

@app.local_entrypoint()
def main():
    print("Running scraper locally (in Modal sandbox)...")
    run_daily_scrape.remote()
