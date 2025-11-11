# Grasp Python SDK

Official Python SDK for the Grasp browser automation platform.

## Features

- **Dual Client Architecture**: Both synchronous and asynchronous clients
- **Type Safety**: Full type hints and Pydantic models for validation
- **Browser Automation**: Seamless integration with Playwright and Puppeteer
- **Proxy Support**: Built-in proxy configuration for different use cases
- **Error Handling**: Comprehensive exception hierarchy
- **Auto-retry**: Automatic retry with exponential backoff

## Installation

```bash
pip install grasp-sdk
```

## Quick Start

### Synchronous Usage

```python
from grasp import Grasp

# Initialize client
client = Grasp(api_key="your-api-key")  # or set GRASP_API_KEY env var

# Create a container
container = client.create(
    idle_timeout=30000,  # 30 seconds
    proxy={
        "enabled": True,
        "type": "residential",
        "country": "US"
    }
)

# Access browser information
print(f"Container ID: {container.id}")
print(f"CDP WebSocket: {container.browser.ws_endpoint}")
print(f"Live View: {container.browser.live_url}")

# Shutdown when done
container.shutdown()
```

### Asynchronous Usage

```python
import asyncio
from grasp import AsyncGrasp

async def main():
    # Use context manager for automatic cleanup
    async with AsyncGrasp(api_key="your-api-key") as client:
        # Create container
        container = await client.create(idle_timeout=30000)

        # Use the container
        print(f"Container ID: {container.id}")

        # Shutdown
        await container.shutdown()

asyncio.run(main())
```

### Playwright Integration

```python
from grasp import Grasp
from playwright.sync_api import sync_playwright

# Create Grasp container
grasp = Grasp()
container = grasp.create()

# Connect Playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(container.browser.ws_endpoint)
    page = browser.new_page()
    page.goto("https://example.com")

    # Your automation code here
    title = page.title()
    print(f"Page title: {title}")

    browser.close()

# Cleanup
container.shutdown()
```

## Configuration

### Environment Variables

- `GRASP_API_KEY`: Your API key (alternative to passing in code)
- `GRASP_BASE_URL`: API base URL (defaults to `https://api.getgrasp.ai`)

### Client Options

```python
client = Grasp(
    api_key="your-api-key",
    base_url="https://api.getgrasp.ai",  # optional
    timeout=60.0,  # request timeout in seconds
    max_retries=2  # maximum retry attempts
)
```

### Container Options

```python
container = client.create(
    idle_timeout=30000,  # milliseconds before container sleeps
    proxy={
        "enabled": True,
        "type": "residential",  # mobile, residential, isp, datacenter, custom
        "country": "US",  # optional: country code
        "state": "CA",    # optional: state code
        "city": "LA"      # optional: city name
    }
)
```

## API Reference

### Main Classes

#### `Grasp` / `AsyncGrasp`
Main client classes for interacting with the API.

**Methods:**
- `create(**options)`: Create a new container
- `connect(container_id)`: Connect to existing container

#### `GraspContainer` / `AsyncGraspContainer`
Represents a browser automation container.

**Properties:**
- `id`: Container identifier
- `status`: Current status (running, stopped, sleeping)
- `created_at`: Creation timestamp
- `browser`: Browser session information

**Methods:**
- `shutdown()`: Shut down the container

#### `BrowserSession`
Browser session information.

**Properties:**
- `ws_endpoint`: Chrome DevTools Protocol WebSocket endpoint
- `live_url`: Live view URL for observing the browser

### Exception Handling

```python
from grasp import (
    GraspError,
    AuthenticationError,
    NotFoundError,
    RateLimitError
)

try:
    container = client.create()
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
except GraspError as e:
    print(f"API error: {e}")
```

### Exception Hierarchy

- `GraspError`: Base exception
  - `APIError`: API-related errors
    - `APIStatusError`: HTTP status errors
      - `AuthenticationError`: 401 Unauthorized
      - `NotFoundError`: 404 Not Found
      - `RateLimitError`: 429 Rate Limited
      - `InternalServerError`: 500 Server Error
  - `APIConnectionError`: Network issues
    - `APITimeoutError`: Request timeout

## Examples

See the [examples](examples/) directory for more detailed examples:

- [basic_usage.py](examples/basic_usage.py): Simple synchronous usage
- [async_usage.py](examples/async_usage.py): Async with multiple containers
- [playwright_integration.py](examples/playwright_integration.py): Full Playwright integration

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/getgrasp-ai/grasp.git
cd grasp/packages/python-sdk

# Install dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=grasp

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0

## License

MIT
