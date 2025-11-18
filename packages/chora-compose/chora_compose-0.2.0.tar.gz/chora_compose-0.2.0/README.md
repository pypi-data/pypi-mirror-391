# chora-compose

Content generation and orchestration capability server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **Note**: This package was renamed from `chora-mcp-compose` to `chora-compose` to follow the `chora-[capability]` naming convention.

## 🎯 What Is This?

**chora-compose** is a capability server that provides **workflow-oriented content generation and orchestration**. It offers intuitive workflow tools that match how agents think: "create this", "refresh stale content", "check status", "configure", "discover what's available".

**Core Value Proposition**: 88% tool call reduction, 74% token savings, and 60-85% time savings for template-based content generation workflows.

### Features

- **5 Workflow Tools**: create, refresh, inspect, configure, discover
- **Idempotent Operations**: Retry-safe with smart caching (fresh=cached, stale=regenerate)
- **Freshness Management**: Time-based policies with collection-level inheritance
- **4-Layer Architecture**: Tool interface → Orchestration → Core operations → Storage
- **Template-Based Generation**: LLM + Jinja2 for structured content creation
- **Batch Operations**: Generate 90+ artifacts in <10 minutes with parallel processing
- **Multi-Interface**: Native API, CLI, HTTP REST, and MCP server
- **Built with [FastMCP](https://github.com/jlowin/fastmcp)** - Anthropic's MCP framework
- **Production-Ready**: Comprehensive testing (85%+ coverage), CI/CD, quality gates

## Installation

### From PyPI (when published)

```bash
pip install chora-compose
```

### From Source

```bash
git clone https://github.com/liminalcommons/chora-compose
cd chora-compose
poetry install
```

## Quick Start

### Native Python API

```python
from chora_compose import Composer

composer = Composer()
result = await composer.create("my-artifact")
```

### CLI

```bash
chora-compose create my-artifact
chora-compose discover
chora-compose inspect my-artifact
```

### HTTP REST API

```bash
# Start server
uvicorn chora_compose.interfaces.http.server:app

# Use API
curl http://localhost:8000/api/v1/templates
curl -X POST http://localhost:8000/api/v1/artifacts?artifact_id=example
```

### MCP Server

Configure in your MCP client (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "chora-compose": {
      "command": "chora-compose"
    }
  }
}
```

## Documentation

- [Architecture](docs/architecture/)
- [How-To Guides](docs/user-docs/how-to/)
- [API Reference](docs/user-docs/reference/)
- [Contributing](docs/dev-docs/contributing.md)
- [Development Setup](docs/dev-docs/development-setup.md)

## Development

```bash
# Setup
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Lint & format
poetry run ruff check .
poetry run black .
```

## Migration from chora-mcp-compose

If you're migrating from `chora-mcp-compose` v0.1.0, see [CHANGELOG.md](CHANGELOG.md) for breaking changes and migration guide.

**Key Changes**:
- Package: `chora-mcp-compose` → `chora-compose`
- Module: `chora_mcp_compose` → `chora_compose`
- CLI: `chora-mcp-compose` → `chora-compose`

## License

MIT

## Links

- **Repository**: https://github.com/liminalcommons/chora-compose
- **Issues**: https://github.com/liminalcommons/chora-compose/issues
- **Documentation**: https://github.com/liminalcommons/chora-compose/blob/main/README.md
