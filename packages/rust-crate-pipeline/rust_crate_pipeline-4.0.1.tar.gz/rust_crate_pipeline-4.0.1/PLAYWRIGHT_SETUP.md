# Playwright and Crawl4AI Setup Guide

## Installation Steps

### 1. Install Python Packages
```bash
pip install crawl4ai playwright
```

### 2. Install Playwright Browsers
```bash
python -m playwright install chromium
```

This downloads:
- Chromium browser (~149 MB)
- FFMPEG for media support (~1.3 MB)
- Chromium Headless Shell (~91 MB)
- Windows dependencies (~0.1 MB)

**Total download size:** ~241 MB

### 3. Verify Installation
```python
from crawl4ai import AsyncWebCrawler, BrowserConfig
config = BrowserConfig(headless=True, browser_type='chromium')
print("Crawl4AI is ready!")
```

## Configuration

The scraper is automatically configured when:
- `crawl4ai` package is installed
- Playwright browsers are installed
- The `UnifiedScraper` class initializes successfully

### Default Configuration
- **Browser**: Chromium (headless mode)
- **Headless**: True (no visible browser window)
- **Verbose**: False (minimal logging)

### Custom Configuration
You can pass configuration when creating the scraper:
```python
config = {
    "headless": True,
    "browser_type": "chromium",  # or "firefox", "webkit"
    "verbose": False,
    "word_count_threshold": 10,
    "screenshot": False
}
scraper = UnifiedScraper(config=config)
```

## Troubleshooting

### "No crawler backend available" Error
1. **Check if crawl4ai is installed:**
   ```bash
   pip list | grep crawl4ai
   ```

2. **Check if playwright browsers are installed:**
   ```bash
   python -m playwright install --help
   ```

3. **Reinstall if needed:**
   ```bash
   pip uninstall crawl4ai playwright
   pip install crawl4ai playwright
   python -m playwright install chromium
   ```

### Browser Launch Failures
- Ensure Windows dependencies are installed (usually automatic)
- Check antivirus isn't blocking browser execution
- Try running with `headless=False` to see browser window for debugging

### Memory Issues
- Crawl4AI uses significant memory for browser automation
- Consider reducing concurrent scraping operations
- Use `headless=True` to reduce memory usage

## What Gets Scraped

With Crawl4AI configured, the pipeline can scrape:
- **crates.io**: Crate documentation and metadata
- **docs.rs**: API documentation
- **lib.rs**: Alternative crate documentation
- **GitHub**: Repository README and documentation (already working)

## Performance Notes

- Browser automation is slower than simple HTTP requests
- Each scrape operation launches a browser instance
- Consider caching scraped content to avoid repeated requests
- The scraper uses async operations for better concurrency

