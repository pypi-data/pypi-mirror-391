# Examples

This page collects example patterns and full working examples.

## Local examples

See `example.py` in the project root for multiple examples demonstrating:

- Callback-based crawling
- Event hooks
- Streaming API
- Multiple seed crawling
- Advanced configuration
- Custom storage
- Loading from config files

## Minimal example

```python
import asyncio
from mlcrawler import Crawler, Page

async def process(page: Page):
    print(page.title)

async def main():
    crawler = Crawler(max_pages=3)
    await crawler.crawl("https://httpbin.org/html", callback=process)

asyncio.run(main())
```

## Streaming example

```python
async with Crawler(max_pages=50) as crawler:
    async for page in crawler.stream("https://example.com"):
        print(page.title)
```

## Integration examples

- FastAPI background task example: see `API.md` under Integration Examples
- Jupyter notebook usage: `API.md`

> Tip: The `example.py` file in the repo is a good starting point—copy it into your project and adapt callbacks to your storage.
