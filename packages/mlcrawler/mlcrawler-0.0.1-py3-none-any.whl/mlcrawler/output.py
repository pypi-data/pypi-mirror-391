"""Output writing for markdown files and metadata."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

from slugify import slugify

from .config import Config
from .extract import ExtractedContent
from .fetch import FetchResponse


class OutputWriter:
    """Writes extracted content and metadata to files."""

    def __init__(self, config: Config):
        """Initialize the output writer.

        Args:
            config: Crawler configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def write(
        self,
        url: str,
        content: ExtractedContent,
        response: FetchResponse,
        extra_metadata: Optional[Dict] = None,
    ):
        """Write content and metadata to output files.

        Args:
            url: Original URL
            content: Extracted content
            response: HTTP response data
            extra_metadata: Additional metadata to include in output
        """
        if extra_metadata is None:
            extra_metadata = {}

        try:
            # Generate file paths
            markdown_path, metadata_path = self._generate_paths(url)

            # Ensure output directories exist
            markdown_path.parent.mkdir(parents=True, exist_ok=True)

            # Write markdown content
            await self._write_markdown(markdown_path, content)

            # Write metadata
            await self._write_metadata(
                metadata_path, url, content, response, extra_metadata
            )

            self.logger.info(f"Wrote output for {url} -> {markdown_path}")

        except Exception as e:
            self.logger.error(f"Failed to write output for {url}: {e}")
            raise

    def _generate_paths(self, url: str) -> tuple[Path, Path]:
        """Generate output file paths for a URL.

        Args:
            url: URL to generate paths for

        Returns:
            Tuple of (markdown_path, metadata_path)
        """
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path

        # Clean up path
        if path.endswith("/"):
            if path == "/":
                # Root path
                filename = "index"
                directory_path = ""
            else:
                # Directory path - use index.md and preserve directory structure
                directory_path = path.strip("/")
                filename = "index"
        else:
            # File path - extract filename and preserve directory structure
            path_parts = path.strip("/").split("/")
            if path_parts:
                # Remove file extension if present and use base name
                filename = path_parts[-1]
                if "." in filename:
                    filename = filename.rsplit(".", 1)[0]
                # Directory is everything except the filename
                directory_path = (
                    "/".join(path_parts[:-1]) if len(path_parts) > 1 else ""
                )
            else:
                filename = "index"
                directory_path = ""

        # Slugify filename for filesystem safety
        filename = slugify(filename) or "page"

        # Build full directory path
        domain_dir = self.config.output.dir / domain
        if directory_path:
            # Slugify each directory component for filesystem safety
            dir_parts = [slugify(part) or "dir" for part in directory_path.split("/")]
            full_dir = domain_dir / Path(*dir_parts)
        else:
            full_dir = domain_dir

        # Create full paths
        markdown_path = full_dir / f"{filename}.md"
        metadata_path = full_dir / f"{filename}.meta.json"

        return markdown_path, metadata_path

    async def _write_markdown(self, path: Path, content: ExtractedContent):
        """Write markdown content to file.

        Args:
            path: Output file path
            content: Content to write
        """
        # Build markdown file content
        markdown_content = []

        # Add title as header if present
        if content.title:
            markdown_content.append(f"# {content.title}")
            markdown_content.append("")

        # Add main content
        if content.content:
            markdown_content.append(content.content)

        # Write to file
        full_content = "\n".join(markdown_content)

        with open(path, "w", encoding="utf-8") as f:
            f.write(full_content)

    async def _write_metadata(
        self,
        path: Path,
        url: str,
        content: ExtractedContent,
        response: FetchResponse,
        extra_metadata: Optional[Dict] = None,
    ):
        """Write metadata to sidecar JSON file.

        Args:
            path: Metadata file path
            url: Original URL
            content: Extracted content
            response: HTTP response data
            extra_metadata: Additional metadata to include
        """
        if extra_metadata is None:
            extra_metadata = {}

        # Build metadata object
        metadata = {
            "url": url,
            "title": content.title,
            "fetched_at": response.fetched_at.isoformat(),
            "last_modified": response.headers.get("last-modified"),
            "etag": response.headers.get("etag"),
            "source": extra_metadata.get(
                "source", "sitemap"
            ),  # Use from extra_metadata if available
            "depth": extra_metadata.get(
                "depth", 0
            ),  # Use from extra_metadata if available
            "status": response.status,
            "content_hash": response.content_hash,
            "cache_path": response.cache_path,
            "extraction_mode": content.extraction_mode,
        }

        # Add trafilatura metadata if present
        if content.metadata:
            metadata["trafilatura_metadata"] = content.metadata

        # Add any additional metadata
        for key, value in extra_metadata.items():
            if key not in metadata:  # Don't override existing keys
                metadata[key] = value

        # Write metadata file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
