Project name
- Default: mlcrawler (changeable; keep user-agent in sync).

Purpose
- Build a thin, configurable Python 3.11+ CLI crawler/scraper that:
  - Runs via uv, Docker, or cron
  - Supports two crawl modes: sitemap and seed-url
  - Extracts and filters HTML, converts to Markdown
  - Optionally extracts “main article” only via trafilatura
  - Caches raw HTML on disk; metadata persisted via sidecar JSON by default
  - Uses TOML configuration with multi-file merging (defaults + site-specific)
  - Obeys robots.txt by default

Development rules
- Always use uv (uv add, uv run, uvx). No pip or python -m.
- Keep modules small, composable, and focused.
- Tests assert observable behavior and outputs, not internals.
- Include ruff and mypy (practical strictness).
- License: Apache-2.0.

Defaults and behavior
- User-Agent: mlcrawler/0.1 (+contact-url)
- Obey robots.txt: true
- Concurrency: global=8, per_host=4
- Per-host delay: 500 ms
- same_domain_only: true
- max_depth (seed mode): 2
- URL matching: regex on absolute URL
- File naming: slugified path; index.md for trailing slash URLs
- Metadata backend default: sidecar JSON
- Two modes:
  - sitemap: load sitemap.xml or index, follow sub-sitemaps, respect lastmod
  - seed: start from seed URLs, dynamically discover links

How we leverage trafilatura (no duplication)
- Main article extraction: use trafilatura.extract for robust boilerplate removal when extract.main_article=true. Prefer output='txt' (plain text). On failure, fall back to full-page pipeline.
- Metadata hints: parse trafilatura’s extracted metadata (title, author, date) when available to enrich sidecar metadata, but remain resilient if missing.
- Sitemap helpers: use trafilatura.sitemaps functions (e.g., sitemap discovery via robots, parsing of sitemap index and urlset) to enumerate URLs and read lastmod. We still manage our own conditional requests, caching, and dedup.
- We do not use trafilatura for crawling/networking, concurrency, or caching; we keep our httpx-based polite fetcher and disk cache for control and observability.

High-level architecture
- CLI entrypoint: mlcrawler
- Pipeline stages:
  1) Discover
     - mode=sitemap: discover sitemap URL (robots) if not configured; parse sitemap index and sub-sitemaps; read lastmod; deduplicate against visited.
     - mode=seed: BFS frontier; extract in-page links; same-domain scope; include/exclude regex.
  2) Fetch
     - httpx.AsyncClient; obey robots.txt; global and per-host concurrency caps; per-host delay; conditional requests (ETag/Last-Modified).
     - Disk cache for raw HTML and headers/metadata.
  3) Parse and filter
     - HTML via bs4 + lxml parser; remove script, style, svg; apply extra selectors from config (e.g., nav, footer, .ads).
  4) Extract
     - If extract.main_article=true: call trafilatura.extract on the original HTML to get clean text; if success, use it; else use filtered full page.
  5) Transform
     - If we have full-page HTML: convert to Markdown via markdownify.
     - If we have trafilatura text: convert to Markdown as paragraphs (no markdownify needed).
     - Title: prefer <title>, then <h1>, then og:title, then trafilatura metadata.
  6) Output
     - Write Markdown file per URL under output/{domain}/{slug}/index.md or {slug}.md.
     - Write sidecar .meta.json with url, title, fetched_at, last_modified, etag, source, depth, status, content_hash, cache_path, extraction_mode.
  7) Resume
     - Persist visited/frontier and sitemap parsing state (in a lightweight sqlite database) to support resume.

Configuration (TOML, deep-merge; later files override earlier)
- mode = "sitemap" | "seed"
- user_agent = "mlcrawler/0.1 (+contact-url)"
- obey_robots = true
- same_domain_only = true
- max_depth = 2  (seed mode; 0 = unlimited)
- limits.max_pages = 0
- concurrency.global = 8
- concurrency.per_host = 4
- rate_limit.per_host_delay_ms = 500
- cache.dir = ".cache/mlcrawler"
- cache.respect_conditional = true
- output.dir = "output"
- output.metadata_backend = "json" | "duckdb"
- sitemap.url = "https://example.com/sitemap.xml"  (optional; discover via robots if omitted)
- sitemap.use_lastmod = true
- seeds = ["https://example.com"]  (seed mode)
- discovery.follow_links = true
- discovery.include_patterns = []  (regex strings)
- discovery.exclude_patterns = []
- filter.dom_remove = ["script", "style", "svg"]
- filter.extra_remove = []  (e.g., "nav", "footer", ".ads")
- extract.main_article = false

