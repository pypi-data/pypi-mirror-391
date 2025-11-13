# mlcrawler Library API

`mlcrawler` can now be used as a Python library in your own projects! This guide covers the programmatic API for crawling websites and processing content with callbacks.

## Installation

Install as a package:

```bash
# From PyPI (once published)
pip install mlcrawler

# Or install locally in development mode
uv pip install -e .

# Or add to your project with uv
uv add mlcrawler
```

## Quick Start

```python
import asyncio
from mlcrawler import Crawler, Page

async def process_page(page: Page):
    """Called for each crawled page."""
    print(f"{page.title}: {page.url}")
    print(f"Content: {len(page.markdown)} chars")

async def main():
    crawler = Crawler(
        max_depth=2,
        max_pages=50,
        follow_links=True,
    )
    
    await crawler.crawl(
        "https://example.com",
        callback=process_page
    )

asyncio.run(main())
```

## Core Classes

### `Crawler`

Main entry point for crawling websites.

**Constructor Parameters:**

```python
Crawler(
    user_agent="mlcrawler/0.1 (+contact-url)",
    max_depth=2,                    # Maximum crawl depth (0 = unlimited)
    max_pages=0,                    # Max pages to crawl (0 = unlimited)
    main_article_only=False,        # Extract main content only
    cache_dir=".cache/mlcrawler",   # Cache directory
    follow_links=True,              # Follow discovered links
    same_domain_only=True,          # Restrict to same domain
    obey_robots=True,               # Respect robots.txt
    rate_limit_ms=500,              # Per-host delay (milliseconds)
    concurrency=8,                  # Global concurrency limit
    per_host_concurrency=4,         # Per-host concurrency
    include_patterns=None,          # URL regex patterns to include
    exclude_patterns=None,          # URL regex patterns to exclude
    remove_selectors=None,          # CSS selectors to remove
    save_to_disk=False,             # Save markdown to disk
    output_dir="output",            # Output directory (if saving)
    config_files=None,              # TOML config files to load
)
```

**Methods:**

#### `crawl(url, *, callback=None, follow_links=None)`

Crawl a single seed URL.

```python
pages = await crawler.crawl(
    "https://example.com",
    callback=process_page,
    follow_links=True,
)
```

**Returns:** `List[Page]`

#### `crawl_many(urls, *, callback=None, follow_links=None)`

Crawl multiple seed URLs.

```python
pages = await crawler.crawl_many(
    ["https://example.com", "https://another.com"],
    callback=process_page,
)
```

**Returns:** `List[Page]`

#### `crawl_sitemap(sitemap_url, *, callback=None)`

Crawl from a sitemap.

```python
pages = await crawler.crawl_sitemap(
    "https://example.com/sitemap.xml",
    callback=process_page,
)
```

**Returns:** `List[Page]`

#### `stream(url, *, follow_links=None)`

Stream pages as they're crawled (async generator).

```python
async with crawler:
    async for page in crawler.stream("https://example.com"):
        process(page)
        if should_stop():
            break
```

**Yields:** `Page` objects

#### `on(event)`

Decorator to register event handlers.

```python
@crawler.on("fetch")
async def on_fetch(url: str):
    print(f"Fetching {url}")

@crawler.on("page")
async def on_page(page: Page):
    print(f"Got {page.title}")

@crawler.on("error")
async def on_error(url: str, error: Exception):
    print(f"Error: {error}")

@crawler.on("complete")
async def on_complete(stats: dict):
    print(f"Done! {stats['pages']} pages")
```

**Events:**
- `"fetch"` - Before fetching a URL `(url: str)`
- `"page"` - After processing a page `(page: Page)`
- `"error"` - On error `(url: str, error: Exception)`
- `"complete"` - When crawl completes `(stats: dict)`

#### `from_config(config_files, **overrides)`

Create a Crawler from configuration file(s).

```python
crawler = Crawler.from_config("crawler.toml")

# Or merge multiple configs
crawler = Crawler.from_config(
    ["defaults.toml", "site.toml"],
    max_pages=100,
)
```

### `Page`

Rich dataclass representing a crawled page.

**Attributes:**

