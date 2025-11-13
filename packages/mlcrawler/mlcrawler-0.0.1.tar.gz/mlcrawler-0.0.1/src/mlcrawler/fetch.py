"""HTTP fetching with politeness, disk cache, and conditional requests."""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Optional, NamedTuple

import httpx
from urllib.parse import urlparse
from pathlib import Path

from .config import Config
from .cache import CacheManager


class FetchResponse(NamedTuple):
    """Response from fetching a URL."""

    url: str
    status: int
    content: str
    headers: dict
    fetched_at: datetime
    content_hash: str
    cache_path: Optional[str]
    from_cache: bool


class Fetcher:
    """HTTP fetcher with basic politeness features."""

    def __init__(self, config: Config):
        """Initialize the fetcher.

        Args:
            config: Crawler configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Create HTTP client
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": config.user_agent},
            follow_redirects=True,
        )

        # Track last request time per host for rate limiting
        self.last_request_time = {}

        # Semaphores for concurrency control
        self.global_semaphore = asyncio.Semaphore(config.concurrency.global_)
        self.host_semaphores = {}

        # Disk cache
        self.cache = CacheManager(Path(str(config.cache.dir)))

    async def fetch(
        self, url: str, *, use_cache: Optional[bool] = None
    ) -> Optional[FetchResponse]:
        """Fetch a URL with politeness controls.

        Args:
            url: URL to fetch
            use_cache: If True, serve from cache if available without network.
                       If False, bypass cache and fetch network.
                       If None (default), use conditional GET when possible.

        Returns:
            FetchResponse if successful, None if failed
        """
        # Determine cache policy if unspecified
        if use_cache is None:
            mode = getattr(self.config.cache, "mode", "conditional")
            if mode == "force":
                use_cache = True
            elif mode == "bypass":
                use_cache = False
            else:
                use_cache = None  # conditional

        parsed_url = urlparse(url)
        host = parsed_url.netloc

        # Get or create host semaphore
        if host not in self.host_semaphores:
            self.host_semaphores[host] = asyncio.Semaphore(
                self.config.concurrency.per_host
            )

        async with self.global_semaphore:
            async with self.host_semaphores[host]:
                # Enforce per-host delay
                await self._enforce_delay(host)

                try:
                    return await self._do_fetch(url, use_cache=use_cache)
                except Exception as e:
                    self.logger.error(f"Failed to fetch {url}: {e}")
                    return None

    async def _enforce_delay(self, host: str):
        """Enforce per-host delay between requests.

        Args:
            host: Hostname to check delay for
        """
        if host in self.last_request_time:
            time_since_last = datetime.now() - self.last_request_time[host]
            delay_needed = self.config.rate_limit.per_host_delay_ms / 1000.0

            if time_since_last.total_seconds() < delay_needed:
                sleep_time = delay_needed - time_since_last.total_seconds()
                self.logger.debug(
                    f"Sleeping {sleep_time:.2f}s for host rate limit: {host}"
                )
                await asyncio.sleep(sleep_time)

        self.last_request_time[host] = datetime.now()

    async def _do_fetch(
        self, url: str, *, use_cache: Optional[bool] = None
    ) -> Optional[FetchResponse]:
        """Perform the actual HTTP fetch.

        Args:
            url: URL to fetch
            use_cache: Cache policy, see fetch()

        Returns:
            FetchResponse if successful, None if failed
        """
        self.logger.info(f"Fetching: {url}")
        # Check existing cache entry
        entry = self.cache.entry_for(url)

        # Unconditional cache hit
        if use_cache is True and entry.exists:
            cached = self.cache.read(entry)
            if cached is not None:
                content_hash = hashlib.sha256(cached.encode("utf-8")).hexdigest()
                meta = self.cache.read_metadata(entry) or {}
                headers = meta.get("headers", {})
                fetched_at_str = meta.get("fetched_at")
                fetched_at = (
                    datetime.fromisoformat(str(fetched_at_str))
                    if fetched_at_str
                    else datetime.now()
                )
                self.logger.info(f"Serving from cache (forced): {url}")
                return FetchResponse(
                    url=url,
                    status=meta.get("status", 200),
                    content=cached,
                    headers=headers,
                    fetched_at=fetched_at,
                    content_hash=content_hash,
                    cache_path=str(entry.content_path),
                    from_cache=True,
                )

        # Age-based cache hit for entries without proper cache validation headers
        if (
            use_cache is None
            and entry.exists
            and not entry.etag
            and not entry.last_modified
        ):
            ttl = getattr(self.config.cache, "ttl_seconds", 3600)
            if self.cache.is_fresh(entry, ttl):
                cached = self.cache.read(entry)
                if cached is not None:
                    content_hash = hashlib.sha256(cached.encode("utf-8")).hexdigest()
                    meta = self.cache.read_metadata(entry) or {}
                    headers = meta.get("headers", {})
                    fetched_at_str = meta.get("fetched_at")
                    fetched_at = (
                        datetime.fromisoformat(str(fetched_at_str))
                        if fetched_at_str
                        else datetime.now()
                    )
                    self.logger.info(
                        f"Serving from cache (fresh, no validators): {url}"
                    )
                    return FetchResponse(
                        url=url,
                        status=meta.get("status", 200),
                        content=cached,
                        headers=headers,
                        fetched_at=fetched_at,
                        content_hash=content_hash,
                        cache_path=str(entry.content_path),
                        from_cache=True,
                    )

        try:
            # Build conditional headers if applicable
            request_headers = {}
            if (
                use_cache is None
                and entry.exists
                and self.config.cache.respect_conditional
            ):
                if entry.etag:
                    request_headers["If-None-Match"] = entry.etag
                    self.logger.debug(f"Adding If-None-Match: {entry.etag}")
                if entry.last_modified:
                    request_headers["If-Modified-Since"] = entry.last_modified
                    self.logger.debug(
                        f"Adding If-Modified-Since: {entry.last_modified}"
                    )

            if request_headers:
                self.logger.debug(
                    f"Sending conditional request headers: {request_headers}"
                )
            else:
                self.logger.debug("No conditional headers to send")

            response = await self.client.get(url, headers=request_headers)

            # Check if we got a successful response
            if response.status_code >= 400:
                self.logger.warning(f"HTTP {response.status_code} for {url}")
                # For M1, we'll still process 4xx responses
                # In future milestones, we might want to be more selective

            # Handle 304 Not Modified using cache
            if response.status_code == 304 and entry.exists:
                cached = self.cache.read(entry)
                if cached is not None:
                    content_hash = hashlib.sha256(cached.encode("utf-8")).hexdigest()
                    # Update metadata timestamps/headers
                    self.cache.update_metadata(
                        entry,
                        status=entry and 200 or 200,
                        headers=dict(response.headers),
                        fetched_at=datetime.now(),
                    )
                    meta = self.cache.read_metadata(entry) or {}
                    return FetchResponse(
                        url=url,
                        status=200,
                        content=cached,
                        headers=meta.get("headers", {}),
                        fetched_at=datetime.fromisoformat(str(meta.get("fetched_at")))
                        if meta.get("fetched_at")
                        else datetime.now(),
                        content_hash=content_hash,
                        cache_path=str(entry.content_path),
                        from_cache=True,
                    )

            # Get response content
            content = response.text

            # Calculate content hash
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Store in cache
            content_type = response.headers.get("content-type")
            entry = self.cache.write(
                url=url,
                content=content,
                status=response.status_code,
                headers=dict(response.headers),
                fetched_at=datetime.now(),
                content_type_hint=content_type,
            )

            # Create response object
            fetch_response = FetchResponse(
                url=url,
                status=response.status_code,
                content=content,
                headers=dict(response.headers),
                fetched_at=datetime.now(),
                content_hash=content_hash,
                cache_path=str(entry.content_path),
                from_cache=False,
            )

            self.logger.info(
                f"Successfully fetched {url} ({len(content)} chars, {response.status_code})"
            )
            return fetch_response

        except httpx.TimeoutException:
            self.logger.error(f"Timeout fetching {url}")
            return None
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
