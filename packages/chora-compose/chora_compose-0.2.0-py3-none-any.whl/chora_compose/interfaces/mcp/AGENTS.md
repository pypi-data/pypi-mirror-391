# Agent Awareness: Source Code Guidelines

**Domain**: Source code implementation and patterns
**Parent**: See [/AGENTS.md](/AGENTS.md) for general guidance

## Project Structure

```
src/chora_mcp_template/
├── __init__.py          # Package initialization, version
├── server.py            # Main MCP server implementation
├── mcp/
│   ├── __init__.py      # Naming conventions, validation
│   └── AGENTS.md        # MCP-specific guidance
└── py.typed             # PEP 561 type marker
```

## Code Style & Standards

### Type Hints (Required)

All functions must have type hints:

```python
# ✅ Correct
async def my_function(param: str, count: int = 1) -> dict[str, Any]:
    return {"result": param * count}

# ❌ Wrong
async def my_function(param, count=1):
    return {"result": param * count}
```

### Python Version

- **Minimum**: Python 3.11
- **Use modern syntax**: `dict[str, Any]` not `Dict[str, Any]`
- **Union types**: `str | None` not `Optional[str]`

### Imports

Organize imports in this order:

```python
# 1. Standard library
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# 2. Third-party packages
from fastmcp import FastMCP
from pydantic import BaseModel

# 3. Local imports
from chora_mcp_template.mcp import NAMESPACE, make_tool_name
```

**Run isort**: `ruff check --select I --fix`

### Async/Await

All MCP tools and resources must be async:

```python
# ✅ Correct
@mcp.tool()
async def my_tool(param: str) -> dict:
    result = await async_operation()
    return {"result": result}

# ❌ Wrong
@mcp.tool()
def my_tool(param: str) -> dict:  # Missing async
    return {"result": param}
```

## FastMCP Patterns

### Tool Definition

```python
from fastmcp import FastMCP

mcp = FastMCP("chora-mcp-template")

@mcp.tool()
async def example_tool(
    param: str,
    optional: bool = False
) -> dict[str, Any]:
    """Clear description for LLM consumption.

    Args:
        param: Description of required parameter
        optional: Description of optional parameter

    Returns:
        Dictionary with result data
    """
    # Validate inputs
    if not param:
        raise ValueError("param cannot be empty")

    # Process
    result = await process_data(param)

    # Return structured data
    return {
        "status": "success",
        "result": result,
        "metadata": {"optional": optional}
    }
```

### Resource Definition

```python
@mcp.resource("choramcp://config/server")
async def get_config() -> dict[str, Any]:
    """Get server configuration.

    Returns:
        Configuration dictionary
    """
    return {
        "name": "chora-mcp-template",
        "version": __version__,
        "namespace": NAMESPACE
    }
```

### Using Naming Conventions

```python
from chora_mcp_template.mcp import make_tool_name, make_resource_uri

# Tool names
@mcp.tool(name=make_tool_name("my_tool"))
async def my_tool():
    pass

# Resource URIs
@mcp.resource(make_resource_uri("config", "server"))
async def config():
    pass
```

## Validation Patterns

### Input Validation

Always validate inputs early:

```python
@mcp.tool()
async def process_data(
    data: str,
    count: int = 1
) -> dict:
    # Validate strings
    if not data:
        raise ValueError("data parameter cannot be empty")

    if not data.strip():
        raise ValueError("data cannot be only whitespace")

    # Validate numbers
    if count < 0:
        raise ValueError("count must be non-negative")

    if count > 1000:
        raise ValueError("count too large (max: 1000)")

    # Process after validation
    result = data * count
    return {"result": result}
```

### Error Messages

Use curly braces for f-strings, escape for validation messages:

