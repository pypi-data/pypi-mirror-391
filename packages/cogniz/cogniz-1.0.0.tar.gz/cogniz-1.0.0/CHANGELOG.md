# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-13

### Added
- Initial release of Cogniz Python SDK
- Synchronous `Client` class for memory operations
- Asynchronous `AsyncClient` class for concurrent operations
- Core memory operations: store, search, get_all, update, delete, delete_all
- Project management: list_projects
- Cogniz features: optimize_prompt, run_playbook, list_playbooks
- Knowledge graph operations: extract_entities, get_graph_stats
- Usage statistics: get_stats, get_debug_settings
- Configuration via `Config` class
- Environment variable support (COGNIZ_API_KEY, COGNIZ_BASE_URL, COGNIZ_PROJECT_ID)
- Comprehensive error handling with custom exceptions
- Context manager support for both sync and async clients
- Type hints throughout the codebase
- Full test suite with pytest
- Documentation and examples
- PyPI packaging configuration

### Features
- 🧠 Persistent memory storage
- 🔍 Semantic search capabilities
- 🎯 Confidence scoring
- ⏰ Auto-expiration support
- 🤖 Agent memory scoping
- ⚡ Native async/await support
- 🎨 Prompt optimization
- 📊 Automation playbooks
- 🌐 Multi-client compatibility (Browser Extension, VS Code, MCP)

[1.0.0]: https://github.com/cogniz-ai/cogniz-python/releases/tag/v1.0.0