```python
page.url                 # Original URL
page.title               # Extracted title
page.markdown            # Markdown content
page.html                # Original HTML
page.text                # Plain text (no markup)

# Metadata
page.metadata            # Complete metadata dict
page.fetched_at          # Fetch timestamp (datetime)
page.status_code         # HTTP status code
page.content_hash        # SHA256 hash

# Crawl context
page.depth               # Crawl depth (0 for seed)
page.source              # "seed", "sitemap", or "link"
page.extraction_mode     # "article" or "fullpage"

# Optional trafilatura metadata
page.author              # Author (if available)
page.date                # Publish date (if available)
page.description         # Description (if available)
page.sitename            # Site name (if available)

# Cache info
page.from_cache          # Whether from cache
page.cache_path          # Cache file path
page.headers             # HTTP headers
```

**Properties:**

```python
page.domain              # Domain from URL
page.is_seed             # True if seed URL
page.is_from_sitemap     # True if from sitemap
page.is_discovered_link  # True if discovered link
page.is_main_article     # True if article extraction
```

**Methods:**

```python
page.to_dict()           # Convert to dict for serialization
```

## Usage Patterns

### 1. Simple Callback Processing

Process each page as it's crawled:

```python
async def save_to_database(page: Page):
    db.insert({
        "url": page.url,
        "title": page.title,
        "content": page.markdown,
        "fetched_at": page.fetched_at,
    })

crawler = Crawler(max_pages=100)
await crawler.crawl("https://example.com", callback=save_to_database)
```

### 2. Event Hooks

React to different stages:

```python
crawler = Crawler()

@crawler.on("fetch")
async def log_fetch(url):
    logger.info(f"Fetching {url}")

@crawler.on("page")
async def process(page):
    await analyze_content(page)

@crawler.on("error")
async def handle_error(url, error):
    logger.error(f"Failed {url}: {error}")

await crawler.crawl("https://example.com")
```

### 3. Streaming for Memory Efficiency

Process pages one at a time without storing all in memory:

```python
async with Crawler(max_pages=1000) as crawler:
    async for page in crawler.stream("https://example.com"):
        process_and_discard(page)
```

### 4. Collect and Post-Process

Collect all pages then process:

```python
crawler = Crawler(max_depth=3)
pages = await crawler.crawl("https://example.com")

# Now process all pages
for page in pages:
    if page.is_main_article:
        extract_entities(page)
```

### 5. Multiple Seed URLs

Crawl multiple sites in one operation:

```python
sites = [
    "https://site1.com",
    "https://site2.com",
    "https://site3.com",
]

pages = await crawler.crawl_many(sites, callback=process_page)
```

### 6. Sitemap Crawling

Efficient crawling using sitemaps:

```python
pages = await crawler.crawl_sitemap(
    "https://example.com/sitemap.xml",
    callback=process_page,
)
```

### 7. Load from Config

Use TOML configuration files:

```python
# Load from file(s)
crawler = Crawler.from_config("crawler.toml")

# Or merge multiple configs with overrides
crawler = Crawler.from_config(
    ["defaults.toml", "site-specific.toml"],
    max_pages=50,  # Override
)
```

### 8. Context Manager for Cleanup

Ensure resources are cleaned up:

```python
async with Crawler() as crawler:
    pages = await crawler.crawl("https://example.com")
    # Resources automatically cleaned up
```

### 9. Custom Content Filtering

Remove unwanted elements:

```python
crawler = Crawler(
    remove_selectors=[
        "nav",           # Navigation
        "footer",        # Footer
        ".ads",          # Ads
        "#comments",     # Comments
        ".social-share", # Social buttons
    ],
    main_article_only=True,  # Extract main content only
)
```

### 10. URL Pattern Filtering

Control which URLs to crawl:

```python
crawler = Crawler(
    include_patterns=[
        r"https://example\.com/blog/.*",
        r"https://example\.com/docs/.*",
    ],
    exclude_patterns=[
        r".*/archive/.*",
        r".*/tag/.*",
        r".*/author/.*",
    ],
)
```

## Advanced Features

### Rate Limiting

Control request rate per host:

```python
crawler = Crawler(
    rate_limit_ms=1000,        # 1 second between requests
    per_host_concurrency=2,    # Max 2 concurrent per host
)
```

### Concurrency Control

Manage concurrent requests:

```python
crawler = Crawler(
    concurrency=16,            # 16 global concurrent requests
    per_host_concurrency=4,    # 4 per host
)
```

