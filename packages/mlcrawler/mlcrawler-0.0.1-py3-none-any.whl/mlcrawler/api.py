"""High-level API for using mlcrawler as a library.

This module provides a Pythonic, async-first API for crawling websites
with callback-based processing. It wraps the internal CrawlController
and provides a cleaner interface for library users.

Example:
    >>> from mlcrawler import Crawler
    >>>
    >>> async def process_page(page):
    ...     print(f"Got {page.title} from {page.url}")
    ...
    >>> crawler = Crawler(max_depth=2, max_pages=50)
    >>> await crawler.crawl("https://example.com", callback=process_page)
"""

import asyncio
import logging
from pathlib import Path
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    List,
    Optional,
    Union,
)
from collections import defaultdict

from .config import Config, create_config, validate_config
from .crawl import CrawlController, UrlInfo
from .extract import ExtractedContent
from .fetch import FetchResponse
from .page import Page


# Type aliases for clarity
PageCallback = Callable[[Page], Any]
ErrorCallback = Callable[[str, Exception], Any]
EventCallback = Callable[..., Any]


class Crawler:
    """Main crawler API for library usage.

    This class provides a high-level interface for crawling websites
    with callback-based processing. It handles configuration, manages
    resources, and provides event hooks for customization.

    Args:
        user_agent: User agent string for HTTP requests
        max_depth: Maximum crawl depth (0 = unlimited)
        max_pages: Maximum pages to crawl (0 = unlimited)
        main_article_only: Extract main article content only
        cache_dir: Directory for caching
        follow_links: Follow links discovered on pages
        same_domain_only: Only crawl URLs from same domain
        obey_robots: Respect robots.txt
        rate_limit_ms: Delay between requests to same host (milliseconds)
        concurrency: Global concurrent request limit
        per_host_concurrency: Per-host concurrent request limit
        include_patterns: Regex patterns for URLs to include
        exclude_patterns: Regex patterns for URLs to exclude
        remove_selectors: CSS selectors to remove from HTML
        save_to_disk: Whether to save markdown/metadata to disk
        output_dir: Directory for output files (if save_to_disk=True)
        config_files: Optional TOML config files to load

    Example:
        >>> crawler = Crawler(
        ...     user_agent="MyBot/1.0",
        ...     max_depth=3,
        ...     main_article_only=True,
        ... )
        >>> await crawler.crawl("https://example.com", callback=my_callback)
    """

    def __init__(
        self,
        *,
        user_agent: str = "mlcrawler/0.1 (+contact-url)",
        max_depth: int = 2,
        max_pages: int = 0,
        main_article_only: bool = False,
        cache_dir: Union[str, Path] = ".cache/mlcrawler",
        follow_links: bool = True,
        same_domain_only: bool = True,
        obey_robots: bool = True,
        rate_limit_ms: int = 500,
        concurrency: int = 8,
        per_host_concurrency: int = 4,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        remove_selectors: Optional[List[str]] = None,
        save_to_disk: bool = False,
        output_dir: Union[str, Path] = "output",
        config_files: Optional[List[Union[str, Path]]] = None,
    ):
        """Initialize the crawler with configuration."""
        self.logger = logging.getLogger(__name__)

        # Event handlers
        self._event_handlers: Dict[str, List[EventCallback]] = defaultdict(list)

        # Build configuration
        config_overrides = {
            "mode": "seed",  # Default to seed mode for library API
            "seeds": [],  # Will be set when crawl() is called
            "user_agent": user_agent,
            "max_depth": max_depth,
            "obey_robots": obey_robots,
            "same_domain_only": same_domain_only,
            "limits": {"max_pages": max_pages},
            "concurrency": {
                "global": concurrency,
                "per_host": per_host_concurrency,
            },
            "rate_limit": {"per_host_delay_ms": rate_limit_ms},
            "cache": {"dir": str(cache_dir)},
            "output": {"dir": str(output_dir)},
            "discovery": {
                "follow_links": follow_links,
                "include_patterns": include_patterns or [],
                "exclude_patterns": exclude_patterns or [],
            },
            "filter": {
                "dom_remove": ["script", "style", "svg"],
                "extra_remove": remove_selectors or [],
            },
            "extract": {"main_article": main_article_only},
        }

        # Load config files if provided
        config_paths = [Path(f) for f in config_files] if config_files else []

        # Create config
        dynaconf_config = create_config(config_paths, **config_overrides)
        # Note: Don't validate yet - seeds will be set when crawl() is called
        self._config = Config(dynaconf_config)

        # Internal state
        self._controller: Optional[CrawlController] = None
        self._save_to_disk = save_to_disk
        self._running = False

    @classmethod
    def from_config(
        cls,
        config_files: Union[str, Path, List[Union[str, Path]]],
        **overrides,
    ) -> "Crawler":
        """Create a Crawler from configuration file(s).

        Args:
            config_files: Single file path or list of TOML config files
            **overrides: Additional configuration overrides

        Returns:
            Configured Crawler instance

        Example:
            >>> crawler = Crawler.from_config("crawler.toml")
            >>> # Or merge multiple configs
            >>> crawler = Crawler.from_config(
            ...     ["defaults.toml", "site.toml"],
            ...     max_pages=100,
            ... )
        """
        if isinstance(config_files, (str, Path)):
            config_files = [config_files]

        return cls(config_files=config_files, **overrides)

    def on(self, event: str) -> Callable:
        """Decorator to register event handlers.

        Supported events:
            - "fetch": Called before fetching a URL (url: str)
            - "page": Called after processing a page (page: Page)
            - "error": Called on error (url: str, error: Exception)
            - "complete": Called when crawl completes (stats: dict)

        Args:
            event: Event name to listen for

        Returns:
            Decorator function

        Example:
            >>> @crawler.on("page")
            ... async def process(page):
            ...     print(f"Got {page.title}")
        """

        def decorator(func: EventCallback) -> EventCallback:
            self._event_handlers[event].append(func)
            return func

        return decorator

    async def _emit(self, event: str, *args, **kwargs):
        """Emit an event to all registered handlers.

        Args:
            event: Event name
            *args: Positional arguments for handlers
            **kwargs: Keyword arguments for handlers
        """
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                result = handler(*args, **kwargs)
                # Handle both sync and async handlers
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                self.logger.error(f"Error in {event} handler: {e}")

    async def crawl(
        self,
        url: str,
        *,
        callback: Optional[PageCallback] = None,
        follow_links: Optional[bool] = None,
    ) -> List[Page]:
        """Crawl a website starting from a seed URL.

        Args:
            url: Starting URL to crawl
            callback: Optional callback function called for each page
            follow_links: Override follow_links setting

        Returns:
            List of crawled Page objects

        Example:
            >>> async def process(page):
            ...     print(page.title)
            >>> pages = await crawler.crawl(
            ...     "https://example.com",
            ...     callback=process,
            ... )
        """
        return await self.crawl_many(
            [url], callback=callback, follow_links=follow_links
        )

    async def crawl_many(
        self,
        urls: List[str],
        *,
        callback: Optional[PageCallback] = None,
        follow_links: Optional[bool] = None,
    ) -> List[Page]:
        """Crawl multiple seed URLs.

        Args:
            urls: List of starting URLs
            callback: Optional callback function called for each page
            follow_links: Override follow_links setting

        Returns:
            List of all crawled Page objects

        Example:
            >>> pages = await crawler.crawl_many([
            ...     "https://example.com",
            ...     "https://another.com",
            ... ])
        """
        # Set mode and seeds
        self._config._config["mode"] = "seed"
        self._config._config["seeds"] = urls

        if follow_links is not None:
            self._config._config["discovery"]["follow_links"] = follow_links

        return await self._run_crawl(callback=callback)

    async def crawl_sitemap(
        self,
        sitemap_url: str,
        *,
        callback: Optional[PageCallback] = None,
    ) -> List[Page]:
        """Crawl pages discovered from a sitemap.

        Args:
            sitemap_url: URL of the sitemap.xml file
            callback: Optional callback function called for each page

        Returns:
            List of crawled Page objects

        Example:
            >>> pages = await crawler.crawl_sitemap(
            ...     "https://example.com/sitemap.xml",
            ...     callback=process_page,
            ... )
        """
        # Set mode and sitemap URL
        self._config._config["mode"] = "sitemap"
        self._config._config["sitemap"]["url"] = sitemap_url

        return await self._run_crawl(callback=callback)

    async def stream(
        self,
        url: str,
        *,
        follow_links: Optional[bool] = None,
    ) -> AsyncIterator[Page]:
        """Stream pages as they are crawled.

        This is an async generator that yields pages as they are processed,
        allowing for memory-efficient processing of large crawls.

        Args:
            url: Starting URL to crawl
            follow_links: Override follow_links setting

        Yields:
            Page objects as they are crawled

        Example:
            >>> async for page in crawler.stream("https://example.com"):
            ...     process(page)
            ...     if should_stop():
            ...         break
        """
        # Use a queue to communicate between crawler and generator
        queue: asyncio.Queue[Page] = asyncio.Queue()

        async def queue_callback(page: Page):
            await queue.put(page)

        # Start crawl in background
        crawl_task = asyncio.create_task(
            self.crawl(url, callback=queue_callback, follow_links=follow_links)
        )

        try:
            # Yield pages as they arrive
            while not crawl_task.done() or not queue.empty():
                try:
                    page = await asyncio.wait_for(queue.get(), timeout=0.1)
                    if page is not None:
                        yield page
                except asyncio.TimeoutError:
                    continue

            # Ensure the crawl task is done
            await crawl_task

        except asyncio.CancelledError:
            # If generator is cancelled, cancel the crawl
            crawl_task.cancel()
            try:
                await crawl_task
            except asyncio.CancelledError:
                pass
            raise

    async def _run_crawl(
        self, *, callback: Optional[PageCallback] = None
    ) -> List[Page]:
        """Internal method to run the crawl with current configuration.

        Args:
            callback: Optional callback for each page

        Returns:
            List of crawled pages
        """
        # Validate configuration before running
        validate_config(self._config._config)

        self._running = True
        pages: List[Page] = []

        try:
            # Create controller
            self._controller = CrawlController(self._config)

            # Monkey-patch the controller to intercept page processing
            pages_lock = asyncio.Lock()

            async def intercept_process(url_info: UrlInfo):
                """Intercept page processing to create Page objects and call callbacks."""
                # Ensure controller exists
                if not self._controller:
                    return False

                # Call original fetch logic
                if url_info.url in self._controller.processed_urls:
                    return False

                self._controller.processed_urls.add(url_info.url)

                try:
                    # Emit fetch event
                    await self._emit("fetch", url_info.url)

                    # Fetch the HTML content
                    response: Optional[
                        FetchResponse
                    ] = await self._controller.fetcher.fetch(url_info.url)
                    if not response or not response.content:
                        return False

                    # Extract and process content
                    extracted: Optional[
                        ExtractedContent
                    ] = await self._controller.extractor.extract(url_info.url, response)
                    if not extracted:
                        return False

                    # Create Page object
                    page = self._create_page(url_info, response, extracted)

                    # Store in results
                    async with pages_lock:
                        pages.append(page)

                    # Emit page event
                    await self._emit("page", page)

                    # Call user callback
                    if callback:
                        result = callback(page)
                        if asyncio.iscoroutine(result):
                            await result

                    # Write to disk if configured
                    if self._save_to_disk:
                        metadata_extras = {
                            "depth": url_info.depth,
                            "source": url_info.source,
                        }
                        await self._controller.output_writer.write(
                            url_info.url, extracted, response, metadata_extras
                        )

                    return True

                except Exception as e:
                    self.logger.error(f"Failed to process URL {url_info.url}: {e}")
                    await self._emit("error", url_info.url, e)
                    raise

            # Replace the process method
            self._controller._process_url = intercept_process

            # Run the crawl
            await self._controller.crawl()

            # Emit complete event with stats
            stats = {
                "pages": len(pages),
                "mode": self._config.mode,
            }
            await self._emit("complete", stats)

            return pages

        finally:
            self._running = False
            if self._controller:
                # Clean up resources
                await self._controller.fetcher.close()
                await self._controller.sitemap_discoverer.close()

    def _create_page(
        self,
        url_info: UrlInfo,
        response: FetchResponse,
        extracted: ExtractedContent,
    ) -> Page:
        """Create a Page object from crawl results.

        Args:
            url_info: URL information
            response: HTTP response
            extracted: Extracted content

        Returns:
            Page object with all data
        """
        # Extract plain text from markdown (simple approach)
        import re

        text = re.sub(r"[#*_\[\]`]", "", extracted.content)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Build page object
        page = Page(
            url=url_info.url,
            title=extracted.title,
            markdown=extracted.content,
            html=response.content,
            text=text,
            metadata=extracted.metadata,
            fetched_at=response.fetched_at,
            status_code=response.status,
            content_hash=response.content_hash,
            depth=url_info.depth,
            source=url_info.source,
            extraction_mode=extracted.extraction_mode,
            from_cache=response.from_cache,
            cache_path=Path(response.cache_path) if response.cache_path else None,
            headers=response.headers,
        )

        # Add trafilatura metadata if present
        if extracted.metadata:
            page.author = extracted.metadata.get("author")
            page.date = extracted.metadata.get("date")
            page.description = extracted.metadata.get("description")
            page.sitename = extracted.metadata.get("sitename")

        return page

    async def __aenter__(self) -> "Crawler":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        if self._controller:
            await self._controller.fetcher.close()
            await self._controller.sitemap_discoverer.close()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Crawler(max_depth={self._config.max_depth}, "
            f"max_pages={self._config.limits.max_pages}, "
            f"running={self._running})"
        )
