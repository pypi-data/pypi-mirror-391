# Installing mlcrawler as a Library

This guide shows how to install and use `mlcrawler` in your own Python projects.

## Installation Methods

### 1. Install from PyPI (Recommended - once published)

```bash
pip install mlcrawler
```

Or with uv:

```bash
uv add mlcrawler
```

### 2. Install from Source (Development)

If you're working with the source code:

```bash
# Clone the repository
git clone <repository-url>
cd mlcrawler

# Install in editable mode
pip install -e .

# Or with uv
uv pip install -e .
```

### 3. Install in Another Project

Add to your project's dependencies:

#### Using pip (requirements.txt)

```txt
mlcrawler>=0.1.0
```

#### Using uv (pyproject.toml)

```bash
cd /path/to/your/project
uv add mlcrawler
```

Or directly from a local path:

```bash
uv add --editable /path/to/mlcrawler
```

#### Using Poetry

```bash
poetry add mlcrawler
```

Or from a local path:

```bash
poetry add /path/to/mlcrawler
```

## Verify Installation

Create a test file `test_mlcrawler.py`:

```python
import asyncio
from mlcrawler import Crawler, Page

async def main():
    print("mlcrawler is installed!")
    
    crawler = Crawler(max_pages=1)
    print(f"Crawler created: {crawler}")
    
    # Quick test
    pages = await crawler.crawl("https://httpbin.org/html")
    print(f"Crawled {len(pages)} page(s)")
    print(f"First page title: {pages[0].title}")

asyncio.run(main())
```

Run it:

```bash
python test_mlcrawler.py
```

Expected output:

```
mlcrawler is installed!
Crawler created: Crawler(max_depth=2, max_pages=1, running=False)
Crawled 1 page(s)
First page title: Herman Melville - Moby-Dick
```

## Dependencies

mlcrawler automatically installs these dependencies:

- `httpx` - HTTP client
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `markdownify` - HTML to Markdown conversion
- `trafilatura` - Main article extraction
- `python-slugify` - URL slugification
- `typer` - CLI framework (for CLI usage)
- `dynaconf` - Configuration management

## Python Version

Requires Python 3.11 or higher.

## Example Project Setup

Here's how to set up a new project that uses mlcrawler:

```bash
# Create project directory
mkdir my-crawler-project
cd my-crawler-project

# Initialize with uv (recommended)
uv init
uv add mlcrawler

# Or with pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install mlcrawler
```

Create `main.py`:

```python
import asyncio
from mlcrawler import Crawler, Page

async def process_page(page: Page):
    """Process each crawled page."""
    print(f"📄 {page.title}")
    print(f"   URL: {page.url}")
    print(f"   Words: {len(page.text.split())}")
    print()

async def main():
    crawler = Crawler(
        max_depth=2,
        max_pages=10,
        follow_links=True,
    )
    
    await crawler.crawl(
        "https://example.com",
        callback=process_page
    )

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
# With uv
uv run python main.py

# Or with standard Python
python main.py
```

## Next Steps

- Read the [Library API Documentation](API.md)
- Check out [example.py](example.py) for more examples
- See [USAGE.md](USAGE.md) for CLI usage

## Troubleshooting

### Import Error

```python
ImportError: No module named 'mlcrawler'
```

**Solution**: Make sure mlcrawler is installed in your current environment:

```bash
pip list | grep mlcrawler
# or
uv pip list | grep mlcrawler
```

### Version Conflicts

If you encounter dependency conflicts, try:

```bash
# With pip
pip install --upgrade mlcrawler

# With uv
uv pip install --upgrade mlcrawler
```

### Python Version

If you get errors about Python version:

```bash
python --version  # Should be 3.11 or higher
```

Upgrade Python or use a compatible version:

```bash
# With uv (automatically manages Python versions)
uv python install 3.11

# Or with pyenv
pyenv install 3.11
pyenv local 3.11
```
