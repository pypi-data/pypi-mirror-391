#!/usr/bin/env python3
"""CLI interface for mlcrawler using Typer."""

import asyncio
from pathlib import Path
from typing import List, Optional

import typer

from . import __version__
from .config import Config, create_config, validate_config
from .crawl import CrawlController


def main(
    url: List[str] = typer.Option(
        [],
        "--url",
        "-u",
        help="Seed URL(s) for crawling. Can be specified multiple times.",
    ),
    sitemap: Optional[str] = typer.Option(
        None,
        "--sitemap",
        "-s",
        help="Sitemap XML URL for discovery.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for markdown files. Default: 'output'",
    ),
    markdown: bool = typer.Option(
        True,
        "--markdown/--no-markdown",
        help="Convert content to markdown (default: true)",
    ),
    no_robots: bool = typer.Option(
        False, "--no-robots", help="Ignore robots.txt (default: obey robots.txt)"
    ),
    main_article: bool = typer.Option(
        False,
        "--main-article",
        help="Extract main article content only using trafilatura",
    ),
    max_depth: Optional[int] = typer.Option(
        None,
        "--max-depth",
        help="Maximum crawl depth for seed mode (default: 2, 0=unlimited)",
    ),
    max_pages: Optional[int] = typer.Option(
        None,
        "--max-pages",
        help="Maximum number of pages to crawl (default: unlimited)",
    ),
    same_domain_only: bool = typer.Option(
        True,
        "--same-domain/--cross-domain",
        help="Only crawl URLs from the same domain (default: true)",
    ),
    follow: bool = typer.Option(
        False,
        "--follow",
        help="Follow links found on seed pages to crawl additional pages (seed mode only)",
    ),
    config: List[Path] = typer.Option(
        [],
        "--config",
        "-c",
        help="Configuration file(s) to load (TOML). Later files override earlier ones.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging (includes HTTP requests)"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging (most detailed)"
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Show version and exit",
        is_eager=True,
    ),
):
    """mlcrawler - A configurable web crawler.

    Examples:
      uv run mlcrawler --url https://example.com --output ./example.com
      uv run mlcrawler --url https://example.com --follow --max-depth 2
      uv run mlcrawler --sitemap https://example.com/sitemap.xml --main-article
      uv run mlcrawler --url https://example.com --max-depth 1 --no-robots
    """
    if version:
        typer.echo(f"mlcrawler {__version__}")
        raise typer.Exit()

    # Check if we have any crawling arguments
    if not url and not sitemap:
        if not config:
            typer.echo(
                "Error: Must specify either --url, --sitemap, or --config", err=True
            )
            typer.echo("Use --help for usage information", err=True)
            raise typer.Exit(1)

    if url and sitemap:
        typer.echo("Error: Cannot specify both --url and --sitemap options", err=True)
        raise typer.Exit(1)

    try:
        # Run the crawler
        asyncio.run(
            _run_crawler_from_args(
                url=url,
                sitemap=sitemap,
                output=output,
                markdown=markdown,
                no_robots=no_robots,
                main_article=main_article,
                max_depth=max_depth,
                max_pages=max_pages,
                same_domain_only=same_domain_only,
                follow=follow,
                config=config,
                verbose=verbose,
                debug=debug,
            )
        )
    except KeyboardInterrupt:
        typer.echo("\nCrawl interrupted by user", err=True)
        raise typer.Exit(130)


async def _run_crawler_from_args(
    url: List[str],
    sitemap: Optional[str],
    output: Optional[str],
    markdown: bool,
    no_robots: bool,
    main_article: bool,
    max_depth: Optional[int],
    max_pages: Optional[int],
    same_domain_only: bool,
    follow: bool,
    config: List[Path],
    verbose: bool,
    debug: bool,
):
    """Run the crawler with arguments from CLI."""
    try:
        # Determine mode based on arguments
        mode = None
        seeds = []
        sitemap_url = None

        if url:
            mode = "seed"
            seeds = list(url)
        elif sitemap:
            mode = "sitemap"
            sitemap_url = sitemap

        # Look for default config files if none specified
        if not config:
            default_configs = [
                Path("defaults.toml"),
                Path("mlcrawler.toml"),
                Path("config.toml"),
            ]
            config = [c for c in default_configs if c.exists()]

        # Build configuration overrides from CLI args
        overrides = {}
        if mode:
            overrides["mode"] = mode
        if seeds:
            overrides["seeds"] = seeds
        if not no_robots:  # Default is to obey robots
            overrides["obey_robots"] = True
        else:
            overrides["obey_robots"] = False
        if max_depth is not None:
            overrides["max_depth"] = max_depth
        overrides["same_domain_only"] = same_domain_only

        # Set discovery.follow_links based on --follow flag
        overrides["discovery"] = overrides.get("discovery", {})
        overrides["discovery"]["follow_links"] = follow

        # Load and merge configurations
        try:
            dynaconf_config = create_config(config, **overrides)

            # Apply nested overrides manually after creation
            if sitemap_url:
                # Ensure sitemap section exists and set URL
                if (
                    not hasattr(dynaconf_config, "sitemap")
                    or not dynaconf_config.sitemap
                ):
                    dynaconf_config.sitemap = {}
                dynaconf_config.sitemap["url"] = sitemap_url  # type: ignore

            if output:
                if not hasattr(dynaconf_config, "output") or not dynaconf_config.output:
                    dynaconf_config.output = {}
                dynaconf_config.output["dir"] = output  # type: ignore

            if main_article:
                if (
                    not hasattr(dynaconf_config, "extract")
                    or not dynaconf_config.extract
                ):
                    dynaconf_config.extract = {}
                dynaconf_config.extract["main_article"] = main_article  # type: ignore

            if max_pages is not None:
                if not hasattr(dynaconf_config, "limits") or not dynaconf_config.limits:
                    dynaconf_config.limits = {}
                dynaconf_config.limits["max_pages"] = max_pages  # type: ignore

            validate_config(dynaconf_config)
            cfg = Config(dynaconf_config)

        except ValueError as e:
            typer.echo(f"Configuration validation error: {e}", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Failed to load configuration: {e}", err=True)
            raise typer.Exit(1)

        # Validate final configuration
        if cfg.mode == "seed" and not cfg.seeds:
            typer.echo("Seed mode requires at least one seed URL", err=True)
            raise typer.Exit(1)
        if cfg.mode == "sitemap" and not cfg.sitemap.url and not cfg.seeds:
            typer.echo(
                "Sitemap mode requires either sitemap URL or seed URLs for discovery",
                err=True,
            )
            raise typer.Exit(1)

        # Run the crawler
        await _run_crawler(cfg, verbose, debug)

    except Exception as e:
        typer.echo(f"Crawl failed: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(1)


async def _run_crawler(config: Config, verbose: bool, debug: bool):
    """Run the crawler with given configuration."""
    controller = CrawlController(config)

    # Set up logging based on debug/verbose flags
    # Configure logging
    import logging

    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Configure httpx and httpcore logging
    if debug:
        # Debug mode: show everything
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("httpcore").setLevel(logging.DEBUG)
    elif verbose:
        # Verbose mode: show httpx but not httpcore debug
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
    else:
        # Default mode: hide HTTP details
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

    try:
        await controller.crawl()
        typer.echo("Crawl completed successfully!")
    except Exception as e:
        typer.echo(f"Crawl failed: {e}", err=True)
        raise


def cli_main():
    """Entry point for console script."""
    typer.run(main)
