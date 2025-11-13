# mlcrawler Quick Reference

## Installation

```bash
pip install mlcrawler
# or
uv add mlcrawler
```

## Basic Usage

```python
import asyncio
from mlcrawler import Crawler, Page

async def process(page: Page):
    print(f"{page.title}: {page.url}")

crawler = Crawler(max_pages=50)
await crawler.crawl("https://example.com", callback=process)
```

## Common Patterns

### 1. Simple Crawl

```python
crawler = Crawler(max_depth=2, max_pages=50)
pages = await crawler.crawl("https://example.com")
```

### 2. With Callback

```python
async def save(page: Page):
    db.insert({"url": page.url, "content": page.markdown})

await crawler.crawl("https://example.com", callback=save)
```

### 3. Event Hooks

```python
@crawler.on("page")
async def on_page(page: Page):
    print(f"Got {page.title}")

await crawler.crawl("https://example.com")
```

### 4. Streaming

```python
async for page in crawler.stream("https://example.com"):
    process(page)
```

### 5. Multiple URLs

```python
pages = await crawler.crawl_many([
    "https://site1.com",
    "https://site2.com",
])
```

### 6. Sitemap

```python
pages = await crawler.crawl_sitemap(
    "https://example.com/sitemap.xml"
)
```

### 7. From Config

```python
crawler = Crawler.from_config("config.toml")
```

## Configuration

```python
Crawler(
    max_depth=2,                    # Crawl depth
    max_pages=100,                  # Max pages
    follow_links=True,              # Follow links
    same_domain_only=True,          # Same domain
    main_article_only=False,        # Main content only
    rate_limit_ms=500,              # Delay (ms)
    concurrency=8,                  # Concurrent requests
    cache_dir=".cache",             # Cache directory
    save_to_disk=False,             # Save files
    output_dir="output",            # Output directory
)
```

## Page Object

```python
page.url                # URL
page.title              # Title
page.markdown           # Markdown content
page.html               # Original HTML
page.text               # Plain text
page.depth              # Crawl depth
page.source             # "seed"/"sitemap"/"link"
page.from_cache         # Cache hit?
page.status_code        # HTTP status
page.fetched_at         # Timestamp
```

## Events

```python
@crawler.on("fetch")
async def on_fetch(url: str):
    ...

@crawler.on("page")
async def on_page(page: Page):
    ...

@crawler.on("error")
async def on_error(url: str, error: Exception):
    ...

@crawler.on("complete")
async def on_complete(stats: dict):
    ...
```

## Context Manager

```python
async with Crawler() as crawler:
    pages = await crawler.crawl("https://example.com")
    # Auto cleanup
```

## URL Filtering

```python
Crawler(
    include_patterns=[r"https://example\.com/blog/.*"],
    exclude_patterns=[r".*/archive/.*"],
)
```

## Content Filtering

```python
Crawler(
    remove_selectors=["nav", "footer", ".ads"],
    main_article_only=True,
)
```

## CLI Usage

```bash
# Simple crawl
mlcrawler --url https://example.com

# With options
mlcrawler --url https://example.com --follow --max-depth 2

# Sitemap
mlcrawler --sitemap https://example.com/sitemap.xml

# From config
mlcrawler --config crawler.toml
```

## Full Example

```python
import asyncio
from mlcrawler import Crawler, Page

async def main():
    # Configure
    crawler = Crawler(
        max_depth=2,
        max_pages=50,
        follow_links=True,
        main_article_only=True,
    )
    
    # Add hooks
    @crawler.on("page")
    async def on_page(page: Page):
        print(f"✓ {page.title}")
    
    # Crawl
    pages = await crawler.crawl("https://example.com")
    
    # Process
    for page in pages:
        print(f"{page.url}: {len(page.markdown)} chars")

asyncio.run(main())
```

## See Also

- [API.md](API.md) - Full API documentation
- [INSTALL.md](INSTALL.md) - Installation guide
- [example.py](example.py) - Working examples
- [README.md](README.md) - Overview
