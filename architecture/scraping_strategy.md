# Scraping Strategy SOP

## Goal
Extract latest AI news articles from Ben's Bites and The Rundown AI within the last 24 hours.

## Data Requirements

### Required Fields
- `title` (string): Article headline
- `url` (string): Full article URL
- `source` (string): "bens_bites" | "ai_rundown"
- `published_date` (ISO 8601 datetime): When article was published
- `scraped_at` (ISO 8601 datetime): When we scraped it

### Optional Fields
- `summary` (string): Article summary/description
- `content` (string): Full article text (if available)

## Scraping Rules

### Ben's Bites (bensbites.com)
- **Platform:** Substack
- **Target URL:** https://www.bensbites.com or RSS feed
- **Approach:** 
  1. Try RSS feed first (faster, more reliable)
  2. Fallback to web scraping if RSS unavailable
- **Selectors (if web scraping):**
  - Article links: Look for post listings
  - Dates: Parse from post metadata
- **Rate Limit:** Max 1 request per second
- **Error Handling:** If 404/500, log error and continue

### AI Rundown (therundown.ai)
- **Platform:** Custom website
- **Target URL:** https://www.therundown.ai
- **Approach:** Web scraping of "Latest Articles" section
- **Selectors:**
  - Articles container: Main content area with article listings
  - Article title: H3 headings
  - Article URL: Links within article cards (pattern: `/p/{slug}`)
  - Published date: Parse from article metadata or timestamps
- **Rate Limit:** Max 1 request per second
- **Error Handling:** If structure changes, log detailed error with HTML snippet

## 24-Hour Filtering
- Calculate cutoff: `current_time - 24 hours`
- Only include articles where `published_date >= cutoff`
- If published_date unavailable, include article (mark as "unknown date")

## Output Format
```json
{
  "source": "bens_bites",
  "scrape_timestamp": "2026-02-17T21:35:00+05:30",
  "articles": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "published_date": "2026-02-17T10:00:00Z",
      "summary": "Optional summary",
      "content": "Optional content"
    }
  ]
}
```

## Ethical Scraping
- Respect robots.txt
- Use descriptive User-Agent header
- Implement rate limiting (1 req/sec)
- Cache results to avoid repeated requests
- Don't overwhelm servers

## Error Handling
1. **Network Errors:** Retry up to 3 times with exponential backoff
2. **Parse Errors:** Log HTML snippet, continue with other articles
3. **No Articles Found:** Log warning, return empty array
4. **Invalid Dates:** Use scrape timestamp as fallback

## Self-Annealing
When scrapers break due to website changes:
1. Update this SOP with new selectors/structure
2. Update the corresponding Python tool
3. Document the change in findings.md
