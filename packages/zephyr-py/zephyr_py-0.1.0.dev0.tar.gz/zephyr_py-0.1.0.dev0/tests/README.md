# Zephyr Authentication System Tests

Comprehensive test suite for the Zephyr authentication system, covering all implemented phases and components.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and shared fixtures
├── run_tests.py               # Test runner script
├── README.md                  # This file
└── security/                  # Security module tests
    ├── __init__.py
    ├── test_jwt.py            # JWT functionality tests
    ├── test_password.py       # Password hashing tests
    ├── test_tokens.py         # Token management tests
    ├── test_user.py           # User model tests
    ├── test_backends.py       # Authentication backend tests
    ├── test_middleware.py     # Bearer auth middleware tests
    └── test_integration.py    # Integration tests
```

## Test Categories

### Unit Tests
- **JWT Tests** (`test_jwt.py`): Token creation, validation, refresh, error handling
- **Password Tests** (`test_password.py`): Hashing, verification, security features
- **Token Tests** (`test_tokens.py`): Blacklisting, revocation, cleanup
- **User Tests** (`test_user.py`): User models, roles, permissions
- **Backend Tests** (`test_backends.py`): Authentication backends
- **Middleware Tests** (`test_middleware.py`): Bearer auth middleware

### Integration Tests
- **Authentication Flow** (`test_integration.py`): Complete auth flows
- **Token Lifecycle**: Creation, validation, refresh, revocation
- **Password Security**: Hashing, verification, constant-time comparison
- **User Management**: Roles, permissions, authentication state
- **Middleware Integration**: ASGI integration, scope handling

## Running Tests

### Quick Start
```bash
# Run all tests
python tests/run_tests.py

# Run with coverage
python tests/run_tests.py --coverage

# Run specific category
python tests/run_tests.py unit
python tests/run_tests.py integration
python tests/run_tests.py security
```

### Test Categories
```bash
# Unit tests only
python tests/run_tests.py unit

# Integration tests only  
python tests/run_tests.py integration

# Security tests only
python tests/run_tests.py security

# Fast tests (exclude slow tests)
python tests/run_tests.py fast
```

### Advanced Options
```bash
# Verbose output
python tests/run_tests.py --verbose

# Parallel execution
python tests/run_tests.py --parallel

# Specific test pattern
python tests/run_tests.py --pattern "test_jwt"

# Specific markers
python tests/run_tests.py --markers "jwt and not slow"

# List all tests
python tests/run_tests.py --list-tests
```

### Direct Pytest Usage
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/security/test_jwt.py

# Run with coverage
pytest --cov=zephyr --cov-report=html

# Run in parallel
pytest -n auto

# Run specific markers
pytest -m "jwt and not slow"
```

## Test Markers

Tests are automatically marked based on their location and content:

- `unit`: Unit tests (in test_*.py files)
- `integration`: Integration tests (test_integration.py)
- `security`: Security-related tests (in security/ directory)
- `auth`: Authentication-related tests
- `jwt`: JWT-related tests
- `password`: Password-related tests
- `token`: Token-related tests
- `user`: User-related tests
- `backend`: Backend-related tests
- `middleware`: Middleware-related tests
- `slow`: Slow tests (can be excluded with `-m "not slow"`)

## Test Coverage

The test suite provides comprehensive coverage of:

### Phase 2.1: JWT Foundation ✅
- JWT configuration and payload models
- Token creation, validation, and refresh
- Error handling and edge cases
- Security features and best practices

### Phase 2.2: Bearer Authentication ✅
- User and AnonymousUser models
- Authentication backends (JWT, Token, NoAuth)
- Bearer authentication middleware
- ASGI integration and scope handling

### Future Phases (Planned)
- OAuth2 flows and server implementation
- SSO providers (Google, GitHub, Azure, SAML)
- Keycloak integration
- WebAuthn passwordless authentication
- MFA (TOTP, SMS, Email)
- LDAP/AD federation
- RBAC with ABAC policies
- UMA resource management
- Session management

## Test Data and Fixtures

### Shared Fixtures (`conftest.py`)
- `jwt_config`: JWT configuration for tests
- `jwt_manager`: JWT manager instance
- `blacklist`: Token blacklist instance
- `token_manager`: Token manager instance
- `password_hasher`: Password hasher instance
- `auth_backend`: JWT authentication backend
- `test_user`: Standard test user
- `superuser`: Superuser for testing
- `anonymous_user`: Anonymous user
- `http_scope`: HTTP ASGI scope
- `websocket_scope`: WebSocket ASGI scope

### Sample Data
- `sample_tokens`: Various token types for testing
- `sample_passwords`: Different password scenarios
- `sample_users`: Different user types
- `sample_roles`: Role definitions
- `sample_permissions`: Permission definitions

## Security Testing

The test suite includes comprehensive security testing:

### Password Security
- Constant-time comparison verification
- Password length validation and truncation
- Hash algorithm verification
- Salt generation and uniqueness

### JWT Security
- Token signature verification
- Expiration handling
- Token type validation
- Error handling without information leakage

### Token Management
- Blacklist functionality
- Revocation verification
- Cleanup of expired tokens
- Concurrent access handling

### Authentication Flow
- Token extraction and validation
- User authentication and authorization
- Middleware security and error handling
- Scope preservation and data integrity

## Performance Testing

Tests include performance considerations:

- Concurrent authentication requests
- Token creation and validation performance
- Password hashing performance
- Middleware overhead measurement
- Memory usage and cleanup

## Error Handling

Comprehensive error handling tests:

- Invalid input handling
- Network and I/O errors
- Authentication failures
- Token validation errors
- Middleware error propagation

## Continuous Integration

The test suite is designed for CI/CD:

- Fast execution for unit tests
- Comprehensive integration tests
- Coverage reporting
- Parallel execution support
- Clear test categorization
- Detailed error reporting

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use appropriate markers
3. Include both positive and negative test cases
4. Test edge cases and error conditions
5. Add integration tests for new features
6. Update this documentation

## Test Dependencies

The test suite requires:

- `pytest>=7.0.0`: Test framework
- `pytest-asyncio>=0.18.0`: Async test support
- `pytest-cov>=4.0.0`: Coverage reporting
- `pytest-xdist>=3.0.0`: Parallel execution
- `pytest-mock>=3.10.0`: Mocking support

Install with:
```bash
pip install -e ".[dev]"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root
2. **Async Issues**: Use `pytest-asyncio` and proper async fixtures
3. **Mock Issues**: Use `pytest-mock` for better mocking support
4. **Coverage Issues**: Check that source paths are correct

### Debug Mode

Run tests in debug mode:
```bash
pytest --pdb --pdbcls=IPython.terminal.debugger:Pdb
```

### Verbose Output

Get detailed test output:
```bash
pytest -v -s
```

## Test Results

Expected test results for Phase 2.1 and 2.2:

- **Total Tests**: ~150+ tests
- **Coverage**: >95% for implemented components
- **Execution Time**: <30 seconds for unit tests
- **Integration Tests**: <2 minutes for full suite

## Future Enhancements

Planned test improvements:

1. **Load Testing**: High-concurrency authentication tests
2. **Security Testing**: Penetration testing scenarios
3. **Performance Benchmarks**: Detailed performance metrics
4. **Visual Testing**: Test result visualization
5. **Automated Security Scanning**: SAST/DAST integration
