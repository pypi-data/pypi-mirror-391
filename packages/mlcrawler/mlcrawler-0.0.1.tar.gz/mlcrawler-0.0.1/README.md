# mlcrawler

A thin, configurable Python 3.11+ crawler/scraper with both **CLI** and **library API** support, featuring sitemap and seed-url modes.

## Features

- **Library API**: Use as a Python library with callback-based processing
- **Command Line**: Full-featured CLI for standalone crawling
- **Sitemap mode**: Automatically discover and parse XML sitemaps
- **Seed mode**: Crawl from starting URLs with link following
- **Content extraction**: Extract main articles using trafilatura or full page content
- **Markdown output**: Convert HTML to clean Markdown files
- **Metadata tracking**: Store fetch metadata in JSON sidecar files
- **Configurable**: TOML configuration with multi-file merging
- **Polite crawling**: Respects rate limits, robots.txt, and concurrency controls
- **Extensible**: Modular architecture with event hooks

## Installation

### As a Library

```bash
# Install from PyPI (once published)
pip install mlcrawler

# Or with uv
uv add mlcrawler

# Or install locally in development mode
uv pip install -e .
```

### For CLI Usage

This project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
# Clone the repository
git clone <repository-url>
cd mlcrawler

# Install dependencies
uv sync
```

## Quick Start

### Library API

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

**[Full Library API Documentation →](API.md)**

### Command Line Interface

```bash
# Crawl using a sitemap
uv run mlcrawler --sitemap https://example.com/sitemap.xml

# Crawl from seed URLs with link following
uv run mlcrawler --url https://example.com --follow --max-depth 2

# Use configuration file
uv run mlcrawler --config mlcrawler.toml
```

## Configuration

mlcrawler uses **Dynaconf** for unified configuration management with support for:

- **Configuration files** (TOML, JSON, YAML)
- **Environment variables** (prefix: `MLCRAWLER_`)
- **CLI overrides**

### Configuration Precedence (highest to lowest):

1. **CLI arguments** (`--url`, `--sitemap`, `--output`, etc.)
2. **Environment variables** (`MLCRAWLER_MODE`, `MLCRAWLER_USER_AGENT`, etc.)
3. **Configuration files** (later files override earlier ones)
4. **Built-in defaults**

### Using Multiple Configuration Sources

```bash
# Use config files with CLI overrides
uv run mlcrawler crawl --config defaults.toml --config site-specific.toml --output ./my-output

# Environment variables override config files
export MLCRAWLER_USER_AGENT="MyBot/1.0"
export MLCRAWLER_RATE_LIMIT__PER_HOST_DELAY_MS=1000
uv run mlcrawler crawl --config mysite.toml

# CLI args override everything
uv run mlcrawler crawl --sitemap https://example.com/sitemap.xml
```

### Example Configuration

```toml
# Crawl mode: 'sitemap' or 'seed'
mode = "sitemap"

# User agent string
user_agent = "mlcrawler/0.1 (+https://yoursite.com/contact)"

# Seed URLs for sitemap discovery
seeds = ["https://example.com"]

[limits]
max_pages = 100  # 0 = unlimited

[concurrency]
global = 8
per_host = 4

[rate_limit]
per_host_delay_ms = 500

[output]
dir = "output"
metadata_backend = "json"

[sitemap]
# url = "https://example.com/sitemap.xml"  # Optional
use_lastmod = true

[extract]
main_article = false  # Use trafilatura for main content extraction
```

See `examples/defaults.toml` and `examples/site.example.toml` for complete configuration examples.

### Environment Variables

All configuration options can be set via environment variables using the `MLCRAWLER_` prefix:

```bash
# Basic settings
export MLCRAWLER_MODE=sitemap
export MLCRAWLER_USER_AGENT="MyBot/1.0 (+https://mysite.com)"
export MLCRAWLER_SAME_DOMAIN_ONLY=true

