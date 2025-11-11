"""Registry polling for auto-discovery of MCP servers."""

import asyncio
import yaml
from pathlib import Path
from typing import Optional, Callable, Awaitable
from .models import Registry, ServerEntry, ToolDefinition


class RegistryPoller:
    """Polls registry.yaml for server definitions and triggers updates."""

    def __init__(
        self,
        registry_path: Path,
        poll_interval: int = 60,
        on_change: Optional[Callable[[Registry], Awaitable[None]]] = None
    ):
        """
        Initialize registry poller.

        Args:
            registry_path: Path to registry.yaml file
            poll_interval: Polling interval in seconds (default: 60)
            on_change: Optional async callback invoked when registry changes
        """
        self.registry_path = registry_path
        self.poll_interval = poll_interval
        self.on_change = on_change
        self._is_polling = False
        self._polling_task: Optional[asyncio.Task] = None
        self._current_registry: Optional[Registry] = None

    @property
    def is_polling(self) -> bool:
        """Return whether polling is currently active."""
        return self._is_polling

    async def load_registry(self) -> Registry:
        """
        Load registry from YAML file.

        Returns:
            Registry object parsed from YAML

        Raises:
            FileNotFoundError: If registry file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")

        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse registry YAML: {e}")

        # Parse registry data into Pydantic models
        registry = Registry(
            version=data.get('version', '1.0'),
            servers=[]
        )

        for server_data in data.get('servers', []):
            # Parse tools
            tools = []
            for tool_data in server_data.get('tools', []):
                if isinstance(tool_data, dict):
                    tools.append(ToolDefinition(**tool_data))

            # Create server entry
            server = ServerEntry(
                namespace=server_data['namespace'],
                name=server_data['name'],
                docker_image=server_data.get('docker_image'),
                port=server_data['port'],
                health_url=server_data.get('health_url'),
                tools=tools
            )
            registry.servers.append(server)

        return registry

    async def poll_once(self) -> Registry:
        """
        Poll registry once and return current state.

        Returns:
            Registry object

        Raises:
            FileNotFoundError: If registry file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        registry = await self.load_registry()
        self._current_registry = registry

        # Invoke callback if provided
        if self.on_change:
            await self.on_change(registry)

        return registry

    async def start_polling(self):
        """Start background polling task."""
        if self._is_polling:
            return

        self._is_polling = True
        self._polling_task = asyncio.create_task(self._poll_loop())

    async def stop_polling(self):
        """Stop background polling task."""
        if not self._is_polling:
            return

        self._is_polling = False

        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None

    async def _poll_loop(self):
        """Internal polling loop (runs in background task)."""
        while self._is_polling:
            try:
                await self.poll_once()
            except Exception as e:
                # Log error but don't stop polling
                # In production, use proper logging
                print(f"Error during registry poll: {e}")

            # Wait for next poll interval
            await asyncio.sleep(self.poll_interval)
