"""Disk cache management for fetched resources (HTML, sitemaps, etc.).

Uses real URL paths and names (no hashes). Query strings are appended to the
filename as a suffix to keep entries unique. Sidecar ``.meta.json`` stores
response metadata for conditional requests and observability.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse, unquote


# Content-Type to default extension mapping
DEFAULT_EXT_BY_TYPE = {
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "application/xml": ".xml",
    "text/xml": ".xml",
    "application/json": ".json",
}


def _choose_ext(path: str, content_type: Optional[str], fallback: str = ".html") -> str:
    # If URL path already has an extension, keep it
    last = path.rsplit("/", 1)[-1]
    if "." in last and not last.endswith("."):
        return ""  # keep as-is; caller shouldn't add extension

    if content_type:
        # Strip charset or parameters
        ct = content_type.split(";")[0].strip().lower()
        ext = DEFAULT_EXT_BY_TYPE.get(ct)
        if ext:
            return ext
    return fallback


def _sanitize_query(qs: str) -> str:
    """Sanitize query string for filesystem usage.

    Keep it readable and reversible without hashing. Replace path separators
    to avoid creating unintended directories.
    """
    if not qs:
        return ""
    # Decode for readability, then neutralize path separators
    decoded = unquote(qs)
    safe = decoded.replace("/", "_").replace("&", "_").replace("?", "_")
    return safe


@dataclass
class CacheEntry:
    content_path: Path
    metadata_path: Path
    exists: bool
    # Optional fields extracted from metadata (when exists=True)
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    content_type: Optional[str] = None


class CacheManager:
    """Manages disk cache paths and read/write of cached resources."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def _paths_for(
        self, url: str, content_type_hint: Optional[str] = None
    ) -> Tuple[Path, Path]:
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path or "/"
        query = parsed.query

        # Build directory under host preserving path components
        # Decode for filesystem readability
        path_decoded = unquote(path)

        # Determine base directory and base filename
        if path_decoded.endswith("/"):
            dir_rel = path_decoded.strip("/")  # may be '' for root
            base_name = "index"
            keep_ext = False
        else:
            parts = path_decoded.strip("/").split("/") if path_decoded != "/" else []
            if parts:
                base_name = parts[-1]
                dir_rel = "/".join(parts[:-1])
                keep_ext = "." in base_name
            else:
                dir_rel = ""
                base_name = "index"
                keep_ext = False

        # Append query suffix if present (keeps cache key distinct for different queries)
        if query:
            base_name = f"{base_name}___{_sanitize_query(query)}"

        # Decide extension
        ext = _choose_ext(path_decoded, content_type_hint)
        filename = base_name if keep_ext else base_name + ext

        # Compose full paths
        host_dir = self.base_dir / host
        full_dir = host_dir if not dir_rel else host_dir / Path(dir_rel)
        content_path = full_dir / filename
        metadata_path = full_dir / (filename + ".meta.json")
        return content_path, metadata_path

    def entry_for(
        self, url: str, content_type_hint: Optional[str] = None
    ) -> CacheEntry:
        # If no content type hint, try to find existing cache files with any extension
        if not content_type_hint:
            # Try common extensions to find existing cache entry
            for ct in [
                None,
                "text/html",
                "application/json",
                "application/xml",
                "text/xml",
            ]:
                content_path, metadata_path = self._paths_for(url, ct)
                if content_path.exists() and metadata_path.exists():
                    # Found existing entry, load its metadata
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        headers = meta.get("headers", {})
                        etag = headers.get("etag") or headers.get("ETag")
                        last_modified = headers.get("last-modified") or headers.get(
                            "Last-Modified"
                        )
                        content_type = headers.get("content-type") or headers.get(
                            "Content-Type"
                        )
                        self.logger.debug(
                            f"Found existing cache entry for {url}: {content_path} etag={etag} last_modified={last_modified}"
                        )
                        return CacheEntry(
                            content_path=content_path,
                            metadata_path=metadata_path,
                            exists=True,
                            etag=etag,
                            last_modified=last_modified,
                            content_type=content_type,
                        )
                    except Exception as e:
                        self.logger.debug(
                            f"Failed to read cache metadata for {url}: {e}"
                        )
                        continue

            # No existing entry found, return new entry with default extension
            content_path, metadata_path = self._paths_for(url, content_type_hint)
            self.logger.debug(
                f"No existing cache entry for {url}, will use: {content_path}"
            )
            return CacheEntry(
                content_path=content_path,
                metadata_path=metadata_path,
                exists=False,
            )

        # Content type hint provided, use it directly
        content_path, metadata_path = self._paths_for(url, content_type_hint)
        exists = content_path.exists() and metadata_path.exists()

        self.logger.debug(
            f"entry_for {url}: content_path={content_path} exists={exists}"
        )

        etag = last_modified = content_type = None
        if exists:
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                # Accept common keys
                headers = meta.get("headers", {})
                etag = headers.get("etag") or headers.get("ETag")
                last_modified = headers.get("last-modified") or headers.get(
                    "Last-Modified"
                )
                content_type = headers.get("content-type") or headers.get(
                    "Content-Type"
                )
                self.logger.debug(
                    f"Cache entry for {url}: {content_path} etag={etag} last_modified={last_modified}"
                )
            except Exception as e:
                # Treat as miss if metadata is unreadable
                self.logger.debug(f"Failed to read cache metadata for {url}: {e}")
                exists = False

        return CacheEntry(
            content_path=content_path,
            metadata_path=metadata_path,
            exists=exists,
            etag=etag,
            last_modified=last_modified,
            content_type=content_type,
        )

    def read(self, entry: CacheEntry) -> Optional[str]:
        if not entry.exists:
            return None
        try:
            with open(entry.content_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def write(
        self,
        url: str,
        content: str,
        status: int,
        headers: dict,
        fetched_at: Optional[datetime] = None,
        content_type_hint: Optional[str] = None,
    ) -> CacheEntry:
        # Determine target paths with content-type hint
        entry = self.entry_for(url, content_type_hint or headers.get("content-type"))
        entry.content_path.parent.mkdir(parents=True, exist_ok=True)

        with open(entry.content_path, "w", encoding="utf-8") as f:
            f.write(content)

        meta = {
            "url": url,
            "status": status,
            "headers": dict(headers),
            "fetched_at": (fetched_at or datetime.now()).isoformat(),
            "size_bytes": len(content.encode("utf-8")),
        }
        with open(entry.metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        # Return a refreshed entry marked as existing
        return self.entry_for(url, content_type_hint or headers.get("content-type"))

    def update_metadata(
        self,
        entry: CacheEntry,
        status: int,
        headers: dict,
        fetched_at: Optional[datetime] = None,
    ) -> None:
        entry.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(entry.metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}
        meta["status"] = status
        meta["headers"] = dict(headers)
        meta["fetched_at"] = (fetched_at or datetime.now()).isoformat()
        with open(entry.metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    def is_fresh(self, entry: CacheEntry, ttl_seconds: int = 3600) -> bool:
        """Check if a cache entry is fresh based on age.

        Args:
            entry: Cache entry to check
            ttl_seconds: Maximum age in seconds

        Returns:
            True if the entry is fresh enough to use without revalidation
        """
        if not entry.exists:
            return False

        meta = self.read_metadata(entry)
        if not meta:
            return False

        try:
            fetched_at = datetime.fromisoformat(meta["fetched_at"])
            age = (datetime.now() - fetched_at).total_seconds()
            return age < ttl_seconds
        except (KeyError, ValueError):
            return False

    def read_metadata(self, entry: CacheEntry) -> Optional[dict]:
        if not entry.exists:
            return None
        try:
            with open(entry.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
