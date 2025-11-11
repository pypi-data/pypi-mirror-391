# Testing the Grasp Python SDK

## Prerequisites

1. **API Server Running**: Ensure the Grasp API server is running locally on `http://localhost:3000`
   ```bash
   # From the root directory
   pnpm --filter api-server dev
   ```

2. **Python Environment**: Python 3.8+ installed

## Running Tests

```bash
cd packages/python-sdk
./run_tests.sh
```

The test script will automatically:
- Set environment variables (`GRASP_API_KEY="api-server-test"`, `GRASP_BASE_URL="http://localhost:3000"`)
- Install the SDK in development mode
- Install test dependencies (pytest, pytest-asyncio)
- Install Playwright for browser automation tests
- Run all tests including Playwright integration tests
- Show clear pass/fail status with troubleshooting tips

## Test Structure

- `tests/test_client.py` - Tests for synchronous client
- `tests/test_async_client.py` - Tests for asynchronous client

Each test file covers:
- Client initialization
- Container creation and management
- Browser endpoint validation
- Error handling
- Serialization
- **Playwright Integration** (optional):
  - Browser connection via CDP
  - Page navigation and content scraping

## Troubleshooting

### Connection Errors
If you see connection errors, ensure:
1. API server is running on port 3000
2. Environment variables are set correctly
3. No firewall blocking localhost connections

### API Key Errors
The test API key `api-server-test` is hardcoded for local testing. Make sure the API server recognizes this key.

### Cleanup
Tests automatically clean up containers after completion. If tests fail, some containers might remain active. Check the API server logs for orphaned containers.