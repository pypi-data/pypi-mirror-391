# PritunlClient Tests

Comprehensive test suite for the `PritunlClient` class.

## Running Tests

```bash
# Run all tests
pytest tests/test_client.py -v

# Run specific test class
pytest tests/test_client.py::TestLogin -v

# Run with coverage
pytest tests/test_client.py --cov=pritunl_webclient --cov-report=html
```

## Test Coverage

The test suite includes **36 tests** covering:

### 1. Client Initialization (`TestPritunlClientInit`)

- URL normalization (trailing slash removal)
- Default values initialization
- Client state setup

### 2. Login Functionality (`TestLogin`)

- Successful login with credential storage
- Failed login with incorrect credentials
- Network error handling
- CSRF token fetching

### 3. Authentication Enforcement (`TestEnsureAuth`)

- Session validation
- Auto-login when credentials are available
- Error when no credentials provided

### 4. State Management (`TestState`)

- Successful state retrieval
- CSRF token updates
- Error handling

### 5. Server Listing (`TestListServers`)

- Successful server listing
- Pagination support
- Error handling
- Authentication requirement

### 6. Server Start Operations (`TestStartServer`)

- Starting with provided server object
- Starting without server object (auto-fetch)
- Server not found errors
- Operation failures

### 7. Server Stop Operations (`TestStopServer`)

- Stopping with provided server object
- Stopping without server object (auto-fetch)
- Operation failures

### 8. Server Status Checks (`TestCheckServerStatus`)

- Successful status retrieval
- Error handling
- Authentication requirement

### 9. Header Management (`TestGetHeaders`)

- Basic header generation
- CSRF token inclusion
- Custom headers
- Header merging

### 10. Server Object Finding (`TestFindServerObj`)

- Finding servers by ID
- Handling missing servers
- Empty server lists

### 11. Decorator Integration (`TestDecoratorIntegration`)

- Authentication decorator allows authenticated calls
- Authentication decorator blocks unauthenticated calls
- Auto-authentication through decorator

### 12. Client Lifecycle (`TestClose`)

- Proper client cleanup

## Test Fixtures

### `base_url`

Base URL for testing (`https://pritunl.example.com`)

### `client`

Unauthenticated `PritunlClient` instance with auto-cleanup

### `authenticated_client`

Pre-authenticated `PritunlClient` instance with:

- Username: `testuser`
- Password: `testpass`
- Session cookie set
- CSRF token: `test-csrf-token`

## Mocking

Tests use `respx` to mock HTTP requests:

- All external HTTP calls are mocked
- No real network requests are made
- Fast and reliable test execution

## Key Features Tested

✅ **Decorator Pattern**: `@require_auth` decorator correctly enforces authentication
✅ **Auto-Reconnection**: Client automatically re-authenticates when session expires
✅ **Error Handling**: Proper exception raising for various failure scenarios
✅ **HTTP Mocking**: All HTTP interactions are mocked with `respx`
✅ **Type Safety**: Return types match function signatures
✅ **Session Management**: Cookie and CSRF token handling

## Dependencies

- `pytest>=7.0.0` - Test framework
- `respx>=0.20.0` - HTTP mocking for httpx
- `httpx>=0.24.0` - HTTP client (production dependency)
