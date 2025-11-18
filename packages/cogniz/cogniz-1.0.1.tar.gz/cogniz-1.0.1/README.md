# Cogniz Python SDK

[![PyPI version](https://badge.fury.io/py/cogniz.svg)](https://pypi.org/project/cogniz/)
[![Python versions](https://img.shields.io/pypi/pyversions/cogniz.svg)](https://pypi.org/project/cogniz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for Cogniz Memory Platform. Build AI applications with persistent, searchable memory.

## Features

- **Persistent Memory** - Store and recall information across sessions
- **Semantic Search** - Natural language memory retrieval
- **Confidence Scoring** - Filter memories by reliability
- **Auto-Expiration** - Automatic cleanup of stale data
- **Agent Scoping** - Separate AI personality from user data
- **Async Support** - Native asyncio for concurrent operations
- **Prompt Optimizer** - AI-powered prompt enhancement
- **Playbooks** - Automation workflows
- **Self-Hosted** - Run on your own infrastructure
- **Multi-Client** - Works with Browser Extension, VS Code, MCP

## Installation

```bash
pip install cogniz
```

## Quick Start

```python
from cogniz import Client

# Initialize client
client = Client(api_key="mp_your_api_key_here")

# Store a memory
client.store(
    "User prefers Python for backend development",
    user_id="alice",
    category="preferences"
)

# Search memories
results = client.search("programming languages", user_id="alice")
for memory in results.get("results", []):
    print(f"- {memory['content']}")

# Get usage stats
stats = client.get_stats()
print(f"Plan: {stats['plan']}, Memories: {stats['total_memories']}")
```

## Environment Variables

Set these in your `.env` file:

```bash
COGNIZ_API_KEY=mp_your_api_key_here
COGNIZ_PROJECT_ID=123  # Optional default project
COGNIZ_BASE_URL=https://cogniz.online  # Optional custom host
```

Then use without parameters:

```python
from cogniz import Client

# Automatically reads from environment
client = Client()
```

## Core Operations

### Store Memories

```python
# Simple storage
result = client.store(
    "User completed Python course",
    user_id="alice"
)

# With metadata and category
result = client.store(
    "User allergic to penicillin",
    user_id="patient_123",
    category="medical",
    metadata={"severity": "high", "verified": True},
    confidence=1.0
)

# With expiration
result = client.store(
    "User browsing electronics section",
    user_id="bob",
    category="session",
    auto_expire=True  # Expires based on category
)
```

### Search Memories

```python
# Basic search
results = client.search(
    "What programming languages does the user know?",
    user_id="alice"
)

# With filtering
results = client.search(
    "medical conditions",
    user_id="patient_123",
    threshold=0.8,  # High confidence only
    limit=5
)

# With agent context
results = client.search(
    "fitness goals",
    user_id="alice",
    agent_id="fitness_coach_v1"
)
```

### Manage Memories

```python
# Get all memories
memories = client.get_all(user_id="alice", limit=50)

# Update memory
client.update(
    memory_id="mem_123",
    content="Updated information",
    metadata={"verified": True}
)

# Delete memory
client.delete("mem_123")

# Delete all for user
client.delete_all(user_id="alice")
```

## Advanced Features

### Agent Memory Scoping

Store AI personality once, share across all users:

```python
# Store agent personality (shared)
client.store(
    "You are a motivational fitness coach who celebrates wins",
    agent_id="fitness_coach_v1"
)

# Store user progress (private)
client.store(
    "User completed 5K run in 28 minutes",
    user_id="alice"
)

# Search combines both contexts
results = client.search(
    "my running progress",
    user_id="alice",
    agent_id="fitness_coach_v1"
)
```

### Prompt Optimization

```python
# Optimize your prompts with AI
result = client.optimize_prompt(
    "Write code to sort a list",
    preset="technical"  # or "comprehensive", "concise"
)

print(result["optimized"])
# Output: "Write production-ready, well-commented Python code..."
```

### Automation Playbooks

```python
# List available playbooks
playbooks = client.list_playbooks()

# Run a playbook
result = client.run_playbook(
    "web_scraper_v1",
    input_data={"url": "https://example.com"}
)
```

### Knowledge Graph

```python
# Extract entities from text
entities = client.extract_entities(
    "Emma works with David at Cogniz on the Python SDK"
)

# Get graph statistics
stats = client.get_graph_stats()
print(f"Entities: {stats['entity_count']}")
```

## Async Usage

```python
import asyncio
from cogniz import AsyncClient

async def main():
    async with AsyncClient(api_key="mp_...") as client:
        # Store memory
        await client.store(
            "User loves async Python",
            user_id="alice"
        )

        # Search memories
        results = await client.search(
            "async programming",
            user_id="alice"
        )

        print(results)

asyncio.run(main())
```

## Project Management

```python
# List all projects
projects = client.list_projects()
for project in projects:
    print(f"{project['id']}: {project['name']}")

# Use specific project
client = Client(api_key="mp_...", project_id=456)
```

## Error Handling

```python
from cogniz import (
    Client,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    QuotaExceededError
)

client = Client(api_key="mp_...")

try:
    result = client.store("User data", user_id="alice")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except QuotaExceededError:
    print("Storage quota exceeded, upgrade plan")
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## Context Manager

```python
# Automatically closes HTTP connections
with Client(api_key="mp_...") as client:
    client.store("User data", user_id="alice")
    results = client.search("query", user_id="alice")
# Connection closed automatically
```

## Compatibility

Works seamlessly with:

- **Cogniz Browser Extension** - Chrome/Firefox extension for web memory
- **Cogniz VS Code Extension** - IDE integration
- **Cogniz MCP Server** - Claude Desktop integration
- **Self-Hosted Platform** - Your own WordPress installation

All clients use the same API, so memories are synced across all surfaces.

## API Reference

### `Client(api_key, base_url, project_id, config, client)`

Main synchronous client.

**Core Methods:**
- `store(content, **kwargs)` - Store a memory
- `search(query, **kwargs)` - Search memories
- `get_all(**kwargs)` - Get all memories
- `update(memory_id, **kwargs)` - Update memory
- `delete(memory_id)` - Delete memory
- `delete_all(**kwargs)` - Bulk delete

**Project Methods:**
- `list_projects()` - List all projects

**Cogniz Features:**
- `optimize_prompt(prompt, **kwargs)` - Optimize prompts
- `run_playbook(playbook_id, input_data, **kwargs)` - Run automation
- `list_playbooks(**kwargs)` - List playbooks
- `get_stats()` - Get usage statistics
- `get_debug_settings()` - Get platform info

**Knowledge Graph:**
- `extract_entities(text, **kwargs)` - Extract entities
- `get_graph_stats(**kwargs)` - Get graph statistics

### `AsyncClient`

Async version with same API using `async`/`await`.

### `Config(api_key, base_url, project_id, timeout)`

Configuration object.

## Get API Key

1. Sign up at [cogniz.online](https://cogniz.online)
2. Go to Dashboard → API Keys
3. Create new API key
4. Copy key (starts with `mp_`)

## Documentation

- [Full Documentation](https://docs.cogniz.online)
- [API Reference](https://docs.cogniz.online/api-reference)
- [Examples](https://github.com/cogniz-ai/cogniz-python/tree/main/examples)
- [WordPress Plugin](https://github.com/cogniz-ai/cogniz-wordpress)

## Support

- Email: support@cogniz.online
- Discord: [Join community](https://discord.gg/cogniz)
- Issues: [GitHub Issues](https://github.com/cogniz-ai/cogniz-python/issues)
- Documentation: [docs.cogniz.online](https://docs.cogniz.online)

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built by the Cogniz team. Powered by WordPress and httpx.
