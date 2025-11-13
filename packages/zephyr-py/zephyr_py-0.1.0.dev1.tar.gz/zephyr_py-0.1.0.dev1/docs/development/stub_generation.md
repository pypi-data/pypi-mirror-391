# Stub File Generation Guide

This guide explains how to generate and use Python stub files (`.pyi`) for the Zephyr framework and applications built with it.

## What are Stub Files?

Stub files (`.pyi`) are Python files that contain type information without implementation details. They provide:

- **Better IDE Support**: Enhanced autocomplete, navigation, and refactoring
- **Type Checking**: Improved static analysis with mypy
- **Documentation**: Clear API interfaces without implementation clutter
- **Distribution**: Share type information without source code

## Quick Start

### 1. Install Dependencies

```bash
# Install with stub generation tools
pip install -e ".[dev,stubs]"

# Or using make
make install-stubs
```

### 2. Generate Stub Files

```bash
# Generate all stub files
make stubs

# Or use the script directly
python scripts/generate_stubs.py
```

### 3. Use Generated Stubs

The stub files will be created in the `stubs/` directory:

```
stubs/
├── zephyr/                 # Zephyr framework stubs
│   ├── __init__.pyi
│   ├── app/
│   │   ├── application.pyi
│   │   ├── requests.pyi
│   │   └── responses.pyi
│   └── core/
└── taskflow_oidc/          # Example application stubs
    ├── app.pyi
    ├── config.pyi
    ├── auth/
    └── models/
```

## Generation Options

### Generate Specific Components

```bash
# Only Zephyr framework stubs
make stubs-zephyr
python scripts/generate_stubs.py --zephyr-only

# Only example applications
make stubs-examples  
python scripts/generate_stubs.py --examples-only

# Only TaskFlow OIDC example
make stubs-taskflow
python scripts/generate_stubs.py --taskflow-only
```

### Custom Output Directory

```bash
python scripts/generate_stubs.py --output-dir my-stubs/
```

### Clean Before Generation

```bash
python scripts/generate_stubs.py --clean
```

## IDE Configuration

### VS Code / Cursor

Add to your `settings.json`:

```json
{
    "python.analysis.extraPaths": ["./stubs"],
    "python.analysis.stubPath": "./stubs"
}
```

### PyCharm

1. Go to **File → Settings → Project → Python Interpreter**
2. Click the gear icon → **Show All**
3. Select your interpreter → **Show paths for the selected interpreter**
4. Add the `stubs/` directory

### Mypy Configuration

The `pyproject.toml` is already configured:

```toml
[tool.mypy]
mypy_path = "stubs"
namespace_packages = true
explicit_package_bases = true
```

## Using Stubs in Your Code

### Import from Stubs

```python
# Your application code can import from the original modules
from zephyr import Zephyr
from zephyr.app.requests import Request
from zephyr.app.responses import JSONResponse

# IDE and mypy will use the stub files for type checking
app = Zephyr()  # Type information from stubs/zephyr/__init__.pyi

@app.get("/")
async def hello(request: Request) -> JSONResponse:  # Types from stubs
    return JSONResponse({"message": "Hello World"})
```

### Type Checking

```bash
# Run mypy with stub support
mypy your_app.py

# Check stub files themselves
make check-stubs
```

## Example: TaskFlow OIDC Stubs

For the TaskFlow OIDC example, stubs are generated for:

### Core Application (`app.pyi`)

```python
from zephyr import Zephyr
from zephyr.app.responses import JSONResponse
from config import Settings

def create_app() -> Zephyr: ...
async def startup() -> None: ...

class DemoUserSwitchRequest:
    username: str
    def __init__(self, username: str = ...) -> None: ...

# Global app instance
app: Zephyr
```

### Configuration (`config.pyi`)

```python
from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseModel):
    url: str
    echo: bool
    def __init__(self, *, url: str = ..., echo: bool = ...) -> None: ...

class KeycloakConfig(BaseModel):
    server_url: str
    realm: str
    client_id: str
    client_secret: str
    
    @property
    def issuer_url(self) -> str: ...
    @property  
    def auth_url(self) -> str: ...
    # ... other properties

class Settings(BaseSettings):
    app_name: str
    debug: bool
    database: DatabaseConfig
    keycloak: KeycloakConfig
    # ... other fields

settings: Settings
```

### Authentication (`auth/*.pyi`)

```python
# auth/demo_auth.pyi
from typing import Optional, Dict, Any

class DemoAuthProvider:
    def __init__(self) -> None: ...
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]: ...
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]: ...
    # ... other methods

# auth/keycloak_auth.pyi  
class KeycloakAuthProvider:
    def __init__(self) -> None: ...
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]: ...
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]: ...
    # ... other methods
```

## Validation and Quality

### Check Generated Stubs

```bash
# Validate stub files
make check-stubs

# Run mypy on stubs
mypy stubs/ --ignore-missing-imports
```

### Common Issues

1. **Missing Dependencies**: Install type stubs for third-party packages
   ```bash
   pip install types-requests types-python-jose types-passlib
   ```

2. **Import Errors**: Ensure all modules are importable during generation

3. **Incomplete Stubs**: Some complex types may need manual refinement

## Advanced Usage

### Custom Stub Templates

You can create custom stub templates in `templates/stubs/`:

```python
# templates/stubs/custom_app.pyi.template
from typing import TypeVar, Generic
from zephyr import Zephyr

AppType = TypeVar('AppType', bound=Zephyr)

class CustomApp(Generic[AppType]):
    def __init__(self, app: AppType) -> None: ...
    # ... custom methods
```

### Integration with CI/CD

Add stub generation to your CI pipeline:

```yaml
# .github/workflows/stubs.yml
name: Generate Stubs
on: [push, pull_request]

jobs:
  stubs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e ".[dev,stubs]"
      - name: Generate stubs
        run: make stubs
      - name: Validate stubs
        run: make check-stubs
```

## Best Practices

1. **Regular Updates**: Regenerate stubs when code changes
2. **Version Control**: Consider committing stubs for team consistency
3. **Documentation**: Include stub usage in project documentation
4. **Testing**: Validate stubs with mypy in CI/CD
5. **Distribution**: Include stubs in package distributions

## Troubleshooting

### Common Errors

```bash
# Module not found during generation
python scripts/generate_stubs.py --search-path /path/to/modules

# Mypy errors in stubs
mypy stubs/ --ignore-missing-imports --no-strict-optional
```

### Getting Help

- Check the [mypy documentation](https://mypy.readthedocs.io/en/stable/stubs.html)
- Review generated stub files for accuracy
- Use `make check-stubs` to validate output

## Summary

Stub files provide excellent type safety and IDE support for Zephyr applications. The automated generation process makes it easy to maintain up-to-date type information without manual effort.

Key commands:
- `make stubs` - Generate all stub files
- `make check-stubs` - Validate generated stubs  
- `python scripts/generate_stubs.py --help` - See all options
