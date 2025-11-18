"""
Cogniz Memory Client - Main SDK implementation.

Maps to WordPress REST API endpoints at /wp-json/memory/v1/*
"""

import httpx
from typing import Dict, List, Any, Optional, Union
import logging

from cogniz.config import Config
from cogniz.errors import (
    CognizError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
    NetworkError,
    QuotaExceededError
)

logger = logging.getLogger(__name__)


class Client:
    """
    Cogniz Memory Platform Client.

    Provides synchronous API access to store, search, and manage memories.

    Args:
        api_key: Your Cogniz API key
        base_url: Platform URL (default: https://cogniz.online)
        project_id: Default project ID
        config: Pre-configured Config object
        client: Custom httpx.Client

    Example:
        >>> from cogniz import Client
        >>> client = Client(api_key="mp_...")
        >>> client.store("User loves Python", user_id="alice")
        >>> results = client.search("programming", user_id="alice")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        project_id: Optional[str] = None,
        config: Optional[Config] = None,
        client: Optional[httpx.Client] = None
    ):
        if config:
            self.config = config
        else:
            self.config = Config(
                api_key=api_key,
                base_url=base_url,
                project_id=project_id
            )

        if client:
            self.http = client
        else:
            self.http = httpx.Client(
                headers=self.config.get_headers(),
                timeout=self.config.timeout,
                follow_redirects=True
            )

    def _handle_response(self, response: httpx.Response) -> Any:
        """Process HTTP response and handle errors."""
        try:
            # Handle error status codes
            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError(
                    "Invalid API key or insufficient permissions",
                    status_code=response.status_code
                )
            elif response.status_code == 404:
                raise NotFoundError(
                    "Resource not found",
                    status_code=404
                )
            elif response.status_code == 429:
                raise RateLimitError(
                    "Rate limit exceeded - please wait before retrying",
                    status_code=429
                )
            elif response.status_code == 413:
                raise QuotaExceededError(
                    "Storage or memory quota exceeded",
                    status_code=413
                )
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code
                )
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get("message", response.text)
                except:
                    message = response.text
                raise CognizError(
                    f"API error: {message}",
                    status_code=response.status_code
                )

            response.raise_for_status()

            # Parse JSON response
            return response.json()

        except httpx.TimeoutException:
            raise NetworkError("Request timeout")
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {str(e)}")
        except httpx.HTTPError as e:
            if not isinstance(e, (httpx.TimeoutException, httpx.ConnectError)):
                raise CognizError(f"HTTP error: {str(e)}")
            raise

    def _prepare_payload(self, **kwargs) -> Dict[str, Any]:
        """Prepare request payload with project_id."""
        payload = dict(kwargs)

        # Add project_id from config if not explicitly set
        if (payload.get("project_id") is None) and self.config.project_id:
            payload["project_id"] = self.config.project_id

        return {k: v for k, v in payload.items() if v is not None}

    # Core Memory Operations

    def store(
        self,
        content: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
        expiration_date: Optional[str] = None,
        auto_expire: bool = False,
        infer: bool = True
    ) -> Dict[str, Any]:
        """
        Store a memory.

        Args:
            content: Memory content/text
            user_id: User identifier
            agent_id: Agent identifier
            project_id: Project ID (uses default if not specified)
            category: Memory category
            metadata: Additional data
            confidence: Confidence score 0.0-1.0
            expiration_date: ISO datetime for expiration
            auto_expire: Use category-based expiration
            infer: Enable LLM processing

        Returns:
            Response with memory_id and success status

        Example:
            >>> result = client.store(
            ...     "User prefers dark mode",
            ...     user_id="alice",
            ...     category="preferences"
            ... )
            >>> print(result["memory_id"])
        """
        if not content:
            raise ValidationError("Content is required")

        payload = self._prepare_payload(
            content=content,
            user_id=user_id,
            agent_id=agent_id,
            project_id=project_id,
            category=category,
            metadata=metadata,
            confidence=confidence,
            expiration_date=expiration_date,
            auto_expire=auto_expire,
            infer=infer
        )

        response = self.http.post(
            f"{self.config.api_endpoint}/store",
            json=payload
        )

        return self._handle_response(response)

    def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        threshold: float = 0.6,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search memories using natural language.

        Args:
            query: Search query text
            user_id: Filter by user
            agent_id: Include agent memories
            project_id: Project ID
            limit: Maximum results
            offset: Pagination offset
            threshold: Minimum confidence score
            filters: Additional filters

        Returns:
            Dictionary with results list

        Example:
            >>> results = client.search(
            ...     "programming languages",
            ...     user_id="alice",
            ...     threshold=0.7
            ... )
            >>> for mem in results.get("results", []):
            ...     print(mem["content"])
        """
        if not query:
            raise ValidationError("Query is required")

        params = self._prepare_payload(
            query=query,
            user_id=user_id,
            agent_id=agent_id,
            project_id=project_id,
            limit=limit,
            offset=offset,
            threshold=threshold
        )

        if filters:
            params["filters"] = filters

        response = self.http.get(
            f"{self.config.api_endpoint}/search",
            params=params
        )

        return self._handle_response(response)

    def get_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all memories with optional filtering.

        Args:
            user_id: Filter by user
            agent_id: Filter by agent
            project_id: Project ID
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Dictionary with memories list

        Example:
            >>> memories = client.get_all(user_id="alice", limit=50)
            >>> print(f"Total: {len(memories.get('memories', []))}")
        """
        params = self._prepare_payload(
            query="",  # Empty query returns all memories
            user_id=user_id,
            agent_id=agent_id,
            project_id=project_id,
            limit=limit,
            offset=offset
        )

        response = self.http.get(
            f"{self.config.api_endpoint}/search",
            params=params
        )

        result = self._handle_response(response)
        # Rename 'results' to 'memories' for consistency
        if 'results' in result:
            result['memories'] = result.pop('results')
        return result

    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update existing memory.

        Args:
            memory_id: Memory identifier
            content: New content
            metadata: New metadata

        Returns:
            Updated memory response

        Example:
            >>> result = client.update(
            ...     "mem_123",
            ...     content="Updated content"
            ... )
        """
        if not memory_id:
            raise ValidationError("Memory ID is required")

        payload = {"memory_id": memory_id}
        if content:
            payload["content"] = content
        if metadata:
            payload["metadata"] = metadata

        response = self.http.put(
            f"{self.config.api_endpoint}/update",
            json=payload
        )

        return self._handle_response(response)

    def delete(
        self,
        memory_id: str
    ) -> Dict[str, Any]:
        """
        Delete specific memory.

        Args:
            memory_id: Memory identifier

        Returns:
            Success response

        Example:
            >>> result = client.delete("mem_123")
        """
        if not memory_id:
            raise ValidationError("Memory ID is required")

        response = self.http.delete(
            f"{self.config.api_endpoint}/memory/{memory_id}"
        )

        return self._handle_response(response)

    def delete_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete all memories with optional filtering.

        Args:
            user_id: Filter by user
            agent_id: Filter by agent
            project_id: Project ID

        Returns:
            Deletion result

        Example:
            >>> result = client.delete_all(user_id="alice")
        """
        params = self._prepare_payload(
            user_id=user_id,
            agent_id=agent_id,
            project_id=project_id
        )

        response = self.http.delete(
            f"{self.config.api_endpoint}/memory",
            params=params
        )

        return self._handle_response(response)

    # Project Management

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.

        Returns:
            List of project dictionaries

        Example:
            >>> projects = client.list_projects()
            >>> for proj in projects:
            ...     print(f"{proj['id']}: {proj['name']}")
        """
        response = self.http.get(
            f"{self.config.api_endpoint}/projects"
        )

        data = self._handle_response(response)
        return data if isinstance(data, list) else data.get("projects", [])

    # Cogniz-Specific Features

    def optimize_prompt(
        self,
        prompt: str,
        facts: Optional[List[str]] = None,
        preset: str = "comprehensive",
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize prompt using AI.

        Args:
            prompt: Original prompt text
            facts: Additional facts to include
            preset: Optimization preset (comprehensive, concise, technical)
            project_id: Project ID

        Returns:
            Optimized prompt data

        Example:
            >>> result = client.optimize_prompt(
            ...     "Write code to sort a list",
            ...     preset="technical"
            ... )
            >>> print(result["optimized"])
        """
        payload = self._prepare_payload(
            prompt=prompt,
            preset=preset,
            project_id=project_id
        )

        if facts:
            payload["facts"] = facts

        response = self.http.post(
            f"{self.config.api_endpoint}/optimize",
            json=payload
        )

        return self._handle_response(response)

    def run_playbook(
        self,
        playbook_id: str,
        input_data: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute automation playbook.

        Args:
            playbook_id: Playbook identifier
            input_data: Input parameters
            project_id: Project ID

        Returns:
            Playbook execution result

        Example:
            >>> result = client.run_playbook(
            ...     "playbook_123",
            ...     {"url": "https://example.com"}
            ... )
        """
        payload = self._prepare_payload(
            input=input_data,
            project_id=project_id
        )

        response = self.http.post(
            f"{self.config.api_endpoint}/playbooks/{playbook_id}/run",
            json=payload
        )

        return self._handle_response(response)

    def list_playbooks(
        self,
        include_public: bool = True,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available playbooks.

        Args:
            include_public: Include public playbooks
            project_id: Project ID

        Returns:
            List of playbooks

        Example:
            >>> playbooks = client.list_playbooks()
            >>> for pb in playbooks:
            ...     print(f"{pb['id']}: {pb['name']}")
        """
        params = self._prepare_payload(
            include_public=include_public,
            project_id=project_id
        )

        response = self.http.get(
            f"{self.config.api_endpoint}/playbooks",
            params=params
        )

        data = self._handle_response(response)
        return data if isinstance(data, list) else data.get("playbooks", [])

    def get_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.

        Returns:
            User stats including plan, storage, memory count

        Example:
            >>> stats = client.get_stats()
            >>> print(f"Plan: {stats['plan']}")
            >>> print(f"Storage: {stats['storage_used']}/{stats['storage_limit']} MB")
        """
        response = self.http.get(
            f"{self.config.api_endpoint}/user-stats"
        )

        return self._handle_response(response)

    def get_debug_settings(self) -> Dict[str, Any]:
        """
        Get debug settings and platform info.

        Returns:
            Debug information

        Example:
            >>> info = client.get_debug_settings()
            >>> print(f"Version: {info['version']}")
        """
        response = self.http.get(
            f"{self.config.api_endpoint}/debug-settings"
        )

        return self._handle_response(response)

    # Knowledge Graph Operations

    def extract_entities(
        self,
        text: str,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract entities from text.

        Args:
            text: Text to analyze
            project_id: Project ID

        Returns:
            List of extracted entities

        Example:
            >>> entities = client.extract_entities(
            ...     "Emma works with David at Cogniz"
            ... )
        """
        payload = self._prepare_payload(
            text=text,
            project_id=project_id
        )

        response = self.http.post(
            f"{self.config.api_endpoint}/entities",
            json=payload
        )

        return self._handle_response(response)

    def get_graph_stats(
        self,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get knowledge graph statistics.

        Args:
            project_id: Project ID

        Returns:
            Graph statistics

        Example:
            >>> stats = client.get_graph_stats()
            >>> print(f"Entities: {stats['entity_count']}")
        """
        params = self._prepare_payload(project_id=project_id)

        response = self.http.get(
            f"{self.config.api_endpoint}/graph",
            params=params
        )

        return self._handle_response(response)

    # Context Management

    def close(self):
        """Close HTTP client."""
        if self.http:
            self.http.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        return f"Client(base_url='{self.config.base_url}')"


class AsyncClient:
    """
    Asynchronous Cogniz Memory Client.

    Provides async API access for concurrent operations.

    Example:
        >>> import asyncio
        >>> from cogniz import AsyncClient
        >>>
        >>> async def main():
        ...     async with AsyncClient(api_key="mp_...") as client:
        ...         await client.store("User message", user_id="alice")
        ...         results = await client.search("query", user_id="alice")
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        project_id: Optional[str] = None,
        config: Optional[Config] = None,
        client: Optional[httpx.AsyncClient] = None
    ):
        if config:
            self.config = config
        else:
            self.config = Config(
                api_key=api_key,
                base_url=base_url,
                project_id=project_id
            )

        if client:
            self.http = client
        else:
            self.http = httpx.AsyncClient(
                headers=self.config.get_headers(),
                timeout=self.config.timeout,
                follow_redirects=True
            )

    async def _handle_response(self, response: httpx.Response) -> Any:
        """Process HTTP response and handle errors (async)."""
        # Same logic as Client._handle_response but async-compatible
        try:
            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError("Invalid API key", status_code=response.status_code)
            elif response.status_code == 404:
                raise NotFoundError("Resource not found", status_code=404)
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", status_code=429)
            elif response.status_code == 413:
                raise QuotaExceededError("Quota exceeded", status_code=413)
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {response.status_code}", status_code=response.status_code)
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get("message", response.text)
                except:
                    message = response.text
                raise CognizError(f"API error: {message}", status_code=response.status_code)

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            raise NetworkError("Request timeout")
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {str(e)}")

    def _prepare_payload(self, **kwargs) -> Dict[str, Any]:
        """Prepare request payload."""
        payload = dict(kwargs)
        if "project_id" not in payload and self.config.project_id:
            payload["project_id"] = self.config.project_id
        return {k: v for k, v in payload.items() if v is not None}

    # Async versions of all methods

    async def store(self, content: str, **kwargs) -> Dict[str, Any]:
        """Store a memory (async)."""
        if not content:
            raise ValidationError("Content is required")

        payload = self._prepare_payload(content=content, **kwargs)
        response = await self.http.post(f"{self.config.api_endpoint}/store", json=payload)
        return await self._handle_response(response)

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search memories (async)."""
        if not query:
            raise ValidationError("Query is required")

        params = self._prepare_payload(query=query, **kwargs)
        response = await self.http.get(f"{self.config.api_endpoint}/search", params=params)
        return await self._handle_response(response)

    async def get_all(self, **kwargs) -> Dict[str, Any]:
        """Get all memories (async)."""
        params = self._prepare_payload(query="", **kwargs)  # Empty query returns all
        response = await self.http.get(f"{self.config.api_endpoint}/search", params=params)
        result = await self._handle_response(response)
        # Rename 'results' to 'memories' for consistency
        if 'results' in result:
            result['memories'] = result.pop('results')
        return result

    async def update(self, memory_id: str, **kwargs) -> Dict[str, Any]:
        """Update memory (async)."""
        payload = {"memory_id": memory_id, **kwargs}
        response = await self.http.put(f"{self.config.api_endpoint}/update", json=payload)
        return await self._handle_response(response)

    async def delete(self, memory_id: str) -> Dict[str, Any]:
        """Delete memory (async)."""
        response = await self.http.delete(f"{self.config.api_endpoint}/memory/{memory_id}")
        return await self._handle_response(response)

    async def delete_all(self, **kwargs) -> Dict[str, Any]:
        """Delete all memories (async)."""
        params = self._prepare_payload(**kwargs)
        response = await self.http.delete(f"{self.config.api_endpoint}/memory", params=params)
        return await self._handle_response(response)

    async def list_projects(self) -> List[Dict[str, Any]]:
        """List projects (async)."""
        response = await self.http.get(f"{self.config.api_endpoint}/projects")
        data = await self._handle_response(response)
        return data if isinstance(data, list) else data.get("projects", [])

    async def optimize_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Optimize prompt (async)."""
        payload = self._prepare_payload(prompt=prompt, **kwargs)
        response = await self.http.post(f"{self.config.api_endpoint}/optimize", json=payload)
        return await self._handle_response(response)

    async def run_playbook(self, playbook_id: str, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Run playbook (async)."""
        payload = self._prepare_payload(input=input_data, **kwargs)
        response = await self.http.post(f"{self.config.api_endpoint}/playbooks/{playbook_id}/run", json=payload)
        return await self._handle_response(response)

    async def list_playbooks(self, **kwargs) -> List[Dict[str, Any]]:
        """List playbooks (async)."""
        params = self._prepare_payload(**kwargs)
        response = await self.http.get(f"{self.config.api_endpoint}/playbooks", params=params)
        data = await self._handle_response(response)
        return data if isinstance(data, list) else data.get("playbooks", [])

    async def get_stats(self) -> Dict[str, Any]:
        """Get stats (async)."""
        response = await self.http.get(f"{self.config.api_endpoint}/user-stats")
        return await self._handle_response(response)

    async def get_debug_settings(self) -> Dict[str, Any]:
        """Get debug settings (async)."""
        response = await self.http.get(f"{self.config.api_endpoint}/debug-settings")
        return await self._handle_response(response)

    async def extract_entities(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract entities (async)."""
        payload = self._prepare_payload(text=text, **kwargs)
        response = await self.http.post(f"{self.config.api_endpoint}/entities", json=payload)
        return await self._handle_response(response)

    async def get_graph_stats(self, **kwargs) -> Dict[str, Any]:
        """Get graph stats (async)."""
        params = self._prepare_payload(**kwargs)
        response = await self.http.get(f"{self.config.api_endpoint}/graph", params=params)
        return await self._handle_response(response)

    async def close(self):
        """Close HTTP client (async)."""
        if self.http:
            await self.http.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        return f"AsyncClient(base_url='{self.config.base_url}')"