CLI
- uv run mlcrawler --config defaults.toml --config site.toml --sitemap https://example.com/sitemap.xml
- uv run mlcrawler --config defaults.toml --config site.toml --url https://example.com --follow
- uv run mlcrawler --url https://example.com --output ./output --main-article
- uv run mlcrawler --sitemap https://example.com/sitemap.xml --verbose
- uv run mlcrawler --config site.toml --max-depth 2 --max-pages 100

Robots and URL handling
- robots.txt: fetch and cache per origin; obey by default.
- Normalize URLs: resolve relatives, strip fragments, keep query by default. Deduplicate strictly.
- Scope: same_domain_only true by default; configurable.

Fetching and caching
- httpx.AsyncClient with connection pooling.
- Concurrency: global and per-host semaphores; per-host delay enforced.
- Cache on disk:
  - cache/{host}/{sha256(url)[:2]}/{sha256(url)}.html for body
  - sibling .headers.json with status, headers, fetched_at, size_bytes, content_hash
- Conditional GET:
  - Send If-None-Match/If-Modified-Since when ETag/Last-Modified present.
  - On 304, reuse cached body; update metadata timestamps.

Sitemap mode specifics
- Discover sitemap via robots if sitemap.url missing.
- Support sitemap index and urlset; recurse into sub-sitemaps.
- Use lastmod:
  - Skip sub-sitemap if lastmod unchanged since last parse (record parse time).
  - Skip URL fetch if validators indicate unchanged (ETag/Last-Modified) or lastmod older than stored fetched_at.

Seed mode specifics
- BFS traversal by default; track depth.
- Apply include/exclude regex before enqueueing.
- Extract links from HTML anchors and canonical link rels; normalize and deduplicate.

Filtering and Markdown
- Filtering with bs4:
  - Always remove script, style, svg.
  - Remove any extra selectors from config.
- Extraction path:
  - If extract.main_article=true: trafilatura.extract(html, include_comments=False, include_links=True). If it returns text, transform to Markdown as paragraphs; do not feed into markdownify.
  - Else: feed filtered HTML to markdownify.
- Metadata sidecar (.meta.json) includes: url, title, fetched_at, last_modified (server), etag, source (seed|sitemap|link), depth, status, content_hash, cache_path, extraction_mode ("article"|"fullpage"), and optional trafilatura metadata (e.g., date, author) if present.

Storage backends
- metadata_backend=json (default): write sidecar .meta.json files

Dependencies (install with uv)
- Required: httpx, beautifulsoup4, lxml, markdownify, typer, pydantic, python-slugify, trafilatura
- Optional: duckdb, pytest, anyio, ruff, mypy
- Example:
  - uv add httpx beautifulsoup4 lxml markdownify typer pydantic python-slugify trafilatura
  - uv add duckdb
  - uv add pytest anyio
  - uvx ruff check .
  - uv add mypy

Testing strategy
- Integration tests spin up a local HTTP server (http.server or Starlette) that serves:
  - robots.txt (allow/deny)
  - sitemap index and sub-sitemaps with varied lastmod
  - HTML pages with internal/external links and noise elements
  - ETag/Last-Modified to validate conditional requests
- Tests assert:
  - Discovery correctness in both modes (sitemap recursion + lastmod, seed BFS)
  - Robots obedience and same-domain scoping
  - Filtering (script/style/svg removed; extra selectors honored)
  - Markdown output file paths and contents
  - Sidecar metadata correctness
  - Cache hits and 304 handling
  - Resume from saved state
- Avoid testing private functions; assert on outputs (files, DB rows, logs).

Milestones
- M1 Sitemap mode minimal crawler:
  - Sitemap index/urlset parsing into a fetch list, fetch HTML, markdownify -> Markdown + .meta.json
- M2 Seed mode:
  - Dynamic fetch list building from parsing crawled pages (manage duplicates)
- M3 Caching and validators:
  - Disk cache, ETag/Last-Modified observation, 304 reuse, concurrency + per-host delay
- M4 Robots + resume:
  - robots.txt obedience, visited/frontier persistence (JSON/ DuckDB), resume functionality

Logging and observability
- Structured logs with level, url, status, source, depth, action (fetch/cache/skip/filter/extract/output).
- Summaries per run: pages fetched, cached hits, skipped via robots, skipped via lastmod, errors.

Small implementation notes
- Use asyncio semaphores for global/per-host concurrency; track last-request time per host for delay.
- URL normalization: urllib.parse; strip fragments; preserve query; normalize trailing slashes; slugify path for filenames.
- Content hashing: sha256 of response body; store in headers.json and metadata.
- For sitemap lastmod comparisons, be tolerant of timezone/format differences.
