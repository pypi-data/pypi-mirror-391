"""Example usage of mlcrawler as a library.

This demonstrates various ways to use mlcrawler programmatically
for crawling websites and processing content with callbacks.
"""

import asyncio
import logging
from pathlib import Path

from mlcrawler import Crawler, Page


# ═══════════════════════════════════════════════════════════
# Example 1: Simple callback-based crawling
# ═══════════════════════════════════════════════════════════


async def example_simple_callback():
    """Basic example: crawl a site and process each page."""
    print("\n" + "=" * 60)
    print("Example 1: Simple callback-based crawling")
    print("=" * 60)

    async def process_page(page: Page):
        """Called for each crawled page."""
        print(f"📄 {page.title}")
        print(f"   URL: {page.url}")
        print(f"   Content: {len(page.markdown)} chars")
        print(f"   From cache: {page.from_cache}")
        print()

    # Create crawler with basic configuration
    crawler = Crawler(
        max_depth=1,  # Only crawl 1 level deep
        max_pages=5,  # Limit to 5 pages
        follow_links=True,
        same_domain_only=True,
    )

    # Crawl and process pages
    pages = await crawler.crawl(
        "https://httpbin.org/html", callback=process_page
    )

    print(f"✅ Crawled {len(pages)} pages total")


# ═══════════════════════════════════════════════════════════
# Example 2: Event hooks for different stages
# ═══════════════════════════════════════════════════════════


async def example_event_hooks():
    """Example using event hooks for fine-grained control."""
    print("\n" + "=" * 60)
    print("Example 2: Event hooks")
    print("=" * 60)

    crawler = Crawler(max_depth=0, max_pages=3)

    # Hook: before fetching
    @crawler.on("fetch")
    async def on_fetch(url: str):
        print(f"⬇️  Fetching: {url}")

    # Hook: after processing page
    @crawler.on("page")
    async def on_page(page: Page):
        print(f"✅ Processed: {page.title} ({page.status_code})")

    # Hook: on error
    @crawler.on("error")
    async def on_error(url: str, error: Exception):
        print(f"❌ Error on {url}: {error}")

    # Hook: when complete
    @crawler.on("complete")
    async def on_complete(stats: dict):
        print(f"\n🏁 Crawl complete! {stats['pages']} pages crawled")

    await crawler.crawl("https://httpbin.org/json")


# ═══════════════════════════════════════════════════════════
# Example 3: Streaming API for memory efficiency
# ═══════════════════════════════════════════════════════════


async def example_streaming():
    """Stream pages as they're crawled."""
    print("\n" + "=" * 60)
    print("Example 3: Streaming API")
    print("=" * 60)

    crawler = Crawler(max_pages=3, follow_links=True)

    async with crawler:
        count = 0
        async for page in crawler.stream("https://httpbin.org/html"):
            count += 1
            print(f"{count}. {page.title} ({page.url})")

            # Could break early if needed
            if count >= 3:
                break


# ═══════════════════════════════════════════════════════════
# Example 4: Multiple seed URLs
# ═══════════════════════════════════════════════════════════


async def example_multiple_seeds():
    """Crawl multiple starting URLs."""
    print("\n" + "=" * 60)
    print("Example 4: Multiple seed URLs")
    print("=" * 60)

    crawler = Crawler(max_depth=0, follow_links=False)

    pages = await crawler.crawl_many(
        [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
        ]
    )

    for page in pages:
        print(f"• {page.url} → {len(page.markdown)} chars")


# ═══════════════════════════════════════════════════════════
# Example 5: Advanced configuration
# ═══════════════════════════════════════════════════════════


async def example_advanced_config():
    """Example with advanced configuration options."""
    print("\n" + "=" * 60)
    print("Example 5: Advanced configuration")
    print("=" * 60)

    crawler = Crawler(
        user_agent="MyBot/1.0 (+https://example.com)",
        max_depth=2,
        max_pages=10,
        main_article_only=True,  # Extract main content only
        cache_dir=".cache/example",
        follow_links=True,
        same_domain_only=True,
        obey_robots=True,
        rate_limit_ms=500,  # 500ms delay between requests
        concurrency=4,  # Max 4 concurrent requests
        per_host_concurrency=2,  # Max 2 per host
        remove_selectors=["nav", "footer", ".ads"],
        save_to_disk=False,  # Don't save to disk
    )

    async def process(page: Page):
        extraction = "🎯 article" if page.is_main_article else "📄 full page"
        print(f"{extraction}: {page.title} (depth {page.depth})")

    await crawler.crawl("https://httpbin.org/html", callback=process)


# ═══════════════════════════════════════════════════════════
# Example 6: Save to custom storage
# ═══════════════════════════════════════════════════════════


async def example_custom_storage():
    """Process pages and save to custom storage."""
    print("\n" + "=" * 60)
    print("Example 6: Custom storage")
    print("=" * 60)

    # In-memory storage
    database = []

    async def save_to_db(page: Page):
        """Save page to our 'database'."""
        record = {
            "url": page.url,
            "title": page.title,
            "content_length": len(page.markdown),
            "fetched_at": page.fetched_at.isoformat(),
            "depth": page.depth,
        }
        database.append(record)
        print(f"💾 Saved: {page.title}")

    crawler = Crawler(max_pages=3, save_to_disk=False)
    await crawler.crawl("https://httpbin.org/html", callback=save_to_db)

    print(f"\n📊 Database contains {len(database)} records:")
    for record in database:
        print(f"   • {record['title']} ({record['content_length']} chars)")


# ═══════════════════════════════════════════════════════════
# Example 7: Load from config file
# ═══════════════════════════════════════════════════════════


async def example_from_config():
    """Load configuration from TOML file."""
    print("\n" + "=" * 60)
    print("Example 7: Load from config file")
    print("=" * 60)

    # Check if config file exists
    config_file = Path("examples/defaults.toml")
    if not config_file.exists():
        print(f"⚠️  Config file not found: {config_file}")
        print("   Skipping this example")
        return

    # Load from config and override some settings
    crawler = Crawler.from_config(
        "examples/defaults.toml",
        max_pages=3,  # Override max_pages
    )

    pages = await crawler.crawl("https://httpbin.org/html")
    print(f"✅ Crawled {len(pages)} pages using config file")


# ═══════════════════════════════════════════════════════════
# Main: Run all examples
# ═══════════════════════════════════════════════════════════


async def main():
    """Run all examples."""
    # Set up logging
    logging.basicConfig(
        level=logging.WARNING,  # Set to INFO or DEBUG for more details
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Suppress httpx/httpcore logs for cleaner output
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    print("\n🚀 mlcrawler Library Examples")
    print("=" * 60)

    # Run examples
    await example_simple_callback()
    await example_event_hooks()
    await example_streaming()
    await example_multiple_seeds()
    await example_advanced_config()
    await example_custom_storage()
    await example_from_config()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
