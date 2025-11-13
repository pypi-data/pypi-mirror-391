"""Main crawl controller that orchestrates the crawling process."""

import asyncio
import logging
from typing import List, Set, NamedTuple
from urllib.parse import urlparse

from .config import Config
from .sitemap import SitemapDiscoverer
from .fetch import Fetcher
from .extract import ContentExtractor
from .output import OutputWriter
from .links import LinkDiscoverer


class UrlInfo(NamedTuple):
    """Information about a URL to crawl."""

    url: str
    depth: int
    source: str  # "seed", "sitemap", or "link"


class CrawlController:
    """Main controller for the crawling process."""

    def __init__(self, config: Config):
        """Initialize the crawl controller.

        Args:
            config: Crawl configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.sitemap_discoverer = SitemapDiscoverer(config)
        self.fetcher = Fetcher(config)
        self.extractor = ContentExtractor(config)
        self.output_writer = OutputWriter(config)
        self.link_discoverer = LinkDiscoverer(config)

        # Track processed URLs to avoid duplicates
        self.processed_urls: Set[str] = set()
        self.queued_urls: Set[str] = set()

    async def crawl(self):
        """Run the main crawl process."""
        self.logger.info(f"Starting crawl in {self.config.mode} mode")

        try:
            # Discover URLs to crawl
            if self.config.mode == "sitemap":
                urls_to_crawl = await self._discover_sitemap_urls()
                # Convert to UrlInfo objects
                url_infos = [UrlInfo(url, 0, "sitemap") for url in urls_to_crawl]
            elif self.config.mode == "seed":
                url_infos = await self._discover_seed_urls()
            else:
                raise ValueError(f"Unknown crawl mode: {self.config.mode}")

            if not url_infos:
                self.logger.warning("No URLs found to crawl")
                return

            self.logger.info(f"Found {len(url_infos)} URLs to crawl")

            # Apply max_pages limit if configured
            if (
                self.config.limits.max_pages > 0
                and len(url_infos) > self.config.limits.max_pages
            ):
                original_count = len(url_infos)
                url_infos = url_infos[: self.config.limits.max_pages]
                self.logger.info(
                    f"Limited to {len(url_infos)} (out of {original_count}) URLs"
                )

            # Create output directory
            self.config.output.dir.mkdir(parents=True, exist_ok=True)

            # Process URLs with concurrency control
            semaphore = asyncio.Semaphore(self.config.concurrency.global_)
            tasks = [
                self._process_url_with_semaphore(semaphore, url_info)
                for url_info in url_infos
            ]

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log results summary
            successful = sum(1 for r in results if r is True)
            failed = sum(1 for r in results if isinstance(r, Exception))
            skipped = len(results) - successful - failed

            self.logger.info(
                f"Crawl completed: {successful} successful, {failed} failed, {skipped} skipped"
            )

        except Exception as e:
            self.logger.error(f"Crawl failed: {e}")
            raise
        finally:
            # Clean up resources
            await self.fetcher.close()
            await self.sitemap_discoverer.close()

    async def _discover_urls(self) -> List[UrlInfo]:
        """Discover URLs to crawl based on the configured mode.

        Returns:
            List of UrlInfo objects to crawl
        """
        if self.config.mode == "sitemap":
            urls = await self._discover_sitemap_urls()
            return [UrlInfo(url, 0, "sitemap") for url in urls]
        elif self.config.mode == "seed":
            return await self._discover_seed_urls()
        else:
            raise ValueError(f"Unknown crawl mode: {self.config.mode}")

    async def _discover_seed_urls(self) -> List[UrlInfo]:
        """Discover URLs in seed mode using BFS traversal.

        Returns:
            List of UrlInfo objects discovered through seed crawling
        """
        if not self.config.seeds:
            raise ValueError("No seed URLs provided for seed mode")

        # Initialize with seed URLs
        queue = [UrlInfo(url, 0, "seed") for url in self.config.seeds]
        discovered = []

        # If not following links, just return the seeds
        if not self.config.discovery.follow_links:
            self.logger.info(f"Not following links - returning {len(queue)} seed URLs")
            return queue

        self.logger.info(f"Starting BFS discovery from {len(queue)} seed URLs")

        # BFS traversal
        while queue:
            current = queue.pop(0)

            # Check if we've already seen this URL
            if current.url in self.processed_urls or current.url in self.queued_urls:
                continue

            # Check depth limit (only skip if we're beyond the limit)
            if self.config.max_depth > 0 and current.depth > self.config.max_depth:
                self.logger.debug(
                    f"Skipping {current.url} - beyond max depth {self.config.max_depth}"
                )
                continue

            # Add to our lists
            discovered.append(current)
            self.queued_urls.add(current.url)

            # If we should follow links and are within depth limit, fetch and extract links
            if self.config.max_depth == 0 or current.depth < self.config.max_depth:
                try:
                    # Fetch the page to extract links
                    response = await self.fetcher.fetch(current.url)
                    if response and response.content:
                        # Extract links from the page
                        discovered_links = self.link_discoverer.extract_links(
                            current.url, response.content
                        )

                        # Filter out already processed/queued URLs
                        new_links = self.link_discoverer.filter_discovered_urls(
                            discovered_links, self.processed_urls, self.queued_urls
                        )

                        # Add new links to queue with incremented depth
                        for link in new_links:
                            new_depth = current.depth + 1
                            queue.append(UrlInfo(link, new_depth, "link"))

                        self.logger.debug(
                            f"Found {len(new_links)} new links from {current.url} "
                            f"(depth {current.depth})"
                        )

                except Exception as e:
                    self.logger.warning(
                        f"Failed to fetch {current.url} for link discovery: {e}"
                    )

            # Apply max_pages limit during discovery
            if (
                self.config.limits.max_pages > 0
                and len(discovered) >= self.config.limits.max_pages
            ):
                self.logger.info(
                    f"Reached max_pages limit ({self.config.limits.max_pages}) during discovery"
                )
                break

        self.logger.info(f"BFS discovery completed: {len(discovered)} URLs to crawl")
        return discovered

    async def _discover_sitemap_urls(self) -> List[str]:
        """Discover URLs from sitemap.

        Returns:
            List of URLs from sitemap
        """
        # Determine sitemap URL
        if self.config.sitemap.url:
            sitemap_url = self.config.sitemap.url
        elif self.config.seeds:
            # Use first seed URL to discover sitemap
            base_url = self.config.seeds[0]
            parsed = urlparse(base_url)
            sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        else:
            raise ValueError(
                "No sitemap URL or seed URL provided for sitemap discovery"
            )

        self.logger.info(f"Discovering URLs from sitemap: {sitemap_url}")

        try:
            urls = await self.sitemap_discoverer.discover_urls(sitemap_url)
            self.logger.info(f"Discovered {len(urls)} URLs from sitemap")
            return urls
        except Exception as e:
            self.logger.error(
                f"Failed to discover URLs from sitemap {sitemap_url}: {e}"
            )
            # Fall back to seed URLs if sitemap discovery fails
            if self.config.seeds:
                self.logger.info("Falling back to seed URLs")
                return self.config.seeds
            raise

    async def _process_url_with_semaphore(
        self, semaphore: asyncio.Semaphore, url_info: UrlInfo
    ):
        """Process a single URL with concurrency control.

        Args:
            semaphore: Concurrency control semaphore
            url_info: UrlInfo object to process

        Returns:
            True if successful, False if skipped, raises exception if failed
        """
        async with semaphore:
            return await self._process_url(url_info)

    async def _process_url(self, url_info: UrlInfo):
        """Process a single URL through the full pipeline.

        Args:
            url_info: UrlInfo object to process

        Returns:
            True if successful, False if skipped
        """
        if url_info.url in self.processed_urls:
            self.logger.debug(f"Skipping already processed URL: {url_info.url}")
            return False

        self.processed_urls.add(url_info.url)

        try:
            self.logger.info(
                f"Processing URL: {url_info.url} (depth: {url_info.depth}, source: {url_info.source})"
            )

            # Fetch the HTML content
            response = await self.fetcher.fetch(url_info.url)
            if not response or not response.content:
                self.logger.warning(f"No content received for URL: {url_info.url}")
                return False

            # Extract and process content
            extracted = await self.extractor.extract(url_info.url, response)
            if not extracted:
                self.logger.warning(
                    f"Content extraction failed for URL: {url_info.url}"
                )
                return False

            # Write output with additional metadata
            metadata_extras = {
                "depth": url_info.depth,
                "source": url_info.source,
            }
            await self.output_writer.write(
                url_info.url, extracted, response, metadata_extras
            )

            self.logger.info(f"Successfully processed URL: {url_info.url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to process URL {url_info.url}: {e}")
            raise
