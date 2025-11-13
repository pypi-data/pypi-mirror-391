# API Reference

This page documents the public library API for `mlcrawler`.

> The canonical and more extensive API documentation is available in `API.md` at the project root; this page is a curated version suitable for the docs site.

## Public imports

```python
from mlcrawler import Crawler, Page
```

## Crawler

`Crawler` is the main entry point. It is an async-first, callback-driven class used to configure and run crawls.

Constructor highlights:

- `user_agent` (str)
- `max_depth` (int)
- `max_pages` (int)
- `main_article_only` (bool)
- `cache_dir` (str)
- `follow_links` (bool)
- `same_domain_only` (bool)
- `obey_robots` (bool)
- `rate_limit_ms` (int)
- `concurrency` (int)
- `per_host_concurrency` (int)
- `include_patterns` / `exclude_patterns` (List[str])
- `remove_selectors` (List[str])
- `save_to_disk` (bool)
- `output_dir` (str)

### Methods

- `crawl(url, callback=None, follow_links=None) -> List[Page]` — Crawl a seed URL and return collected Page objects.
- `crawl_many(urls, callback=None, follow_links=None) -> List[Page]` — Crawl multiple seeds.
- `crawl_sitemap(sitemap_url, callback=None) -> List[Page]` — Discover URLs in a sitemap and crawl them.
- `stream(url, follow_links=None) -> AsyncIterator[Page]` — Async generator yielding `Page` objects as they are processed.
- `on(event)` — Decorator to register event handlers for `fetch`, `page`, `error`, and `complete`.
- `from_config(config_files, **overrides)` — Classmethod to construct a `Crawler` from TOML config files.

### Events

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

## Page

A `Page` dataclass is passed to callbacks. Key attributes include:

- `url`, `title`, `markdown`, `html`, `text`
- `metadata`, `fetched_at`, `status_code`, `content_hash`
- `depth`, `source`, `extraction_mode`
- `author`, `date`, `description`, `sitename`
- `from_cache`, `cache_path`, `headers`

Properties:

- `.domain`, `.is_seed`, `.is_from_sitemap`, `.is_discovered_link`, `.is_main_article`

## Examples

See the Examples page for practical code snippets and patterns.

---

_For a more verbose copy of the API docs (including full examples and best practices), see `API.md` in the repository root._
