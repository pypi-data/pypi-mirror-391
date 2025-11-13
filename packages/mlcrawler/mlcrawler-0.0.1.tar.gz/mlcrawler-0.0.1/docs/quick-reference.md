# Quick Reference

This is a condensed cheat-sheet for common tasks.

## Basic usage (programmatic)

```python
from mlcrawler import Crawler, Page

async def process(page: Page):
    print(page.title)

crawler = Crawler(max_pages=50)
await crawler.crawl("https://example.com", callback=process)
```

## Core methods

- `crawl(url, callback=None)` — Crawl a seed URL
- `crawl_many(urls, callback=None)` — Crawl multiple seeds
- `crawl_sitemap(sitemap_url, callback=None)` — Crawl via sitemap
- `stream(url)` — Async generator of `Page` objects
- `on(event)` — Register an event handler

## Useful options

- `max_depth` — 0 = unlimited
- `max_pages` — 0 = unlimited
- `main_article_only` — extract main article via trafilatura
- `cache_dir` — disk cache location
- `save_to_disk` — write markdown + metadata files

## Events

- `fetch(url)` — before fetching
- `page(page)` — after page processed
- `error(url, exc)` — on error
- `complete(stats)` — when run finishes

For full details see the API Reference.