# Nested settings use double underscores
export MLCRAWLER_OUTPUT__DIR=./my-output
export MLCRAWLER_OUTPUT__METADATA_BACKEND=json
export MLCRAWLER_CONCURRENCY__GLOBAL=4
export MLCRAWLER_CONCURRENCY__PER_HOST=2
export MLCRAWLER_RATE_LIMIT__PER_HOST_DELAY_MS=1000

# Arrays can be comma-separated
export MLCRAWLER_SEEDS="https://example.com,https://example.org"
export MLCRAWLER_FILTER__EXTRA_REMOVE="nav,.ads,.sidebar"

# Then run without config files
uv run mlcrawler crawl --sitemap https://example.com/sitemap.xml
```

## Usage

### Command Line Interface

```bash
# Show help
uv run mlcrawler --help

# Crawl with sitemap URL
uv run mlcrawler crawl --sitemap https://example.com/sitemap.xml

# Crawl with seed URLs (seed mode)
uv run mlcrawler crawl --url https://example.com --url https://example.com/page2

# Crawl with configuration file
uv run mlcrawler crawl --config mysite.toml

# Crawl with CLI overrides
uv run mlcrawler crawl --config defaults.toml --sitemap https://example.com/sitemap.xml --output ./my-output

# Verbose logging
uv run mlcrawler crawl --sitemap https://example.com/sitemap.xml --verbose

# Multiple configuration files (later ones override earlier)
uv run mlcrawler crawl --config defaults.toml --config site.toml
```

### Configuration Options

- **`--config`** (`-c`): Configuration file(s) to load (TOML). Can be specified multiple times.
- **`--url`** (`-u`): Seed URL(s) for crawling (implies seed mode). Can be specified multiple times.
- **`--sitemap`** (`-s`): Sitemap XML URL (implies sitemap mode).
- **`--output`** (`-o`): Override output directory
- **`--verbose`** (`-v`): Enable verbose logging

**Note**: You cannot specify both `--url` and `--sitemap` in the same command.

## Output Structure

mlcrawler creates the following output structure:

```
output/
└── example.com/
    ├── index.md              # Converted content
    ├── index.meta.json       # Metadata
    ├── about.md
    ├── about.meta.json
    └── blog/
        ├── post-1.md
        └── post-1.meta.json
```

### Metadata Format

Each `.meta.json` file contains:

```json
{
  "url": "https://example.com/page",
  "title": "Page Title",
  "fetched_at": "2025-01-15T10:30:00",
  "status": 200,
  "content_hash": "sha256-hash",
  "extraction_mode": "article",
  "trafilatura_metadata": {
    "author": "Author Name",
    "date": "2025-01-01"
  }
}
```

## Milestone 1 Features

This is **Milestone 1** implementation with the following features:

- ✅ Sitemap discovery and parsing (index and urlset)
- ✅ HTTP fetching with basic politeness (rate limiting, concurrency)
- ✅ HTML content extraction (full page + trafilatura main article)
- ✅ Markdown conversion using markdownify
- ✅ File output with metadata sidecars
- ✅ TOML configuration with deep merging
- ✅ CLI interface with Typer

### Coming in Future Milestones

- **M2**: Seed mode with dynamic link discovery
- **M3**: Disk caching with ETag/Last-Modified support
- **M4**: robots.txt obedience and crawl state persistence

## Development

This project follows these principles:

- Always use `uv` (no pip or python -m)
- Keep modules small, composable, and focused
- Tests assert observable behavior, not internals
- Apache-2.0 license

### Running Tests

```bash
# Install dev dependencies
uv add --dev pytest

# Run tests (when implemented)
uv run pytest
```

### Code Quality

```bash
# Install dev tools
uv add --dev ruff mypy

# Run linting
uvx ruff check .

# Run type checking
uvx mypy src/
```

## License

Apache-2.0

---

For more examples and advanced usage, see the `examples/` directory.
