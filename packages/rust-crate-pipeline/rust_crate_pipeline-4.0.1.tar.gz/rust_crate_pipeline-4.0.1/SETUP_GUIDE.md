# Project Setup and Initialization Guide

## Quick Setup

For a complete automated setup, run:

```bash
python setup_project.py
```

This script will:
1. ✅ Install all Python packages from `requirements.txt`
2. ✅ Verify all critical dependencies are installed
3. ✅ Install Playwright Chromium browser (~240 MB)
4. ✅ Verify Crawl4AI configuration
5. ✅ Run post-install setup (Rust tools, LLM providers, etc.)

## Manual Setup Steps

If you prefer to set up manually or the automated script fails:

### 1. Install Python Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### 2. Install Playwright Browsers

```bash
# Install Chromium (required for web scraping)
python -m playwright install chromium

# Or install all browsers (larger download)
python -m playwright install
```

### 3. Verify Critical Packages

The following packages must be installed for the pipeline to work:

**Core Runtime:**
- `crawl4ai` - Web scraping backend
- `playwright` - Browser automation
- `litellm` - Multi-provider LLM support
- `tiktoken` - Token counting
- `aiofiles` - Async file operations
- `redis` - Caching backend
- `cachetools` - In-memory caching
- `requests-cache` - HTTP response caching
- `psutil` - System monitoring
- `spacy` - NLP for Presidio
- `presidio-analyzer` - Privacy analysis
- `toml` - TOML file parsing

**HTTP/2 Support:**
- `httpx` - HTTP client
- `h2` - HTTP/2 protocol
- `hpack` - HTTP/2 header compression
- `hyperframe` - HTTP/2 framing

Verify installation:
```bash
python -c "import crawl4ai, playwright, litellm, tiktoken, aiofiles, redis, cachetools, requests_cache, psutil, spacy, presidio_analyzer, toml; print('All packages installed')"
```

### 4. Run Post-Install Setup

```bash
# Run comprehensive setup
python -m rust_crate_pipeline.setup_manager

# Or use the CLI entry point (after pip install -e .)
rust-crate-setup
```

This will:
- Install Playwright browsers (if not already installed)
- Configure Crawl4AI
- Install Rust analysis tools (if Cargo is available)
- Set up LLM provider configurations
- Create environment variable templates

## Verification

After setup, verify everything works:

```bash
# Test Crawl4AI
python -c "from crawl4ai import AsyncWebCrawler, BrowserConfig; print('Crawl4AI OK')"

# Test Playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# Test LiteLLM
python -c "import litellm; print('LiteLLM OK')"

# Run setup status check
python -m rust_crate_pipeline.setup_manager --check-only
```

## Troubleshooting

### Missing Packages

If packages are missing after installation:

```bash
# Reinstall from requirements.txt
pip install --upgrade -r requirements.txt

# Or install specific missing packages
pip install crawl4ai playwright litellm tiktoken aiofiles redis cachetools requests-cache psutil spacy presidio-analyzer toml
```

### Playwright Browser Issues

```bash
# Reinstall browsers
python -m playwright install --force chromium

# Check browser installation
python -m playwright install --help
```

### Crawl4AI Import Errors

```bash
# Reinstall crawl4ai
pip uninstall crawl4ai
pip install crawl4ai

# Verify Playwright is installed
python -m playwright install chromium
```

## Automated Setup Script

The `setup_project.py` script provides a complete automated setup:

```bash
# Full setup with verbose output
python setup_project.py --verbose

# Skip browser installation (if already installed)
python setup_project.py --skip-browsers
```

## What Gets Installed

### Python Packages (~500+ MB)
- All packages from `requirements.txt`
- Development tools (if using `requirements-dev.txt`)

### Playwright Browsers (~240 MB)
- Chromium browser
- Chromium Headless Shell
- FFMPEG for media support
- Windows dependencies

### Rust Tools (if Cargo available)
- cargo-geiger (unsafe code detection)
- cargo-outdated (dependency updates)
- cargo-license (license analysis)
- cargo-tarpaulin (code coverage)
- cargo-deny (dependency checking)

## Configuration Files

Setup creates configuration files in `~/.rust_crate_pipeline/`:

- `setup_results.json` - Overall setup status
- `crawl4ai_config.json` - Crawl4AI configuration
- `rust_tools_config.json` - Installed Rust tools
- `llm_providers_config.json` - LLM provider settings
- `.env.template` - Environment variable template
- `system_checks.json` - System compatibility checks

## Next Steps

After setup:

1. **Configure LLM Provider** (if using external LLM):
   ```bash
   export OPENAI_API_KEY="your-key"
   # or
   export AZURE_OPENAI_ENDPOINT="your-endpoint"
   export AZURE_OPENAI_API_KEY="your-key"
   ```

2. **Set GitHub Token** (for enhanced GitHub analysis):
   ```bash
   export GITHUB_TOKEN="your-token"
   ```

3. **Run the Pipeline**:
   ```bash
   python run_with_llm.py --help
   ```

## CI/CD Integration

For automated environments, use:

```bash
# Install dependencies
pip install -r requirements.txt

# Install browsers (non-interactive)
python -m playwright install chromium --with-deps

# Run setup (non-interactive)
python -m rust_crate_pipeline.setup_manager
```

