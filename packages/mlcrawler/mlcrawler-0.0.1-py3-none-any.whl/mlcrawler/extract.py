"""Content extraction and processing using BeautifulSoup and trafilatura."""

import logging
from typing import Optional, NamedTuple

from bs4 import BeautifulSoup
import trafilatura

from .config import Config
from .fetch import FetchResponse


class ExtractedContent(NamedTuple):
    """Extracted and processed content."""

    title: str
    content: str
    extraction_mode: str  # "article" or "fullpage"
    metadata: dict


class ContentExtractor:
    """Extracts and processes HTML content."""

    def __init__(self, config: Config):
        """Initialize the content extractor.

        Args:
            config: Crawler configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def extract(
        self, url: str, response: FetchResponse
    ) -> Optional[ExtractedContent]:
        """Extract content from an HTTP response.

        Args:
            url: URL that was fetched
            response: HTTP response data

        Returns:
            ExtractedContent if successful, None if failed
        """
        if not response.content:
            self.logger.warning(f"No content to extract for {url}")
            return None

        try:
            # Try main article extraction first if configured
            if self.config.extract.main_article:
                extracted = self._extract_main_article(response.content)
                if extracted:
                    return extracted

                self.logger.info(
                    f"Main article extraction failed for {url}, falling back to full page"
                )

            # Fall back to full page extraction
            return self._extract_full_page(url, response.content)

        except Exception as e:
            self.logger.error(f"Content extraction failed for {url}: {e}")
            return None

    def _extract_main_article(self, html: str) -> Optional[ExtractedContent]:
        """Extract main article using trafilatura.

        Args:
            html: Raw HTML content

        Returns:
            ExtractedContent if successful, None if failed
        """
        try:
            # Use trafilatura to extract main article
            extracted_text = trafilatura.extract(
                html,
                include_comments=False,
                include_links=True,
                output_format="txt",  # Plain text output
            )

            if not extracted_text or len(extracted_text.strip()) < 50:
                self.logger.debug(
                    "Trafilatura extraction returned insufficient content"
                )
                return None

            # Get metadata from trafilatura
            metadata = trafilatura.extract_metadata(html)

            # Extract title
            title = ""
            if metadata:
                title = metadata.title or ""

            if not title:
                # Try to extract title from HTML as fallback
                soup = BeautifulSoup(html, "lxml")
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.get_text().strip()

            # Convert plain text to simple markdown (paragraphs)
            content_lines = extracted_text.strip().split("\n")
            # Filter empty lines and join with double newlines for markdown paragraphs
            content_paragraphs = [
                line.strip() for line in content_lines if line.strip()
            ]
            markdown_content = "\n\n".join(content_paragraphs)

            # Build metadata dict
            extracted_metadata = {
                "author": metadata.author if metadata else None,
                "date": metadata.date if metadata else None,
                "description": metadata.description if metadata else None,
                "sitename": metadata.sitename if metadata else None,
            }
            # Remove None values
            extracted_metadata = {
                k: v for k, v in extracted_metadata.items() if v is not None
            }

            return ExtractedContent(
                title=title,
                content=markdown_content,
                extraction_mode="article",
                metadata=extracted_metadata,
            )

        except Exception as e:
            self.logger.debug(f"Trafilatura extraction failed: {e}")
            return None

    def _extract_full_page(self, url: str, html: str) -> ExtractedContent:
        """Extract full page content with filtering.

        Args:
            url: URL being processed
            html: Raw HTML content

        Returns:
            ExtractedContent with filtered and converted content
        """
        # Parse HTML
        soup = BeautifulSoup(html, "lxml")

        # Extract title
        title = self._extract_title(soup)

        # Remove unwanted elements
        self._filter_html(soup)

        # Convert to markdown
        content = self._convert_to_markdown(soup)

        return ExtractedContent(
            title=title, content=content, extraction_mode="fullpage", metadata={}
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from HTML.

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            Page title
        """
        # Try title tag first
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
            if title:
                return title

        # Try h1 tag
        h1_tag = soup.find("h1")
        if h1_tag:
            title = h1_tag.get_text().strip()
            if title:
                return title

        # Try og:title meta tag - skip for now due to typing issues
        # og_title = soup.find('meta', property='og:title')

        return "Untitled"

    def _filter_html(self, soup: BeautifulSoup):
        """Remove unwanted elements from HTML.

        Args:
            soup: BeautifulSoup parsed HTML (modified in-place)
        """
        # Remove standard unwanted elements
        for tag_name in self.config.filter.dom_remove:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Remove additional configured selectors
        for selector in self.config.filter.extra_remove:
            try:
                for element in soup.select(selector):
                    element.decompose()
            except Exception as e:
                self.logger.warning(
                    f"Failed to apply filter selector '{selector}': {e}"
                )

    def _convert_to_markdown(self, soup: BeautifulSoup) -> str:
        """Convert HTML to Markdown.

        Args:
            soup: Filtered BeautifulSoup HTML

        Returns:
            Markdown content
        """
        try:
            from markdownify import markdownify

            # Convert to markdown
            markdown = markdownify(str(soup), heading_style="ATX")

            return markdown

            # # Clean up the markdown
            # lines = markdown.split("\n")
            # cleaned_lines = []

            # for line in lines:
            #     line = line.strip()
            #     if line:  # Skip empty lines
            #         cleaned_lines.append(line)

            # # Join with appropriate spacing
            # return "\n\n".join(cleaned_lines)

        except Exception as e:
            self.logger.error(f"Markdown conversion failed: {e}")
            # Fall back to plain text extraction
            return soup.get_text(separator="\n\n", strip=True)
