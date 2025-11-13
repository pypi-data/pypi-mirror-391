# Getting Started

This page helps you get up and running with mlcrawler quickly.

## 1) Install

Install via pip (once published) or using `uv` for development:

```bash
pip install mlcrawler
# or (development)
uv pip install -e .
```

## 2) Simple programmatic example

Create a file `main.py` with the following:

```python
import asyncio
from mlcrawler import Crawler, Page

async def process(page: Page):
    print(f"{page.title}: {page.url}")

async def main():
    crawler = Crawler(max_depth=2, max_pages=10)
    await crawler.crawl("https://httpbin.org/html", callback=process)

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python main.py
```

## 3) CLI quick start

If you prefer the CLI, run:

```bash
uv run mlcrawler --url https://example.com --follow --max-depth 2
```

or use a sitemap:

```bash
uv run mlcrawler --sitemap https://example.com/sitemap.xml
```

## 4) Where to go next

- See the Installation page for more installation options and verification steps.
- See the API Reference for programmatic usage.
- See Examples for patterns and common setups.