### Caching

Control caching behavior:

```python
crawler = Crawler(
    cache_dir=".cache/mycrawler",
    # Cache respects ETags and Last-Modified by default
)
```

### Main Article Extraction

Extract only main content using trafilatura:

```python
crawler = Crawler(main_article_only=True)

pages = await crawler.crawl("https://example.com")

for page in pages:
    if page.is_main_article:
        print(f"Extracted article: {page.title}")
    else:
        print(f"Full page: {page.title}")
```

### Save to Disk

Save markdown and metadata to files:

```python
crawler = Crawler(
    save_to_disk=True,
    output_dir="./scraped_content",
)

await crawler.crawl("https://example.com")
# Files saved to ./scraped_content/example.com/...
```

## Complete Example

Here's a complete example showing multiple features:

```python
import asyncio
import logging
from mlcrawler import Crawler, Page

# Set up logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Create crawler with custom config
    crawler = Crawler(
        user_agent="MyBot/1.0 (+https://mysite.com)",
        max_depth=3,
        max_pages=100,
        main_article_only=True,
        follow_links=True,
        same_domain_only=True,
        rate_limit_ms=500,
        concurrency=8,
        remove_selectors=["nav", "footer", ".ads"],
    )
    
    # Add event hooks
    @crawler.on("fetch")
    async def on_fetch(url):
        print(f"⬇️  {url}")
    
    @crawler.on("error")
    async def on_error(url, error):
        print(f"❌ {url}: {error}")
    
    # Process pages
    results = []
    
    async def process_page(page: Page):
        results.append({
            "url": page.url,
            "title": page.title,
            "word_count": len(page.text.split()),
            "depth": page.depth,
        })
        print(f"✅ {page.title} ({len(page.text.split())} words)")
    
    # Crawl
    await crawler.crawl(
        "https://example.com",
        callback=process_page
    )
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Pages: {len(results)}")
    print(f"   Total words: {sum(r['word_count'] for r in results)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Integration Examples

### Flask/FastAPI Integration

```python
from fastapi import FastAPI, BackgroundTasks
from mlcrawler import Crawler

app = FastAPI()

@app.post("/crawl")
async def crawl_site(url: str, background_tasks: BackgroundTasks):
    async def do_crawl():
        crawler = Crawler(max_pages=50)
        pages = await crawler.crawl(url)
        # Save to database, etc.
    
    background_tasks.add_task(do_crawl)
    return {"status": "started"}
```

### Jupyter Notebook

```python
# In a Jupyter cell
from mlcrawler import Crawler
import asyncio

crawler = Crawler(max_pages=10)
pages = await crawler.crawl("https://example.com")

# Analyze in pandas
import pandas as pd
df = pd.DataFrame([p.to_dict() for p in pages])
df.head()
```

### CLI Script

```python
#!/usr/bin/env python3
import asyncio
import sys
from mlcrawler import Crawler

async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    
    crawler = Crawler(max_depth=2)
    pages = await crawler.crawl(url)
    
    for page in pages:
        print(f"{page.title}: {page.url}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

Handle errors gracefully:

```python
crawler = Crawler()

@crawler.on("error")
async def handle_error(url: str, error: Exception):
    if isinstance(error, TimeoutError):
        log.warning(f"Timeout on {url}")
    elif isinstance(error, ValueError):
        log.error(f"Invalid content on {url}")
    else:
        log.exception(f"Unexpected error on {url}")

try:
    pages = await crawler.crawl("https://example.com")
except Exception as e:
    log.exception("Crawl failed completely")
```

## Best Practices

1. **Always use async/await** - The API is async-first
2. **Use context managers** - Ensures proper cleanup
3. **Implement error handlers** - Handle failures gracefully
4. **Rate limit responsibly** - Don't overwhelm servers
5. **Respect robots.txt** - Leave `obey_robots=True`
6. **Use callbacks for streaming** - Process pages as they arrive
7. **Cache appropriately** - Reuse cached content when possible
8. **Filter URLs** - Use include/exclude patterns
9. **Limit depth/pages** - Prevent runaway crawls
10. **Set user agent** - Identify your bot

## See Also

- [USAGE.md](USAGE.md) - CLI usage
- [example.py](example.py) - Complete examples
- [examples/](examples/) - Configuration examples
