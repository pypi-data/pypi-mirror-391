# Installation

This page documents installation options for mlcrawler.

## From PyPI

```bash
pip install mlcrawler
```

## Development (from source)

```bash
git clone <repository-url>
cd mlcrawler
pip install -e .
# or with uv
uv pip install -e .
```

## Dependencies

mlcrawler depends on:

- httpx
- beautifulsoup4
- lxml
- markdownify
- trafilatura
- python-slugify
- typer
- dynaconf

If you use MkDocs on ReadTheDocs, ensure `mkdocs` and `mkdocs-material` appear in the docs build requirements.

## Verify installation

A small script to verify the library works:

```python
import asyncio
from mlcrawler import Crawler

async def main():
    crawler = Crawler(max_pages=1)
    pages = await crawler.crawl("https://httpbin.org/html")
    print(f"Crawled {len(pages)} page(s)")

asyncio.run(main())
```

## Notes for ReadTheDocs

- On ReadTheDocs select the "MkDocs" documentation type.
- Add `mkdocs` and `mkdocs-material` to documentation install requirements so the build environment provides them. You can add a `docs/requirements.txt` for ReadTheDocs.

Example `docs/requirements.txt`:

```
mkdocs
mkdocs-material
```
