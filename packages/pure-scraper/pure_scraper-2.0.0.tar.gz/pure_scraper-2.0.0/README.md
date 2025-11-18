# PureScraper 🧠

A **pure Python HTML scraper** that replaces BeautifulSoup for simple data extraction — no external dependencies required for core functionality.

## 🚀 Features
- Fetches HTML using raw sockets (no `requests` library needed)
- Parses HTML into a traversable DOM tree
- Cleans and prettifies malformed HTML
- Removes invalid Unicode / hidden characters
- Extracts data: links, images, tables, and JSON from scripts
- Optional caching with configurable expiry
- Rate limiting support
- Fully extensible and reusable as a local or pip package

## 📦 Installation

### Local install
```bash
pip install .
```

### From PyPI
```bash
pip install pure-scraper
```

## 🎯 Quick Start

### Basic Usage
```python
from pure_scraper.parser import PureScraper
from pure_scraper.fetcher import fetch_html

# Fetch and parse HTML
html = fetch_html("https://example.com")
scraper = PureScraper(html)

# Find elements
links = scraper.get_links()
images = scraper.get_images()
tables = scraper.get_tables()

# Extract text
text = scraper.get_text()

# Pretty print HTML
print(scraper.prettify())
```

### CLI Usage
```bash
pure-scraper https://example.com
```

## 📚 API Reference

### `PureScraper` Class

#### Methods

- **`find(tag=None, attrs=None)`** - Find first element matching tag and attributes
- **`find_all(tag=None, attrs=None)`** - Find all elements matching tag and attributes
- **`get_text()`** - Extract all text content
- **`get_links(tag="a")`** - Extract all links with text and href
- **`get_images(tag="img")`** - Extract all images with src and alt text
- **`get_tables()`** - Extract table data as nested lists
- **`get_html()`** - Get prettified HTML string
- **`prettify()`** - Alias for `get_html()`

#### Attribute Matching

Find elements using attribute selectors:

```python
# Exact match
scraper.find("div", attrs={"class": "container"})

# Regex match
scraper.find("div", attrs={"class": "regex:^item-.*"})
```

### `fetch_html(url, timeout=None, use_cache=None, max_attempts=3)`

Fetches HTML from a URL with automatic retry and caching support.

**Parameters:**
- `url` (str) - URL to fetch
- `timeout` (int) - Socket timeout in seconds (default: 30)
- `use_cache` (bool) - Enable caching (default: True)
- `max_attempts` (int) - Number of retry attempts (default: 3)

**Returns:** HTML string

### Configuration

Set via `pure_scraper.config`:

```python
from pure_scraper.config import config

config.timeout = 30                    # Socket timeout
config.use_cache = True                # Enable caching
config.cache_expiry_hours = 24         # Cache expiry time
config.rate_limit_seconds = 1          # Delay between requests
config.show_logs = True                # Show fetch logs
config.user_agent = "Custom Agent"     # Custom User-Agent
```

## 🏗️ Project Structure

```
pure_scraper/
├── __init__.py          # Package exports
├── parser.py            # HTML parser and DOM tree
├── fetcher.py           # HTTP fetching with socket
├── cache.py             # Caching utilities
├── config.py            # Configuration
├── utils.py             # Utility functions
└── cli.py               # Command-line interface
```

## ⚙️ Technical Details

### Socket-Based HTTP
- Uses Python's built-in `socket` and `ssl` modules
- Supports HTTP/1.1 with automatic redirects
- Handles gzip and deflate compression
- Optional Brotli support

### DOM Tree Structure
- Hierarchical `Node` objects representing HTML elements
- Parent-child relationships preserved
- Efficient traversal and searching

### Caching
- File-based caching with configurable expiry
- Automatic cache invalidation based on age
- Optional per-request cache bypass

## 🔧 Development

### Running Tests
```bash
python test.py
```

### Building Package
```bash
python -m build
```

### Installation for Development
```bash
pip install -e .
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## ⚠️ Notes

- This is a lightweight alternative to BeautifulSoup for simple scraping tasks
- Not recommended for heavily JavaScript-rendered content (use Selenium/Playwright for that)
- Respects robots.txt and be mindful of rate limiting
- Always check the target website's terms of service before scraping
