"""
Scraper Orchestrator
Runs all scrapers in sequence and merges results
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # Append to log file
    log_path = Path(".tmp/scraper_log.txt")
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")

def run_script(script_name):
    """Run a Python script and return success status"""
    log(f"Running {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, f"tools/{script_name}"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            log(f"✓ {script_name} completed successfully")
            return True
        else:
            log(f"✗ {script_name} failed with code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        log(f"✗ {script_name} timed out")
        return False
    except Exception as e:
        log(f"✗ {script_name} error: {e}")
        return False

def main():
    """Main orchestrator"""
    log("=" * 60)
    log("Starting scraper pipeline")
    log("=" * 60)
    
    # Ensure .tmp directory exists
    Path(".tmp").mkdir(exist_ok=True)
    
    # Run scrapers
    scrapers = [
        "scrape_bensbites.py",
        "scrape_airundown.py"
    ]
    
    results = {}
    for scraper in scrapers:
        results[scraper] = run_script(scraper)
    
    # Run merger
    log("Merging articles...")
    results["merge_articles.py"] = run_script("merge_articles.py")
    
    # Sync to Supabase
    log("Syncing to Supabase...")
    results["sync_to_supabase.py"] = run_script("sync_to_supabase.py")
    
    # Summary
    log("=" * 60)
    log("Pipeline Summary:")
    for script, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        log(f"  {script}: {status}")
    
    all_success = all(results.values())
    if all_success:
        log("Pipeline completed successfully!")
        log("Output: .tmp/all_articles.json")
    else:
        log("Pipeline completed with errors")
    
    log("=" * 60)
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
