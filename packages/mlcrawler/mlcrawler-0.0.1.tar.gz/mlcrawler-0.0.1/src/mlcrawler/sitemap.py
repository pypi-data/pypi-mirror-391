"""Sitemap discovery and parsing using trafilatura helpers and disk cache."""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List
from urllib.parse import urljoin, urlparse

from trafilatura.sitemaps import sitemap_search

from .config import Config
from .fetch import Fetcher


class SitemapDiscoverer:
    """Discovers and parses sitemaps to extract URLs."""

    def __init__(self, config: Config):
        """Initialize the sitemap discoverer.

        Args:
            config: Crawler configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Reuse Fetcher for caching/conditionals
        self.fetcher = Fetcher(config)

    async def discover_urls(self, sitemap_url: str) -> List[str]:
        """Discover URLs from sitemap.

        Args:
            sitemap_url: URL of the sitemap to parse

        Returns:
            List of discovered URLs
        """
        self.logger.info(f"Discovering URLs from sitemap: {sitemap_url}")

        # First try to fetch the sitemap directly
        try:
            urls = await self._parse_sitemap_url(sitemap_url)
            if urls:
                return urls
        except Exception as e:
            self.logger.warning(f"Failed to parse sitemap directly {sitemap_url}: {e}")

        # Fall back to using trafilatura's sitemap discovery
        try:
            parsed_url = urlparse(sitemap_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            self.logger.info(f"Trying sitemap discovery for base URL: {base_url}")

            # Use trafilatura to discover sitemaps
            discovered_sitemaps = sitemap_search(base_url)

            if not discovered_sitemaps:
                self.logger.warning(f"No sitemaps discovered for {base_url}")
                return []

            # Parse all discovered sitemaps
            all_urls = set()
            for sitemap in discovered_sitemaps:
                try:
                    sitemap_urls = await self._parse_sitemap_url(sitemap)
                    all_urls.update(sitemap_urls)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse discovered sitemap {sitemap}: {e}"
                    )

            return list(all_urls)

        except Exception as e:
            self.logger.error(f"Sitemap discovery failed: {e}")
            return []

    async def _parse_sitemap_url(self, sitemap_url: str) -> List[str]:
        """Parse a single sitemap URL.

        Args:
            sitemap_url: URL of sitemap to parse

        Returns:
            List of URLs from the sitemap
        """
        try:
            # Fetch sitemap content (prefer conditional cache)
            fetch = await self.fetcher.fetch(sitemap_url)
            if not fetch:
                return []
            content = fetch.content

            # Parse XML
            root = ET.fromstring(content)

            # Handle different sitemap types
            if root.tag.endswith("sitemapindex"):
                # This is a sitemap index - parse sub-sitemaps
                return await self._parse_sitemap_index(root, sitemap_url)
            elif root.tag.endswith("urlset"):
                # This is a regular sitemap - extract URLs
                return self._parse_sitemap_urlset(root)
            else:
                self.logger.warning(
                    f"Unknown sitemap format in {sitemap_url}, root tag: {root.tag}"
                )
                return []

        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML in sitemap {sitemap_url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error parsing sitemap {sitemap_url}: {e}")
            return []

    async def _parse_sitemap_index(self, root: ET.Element, base_url: str) -> List[str]:
        """Parse a sitemap index and fetch all sub-sitemaps.

        Args:
            root: Root element of sitemap index XML
            base_url: Base URL for resolving relative URLs

        Returns:
            List of URLs from all sub-sitemaps
        """
        all_urls = set()

        # Find sitemap entries
        for sitemap in root.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"
        ):
            loc_elem = sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc_elem is not None and loc_elem.text:
                sub_sitemap_url = loc_elem.text.strip()

                # Resolve relative URLs
                sub_sitemap_url = urljoin(base_url, sub_sitemap_url)

                # Check lastmod if configured
                if self.config.sitemap.use_lastmod:
                    lastmod_elem = sitemap.find(
                        "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
                    )
                    if lastmod_elem is not None and lastmod_elem.text:
                        try:
                            lastmod = datetime.fromisoformat(
                                lastmod_elem.text.replace("Z", "+00:00")
                            )
                            # For M1, we'll process all sitemaps
                            # In future milestones, we can add lastmod-based skipping
                            self.logger.debug(
                                f"Sitemap {sub_sitemap_url} lastmod: {lastmod}"
                            )
                        except ValueError as e:
                            self.logger.warning(
                                f"Invalid lastmod format in sitemap index: {e}"
                            )

                # Parse the sub-sitemap
                self.logger.debug(f"Parsing sub-sitemap: {sub_sitemap_url}")
                try:
                    sub_urls = await self._parse_sitemap_url(sub_sitemap_url)
                    all_urls.update(sub_urls)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse sub-sitemap {sub_sitemap_url}: {e}"
                    )

        return list(all_urls)

    def _parse_sitemap_urlset(self, root: ET.Element) -> List[str]:
        """Parse a regular sitemap urlset.

        Args:
            root: Root element of sitemap XML

        Returns:
            List of URLs from the sitemap
        """
        urls = []

        # Find URL entries
        for url_elem in root.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"
        ):
            loc_elem = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc_elem is not None and loc_elem.text:
                url = loc_elem.text.strip()

                # Apply domain filtering if configured
                if self.config.same_domain_only and self.config.seeds:
                    seed_domain = urlparse(self.config.seeds[0]).netloc
                    url_domain = urlparse(url).netloc

                    if seed_domain != url_domain:
                        self.logger.debug(f"Skipping URL from different domain: {url}")
                        continue

                # Check lastmod if configured
                if self.config.sitemap.use_lastmod:
                    lastmod_elem = url_elem.find(
                        "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
                    )
                    if lastmod_elem is not None and lastmod_elem.text:
                        try:
                            lastmod = datetime.fromisoformat(
                                lastmod_elem.text.replace("Z", "+00:00")
                            )
                            # For M1, we'll process all URLs
                            # In future milestones, we can add lastmod-based skipping
                            self.logger.debug(f"URL {url} lastmod: {lastmod}")
                        except ValueError as e:
                            self.logger.warning(
                                f"Invalid lastmod format for URL {url}: {e}"
                            )

                urls.append(url)

        return urls

    async def close(self):
        """Close the HTTP client."""
        await self.fetcher.close()
