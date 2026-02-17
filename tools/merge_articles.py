"""
Article Merger
Combines articles from multiple sources, deduplicates, and sorts
"""

import json
from datetime import datetime
from pathlib import Path
import uuid

def load_json(filepath):
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def merge_articles():
    """Merge articles from all sources"""
    print("[merge] Starting merge process...")
    
    # Load data from both sources
    bensbites_data = load_json(".tmp/bensbites_articles.json")
    airundown_data = load_json(".tmp/airundown_articles.json")
    
    all_articles = []
    seen_urls = set()
    
    # Process Ben's Bites articles
    if bensbites_data and bensbites_data.get('articles'):
        for article in bensbites_data['articles']:
            url = article.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                # Add unique ID and source
                article['id'] = str(uuid.uuid4())
                article['source'] = 'bens_bites'
                article['scraped_at'] = bensbites_data.get('scrape_timestamp')
                all_articles.append(article)
    
    # Process AI Rundown articles
    if airundown_data and airundown_data.get('articles'):
        for article in airundown_data['articles']:
            url = article.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                # Add unique ID and source
                article['id'] = str(uuid.uuid4())
                article['source'] = 'ai_rundown'
                article['scraped_at'] = airundown_data.get('scrape_timestamp')
                all_articles.append(article)
    
    # Sort by published date (newest first)
    # Articles without dates go to the end
    def sort_key(article):
        pub_date = article.get('published_date')
        if pub_date:
            try:
                return datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            except:
                return datetime.min
        return datetime.min
    
    all_articles.sort(key=sort_key, reverse=True)
    
    # Calculate stats
    from datetime import timedelta
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    
    new_count = 0
    for article in all_articles:
        pub_date = article.get('published_date')
        is_new = False
        if pub_date:
            try:
                pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                is_new = pub_dt >= cutoff
            except:
                pass
        article['is_new'] = is_new
        article['is_saved'] = False  # Default for Phase 1
        if is_new:
            new_count += 1
    
    # Create output
    result = {
        "articles": all_articles,
        "last_updated": datetime.now().isoformat(),
        "total_count": len(all_articles),
        "new_count": new_count,
        "saved_count": 0  # Phase 2 feature
    }
    
    print(f"[merge] Merged {len(all_articles)} articles ({new_count} new)")
    return result

if __name__ == "__main__":
    # Run merger
    data = merge_articles()
    
    # Save to .tmp directory
    output_path = ".tmp/all_articles.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[merge] Saved to {output_path}")
