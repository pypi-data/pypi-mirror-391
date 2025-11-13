"""mlcrawler - A configurable web crawler and scraper.

This package provides both a command-line interface and a library API
for crawling websites, extracting content, and converting to Markdown.

Library Usage:
    >>> from mlcrawler import Crawler
    >>>
    >>> async def process_page(page):
    ...     print(f"{page.title}: {page.url}")
    ...
    >>> crawler = Crawler(max_depth=2, max_pages=50)
    >>> await crawler.crawl("https://example.com", callback=process_page)

CLI Usage:
    $ mlcrawler --url https://example.com --follow --max-depth 2
    $ mlcrawler --sitemap https://example.com/sitemap.xml --output ./docs
"""

__version__ = "0.0.1"

# Public API exports
from .api import Crawler
from .page import Page

__all__ = [
    "Crawler",
    "Page",
    "__version__",
]
