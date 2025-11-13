"""Link discovery and URL extraction from HTML content."""

import logging
import re
from typing import List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .config import Config


class LinkDiscoverer:
    """Discovers and extracts links from HTML content."""

    def __init__(self, config: Config):
        """Initialize the link discoverer.

        Args:
            config: Crawler configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def extract_links(self, url: str, html: str) -> List[str]:
        """Extract all valid links from HTML content.

        Args:
            url: Base URL for resolving relative links
            html: HTML content to extract links from

        Returns:
            List of absolute URLs found in the HTML
        """
        if not html:
            return []

        try:
            soup = BeautifulSoup(html, "lxml")
            links = set()

            # Extract links from anchor tags
            for a_tag in soup.find_all("a", href=True):
                if hasattr(a_tag, "get"):
                    href = a_tag.get("href")  # type: ignore
                    if href and isinstance(href, str):
                        href = href.strip()
                        if href:
                            absolute_url = urljoin(url, href)
                            normalized_url = self._normalize_url(absolute_url)
                            if normalized_url and self._is_valid_url(
                                normalized_url, url
                            ):
                                links.add(normalized_url)

            # Extract canonical links
            for link_tag in soup.find_all("link", {"rel": "canonical", "href": True}):
                if hasattr(link_tag, "get"):
                    href = link_tag.get("href")  # type: ignore
                    if href and isinstance(href, str):
                        href = href.strip()
                        if href:
                            absolute_url = urljoin(url, href)
                            normalized_url = self._normalize_url(absolute_url)
                            if normalized_url and self._is_valid_url(
                                normalized_url, url
                            ):
                                links.add(normalized_url)

            self.logger.debug(f"Extracted {len(links)} unique links from {url}")
            return list(links)

        except Exception as e:
            self.logger.error(f"Failed to extract links from {url}: {e}")
            return []

    def _normalize_url(self, url: str) -> str:
        """Normalize a URL by removing fragments and normalizing structure.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL, empty string if invalid
        """
        try:
            parsed = urlparse(url)

            # Skip invalid schemes
            if parsed.scheme not in ("http", "https"):
                return ""

            # Skip if no netloc (domain)
            if not parsed.netloc:
                return ""

            # Remove fragment
            normalized = parsed._replace(fragment="").geturl()

            return normalized

        except Exception as e:
            self.logger.debug(f"Failed to normalize URL {url}: {e}")
            return ""

    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if a URL should be crawled based on configuration.

        Args:
            url: URL to validate
            base_url: Base URL for domain comparison

        Returns:
            True if URL should be crawled, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)

            # Skip non-HTTP URLs
            if parsed_url.scheme not in ("http", "https"):
                return False

            # Check same domain restriction
            if self.config.same_domain_only:
                if parsed_url.netloc.lower() != parsed_base.netloc.lower():
                    return False

            # Apply include patterns (safely access)
            try:
                include_patterns = getattr(
                    self.config.discovery, "include_patterns", []
                )
                if include_patterns:
                    if not any(
                        re.search(pattern, url, re.IGNORECASE)
                        for pattern in include_patterns
                    ):
                        return False
            except AttributeError:
                # If include_patterns is not available, skip this check
                pass

            # Apply exclude patterns (safely access)
            try:
                exclude_patterns = getattr(
                    self.config.discovery, "exclude_patterns", []
                )
                if exclude_patterns:
                    if any(
                        re.search(pattern, url, re.IGNORECASE)
                        for pattern in exclude_patterns
                    ):
                        return False
            except AttributeError:
                # If exclude_patterns is not available, skip this check
                pass

            # Skip common non-content URLs
            path = parsed_url.path.lower()
            if any(
                path.endswith(ext)
                for ext in [
                    ".pdf",
                    ".doc",
                    ".docx",
                    ".xls",
                    ".xlsx",
                    ".ppt",
                    ".pptx",
                    ".zip",
                    ".rar",
                    ".tar",
                    ".gz",
                    ".exe",
                    ".dmg",
                    ".pkg",
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".svg",
                    ".ico",
                    ".webp",
                    ".mp3",
                    ".mp4",
                    ".avi",
                    ".mov",
                    ".wmv",
                    ".flv",
                    ".css",
                    ".js",
                    ".xml",
                    ".rss",
                    ".atom",
                    ".json",
                ]
            ):
                return False

            return True

        except Exception as e:
            self.logger.debug(f"URL validation failed for {url}: {e}")
            return False

    def filter_discovered_urls(
        self,
        discovered_urls: List[str],
        processed_urls: Set[str],
        queued_urls: Set[str],
    ) -> List[str]:
        """Filter discovered URLs against already processed/queued URLs.

        Args:
            discovered_urls: List of newly discovered URLs
            processed_urls: Set of URLs already processed
            queued_urls: Set of URLs already in queue

        Returns:
            List of URLs that should be added to queue
        """
        filtered = []

        for url in discovered_urls:
            if url not in processed_urls and url not in queued_urls:
                filtered.append(url)
            else:
                self.logger.debug(f"Skipping already seen URL: {url}")

        return filtered