```python
# ✅ Correct: f-string
message = f"Processing {item_count} items"

# ✅ Correct: Validation message with escaped braces
raise ValueError(
    f"Invalid namespace: {namespace}. "
    f"Must match pattern: [a-z][a-z0-9]{{2,19}}"
)

# ❌ Wrong: Unescaped braces in f-string
raise ValueError(f"Pattern {0,19} failed")  # KeyError!
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
async def example_function(param: str, count: int) -> dict:
    """Brief one-line description.

    Longer description with more details about what
    this function does and why it exists.

    Args:
        param: Description of parameter
        count: Number of times to process

    Returns:
        Dictionary containing:
            - result: Processed data
            - count: Number of iterations

    Raises:
        ValueError: If param is empty or count is negative
    """
    pass
```

### Comments

Comment the "why", not the "what":

```python
# ✅ Good: Explains why
# Use cache to avoid expensive API calls on repeated access
if key in cache:
    return cache[key]

# ❌ Bad: States the obvious
# Check if key is in cache
if key in cache:
    return cache[key]
```

## Testing Your Code

Every new function needs tests:

```python
# tests/test_server.py
import pytest
from chora_mcp_template.server import my_tool

@pytest.mark.asyncio
async def test_my_tool():
    result = await my_tool.fn(param="test")
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_my_tool_validation():
    with pytest.raises(ValueError, match="cannot be empty"):
        await my_tool.fn(param="")
```

Run tests:
```bash
pytest
pytest --cov=src/chora_mcp_template
```

## Common Patterns

### Returning Structured Data

Return dictionaries with consistent structure:

```python
# ✅ Good: Consistent structure
return {
    "status": "success",
    "data": result,
    "metadata": {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }
}

# ⚠️ Acceptable: Simple return
return {"result": value}

# ❌ Avoid: Inconsistent structure
if success:
    return {"data": value}
else:
    return {"error": message}  # Different keys!
```

### Error Handling

Raise exceptions for validation, return errors for processing:

```python
@mcp.tool()
async def safe_operation(data: dict) -> dict:
    # Validation errors: raise
    if not data:
        raise ValueError("data cannot be empty")

    # Processing errors: return structured error
    try:
        result = await risky_operation(data)
        return {"success": True, "result": result}

    except Exception as e:
        return {
            "success": False,
            "error": type(e).__name__,
            "message": str(e)
        }
```

### Configuration

Load config at module level:

```python
# At top of server.py
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config"

# Use in functions
@mcp.tool()
async def load_config(name: str) -> dict:
    config_file = CONFIG_PATH / f"{name}.json"
    if not config_file.exists():
        raise FileNotFoundError(f"Config not found: {name}")

    return json.loads(config_file.read_text())
```

## Linting & Formatting

Before committing:

```bash
# Auto-format code
ruff format .

# Fix auto-fixable issues
ruff check --fix .

# Check remaining issues
ruff check .

# Type checking
mypy src/chora_mcp_template
```

Or use the shortcut:
```bash
just pre-merge
```

## Performance

### Async Best Practices

```python
# ✅ Good: Concurrent operations
results = await asyncio.gather(
    fetch_data_1(),
    fetch_data_2(),
    fetch_data_3()
)

# ❌ Bad: Sequential operations
result1 = await fetch_data_1()
result2 = await fetch_data_2()
result3 = await fetch_data_3()
```

### Caching

```python
from functools import lru_cache

# Simple caching for expensive computations
@lru_cache(maxsize=128)
def expensive_computation(param: str) -> dict:
    # Expensive work here
    return result
```

## Security

### Input Sanitization

```python
# Sanitize file paths
from pathlib import Path

def safe_read_file(filename: str) -> str:
    # Prevent directory traversal
    safe_path = Path(filename).resolve()
    base_path = Path("/allowed/directory").resolve()

    if not safe_path.is_relative_to(base_path):
        raise ValueError("Access denied")

    return safe_path.read_text()
```

### Environment Variables

```python
import os
from pathlib import Path

# ✅ Good: Default values, validation
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")

# ✅ Good: .env file support
from dotenv import load_dotenv
load_dotenv()
```

## See Also

- [Root AGENTS.md](/AGENTS.md) - General guidance
- [MCP Conventions](/src/chora_mcp_template/mcp/AGENTS.md) - Naming patterns
- [Testing Guide](/tests/AGENTS.md) - How to test
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [SAP-014 MCP Development](/docs/mcp-patterns/README.md)
