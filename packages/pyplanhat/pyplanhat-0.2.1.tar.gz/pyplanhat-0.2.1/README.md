# PyPlanhat SDK

Modern async-first Python SDK for the Planhat API.

## Features

- 🚀 **Async-first architecture** with auto-generated sync support
- 📦 **Built with modern Python tooling** (httpx, pydantic, uv)
- 🔒 **Type-safe** with full mypy support
- ✨ **Comprehensive error handling** with custom exception hierarchy
- 🧪 **Extensively tested** with 97% coverage
- 📚 **Complete resource coverage** - Companies, EndUsers, Conversations
- 🎨 **Fully extensible models** - Subclass and add your own typed fields

## Installation

```bash
pip install pyplanhat
```

## Quick Start

### Async Usage (Recommended)

```python
import asyncio
from pyplanhat import AsyncPyPlanhat, Company

async def main():
    async with AsyncPyPlanhat(api_key="your-api-key") as client:
        # List all companies
        companies = await client.companies.list()

        # Get a specific company
        company = await client.companies.get("company-id")

        # Create a new company
        new_company = Company(
            name="Acme Corporation",
            status="prospect",
            custom={"industry": "Technology"}
        )
        created = await client.companies.create(new_company)

        # Work with end users
        users = await client.endusers.list(company_id=company.id)

        # Work with conversations
        conversations = await client.conversations.list(company_id=company.id)

asyncio.run(main())
```

### Sync Usage

```python
from pyplanhat import PyPlanhat, Company

with PyPlanhat(api_key="your-api-key") as client:
    # All the same methods work synchronously
    companies = client.companies.list()
    company = client.companies.get("company-id")
```

For detailed examples and advanced usage, see [USAGE.md](USAGE.md).

## Configuration

Set environment variables for convenient testing:

```bash
export PLANHAT_API_KEY="your-api-key"
export PLANHAT_API_BASE_URL="https://api.planhat.com"  # optional
```

Or pass directly to the client:

```python
client = AsyncPyPlanhat(
    api_key="your-api-key",
    base_url="https://api.planhat.com"
)
```

## Resources

PyPlanhat provides complete CRUD operations for the following Planhat resources:

- **Companies** - Manage customer companies with full lifecycle tracking
- **EndUsers** - Manage contacts and end users within companies
- **Conversations** - Track interactions, meetings, and communications

Each resource supports:
- `list()` - Get all resources (with optional filtering)
- `get(id)` - Get a specific resource by ID
- `create(resource)` - Create a new resource
- `update(id, resource)` - Update an existing resource
- `delete(id)` - Delete a resource

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/ddlaws0n/pyplanhat.git
cd pyplanhat

# Install dependencies
uv sync --all-groups

# Run tests
uv run pytest -v

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

### Architecture

PyPlanhat uses an **async-first DRY architecture**:

1. ✏️ Write async code in `src/pyplanhat/_async/`
2. 🔄 Generate sync code: `python scripts/generate_sync.py`
3. ✅ Both versions tested identically
4. 📦 Zero duplication of business logic

The synchronous version is automatically generated from the async source using `unasync`, ensuring perfect parity between both APIs.

### Development Guidelines

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines and workflow.

Key principles:
- **Never edit** files in `_sync/` directories (they're auto-generated)
- **Always run** `python scripts/generate_sync.py` after modifying async code
- **Maintain test parity** between async and sync test suites
- **Follow the phased plan** in `docs/pyplanhat/PLAN.md`

### Project Structure

```
src/pyplanhat/
├── _async/              # Async source code (write here)
│   ├── client.py        # Main async client
│   └── resources/       # Async resource implementations
├── _sync/               # Generated sync code (never edit)
│   ├── client.py        # Generated sync client
│   └── resources/       # Generated sync resources
├── _exceptions.py       # Custom exception hierarchy
└── __init__.py         # Public API exports

tests/
├── _async/             # Async tests (write here)
└── _sync/              # Generated sync tests (never edit)
```

## Roadmap

- **Phase 0**: Foundation (exception hierarchy, client shell, code generation) ✅ **Complete**
- **Phase 1**: Companies resource implementation ✅ **Complete**
- **Phase 2**: EndUsers and Conversations resources ✅ **Complete**
- **Phase 3**: Documentation (mkdocs, API reference) 🚧 **In Progress**
- **Phase 4**: Release to PyPI ✅ **Complete** (v0.1.0 published)

## Contributing

This project follows strict architectural patterns and phased development. Please review:

1. [CLAUDE.md](CLAUDE.md) - Development workflow and commands
2. [docs/pyplanhat/PLAN.md](docs/pyplanhat/PLAN.md) - Phased development plan
3. [docs/pyplanhat/ARCHITECTURE.md](docs/pyplanhat/ARCHITECTURE.md) - Architecture details

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.
