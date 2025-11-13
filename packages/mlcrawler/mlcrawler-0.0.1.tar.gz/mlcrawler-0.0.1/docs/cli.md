# CLI Usage

mlcrawler also ships with a CLI powered by Typer. This page documents common commands and flags.

## Entry point

The console script is `mlcrawler` (configured in `pyproject.toml`).

```bash
uv run mlcrawler --help
```

## Common options

- `--url` / `-u` : Seed URL(s) for crawling (can be passed multiple times)
- `--sitemap` / `-s` : Sitemap XML URL for discovery
- `--output` / `-o` : Output directory
- `--no-robots` : Ignore robots.txt (default is to obey)
- `--main-article` : Use trafilatura to extract main article
- `--max-depth` : Maximum crawl depth (seed mode)
- `--max-pages` : Maximum number of pages to crawl
- `--same-domain` / `--cross-domain` : Limit to same domain
- `--follow` : Follow links from seed pages
- `--config` / `-c` : TOML config files to load
- `--verbose` / `-v` : Verbose logging
- `--debug` : Debug logging

## Examples

Crawl using a sitemap:

```bash
uv run mlcrawler --sitemap https://example.com/sitemap.xml
```

Crawl from seeds and follow links:

```bash
uv run mlcrawler --url https://example.com --follow --max-depth 2
```

Use config files:

```bash
uv run mlcrawler --config defaults.toml --config site.toml
```

## Notes

- You cannot specify both `--url` and `--sitemap` at the same time.
- CLI options override configuration file values.
- For advanced usage, use the library API instead of the CLI.
