"""Docker orchestrator for managing MCP server containers."""

import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import yaml
import docker
import httpx


@dataclass
class ServerDefinition:
    """Definition of an MCP server from registry."""
    namespace: str
    name: str
    docker_image: str
    port: int
    health_url: str
    tools: List[Dict[str, str]] = None
    volumes: Dict[str, Dict[str, str]] = None  # {host_path: {'bind': container_path, 'mode': 'rw'}}


class DockerOrchestrator:
    """Manages MCP server containers via Docker SDK."""

    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize orchestrator.

        Args:
            registry_path: Path to registry.yaml file (absolute or relative to cwd)
                          If None, uses smart path resolution with fallback hierarchy.
        """
        self.client = docker.from_env()
        self.registry_path = self._resolve_registry_path(registry_path)
        self.registry = self._load_registry()

    def _resolve_registry_path(self, explicit_path: Optional[str] = None) -> Path:
        """
        Resolve registry.yaml path using fallback hierarchy.

        Priority (first existing path wins):
        1. Explicit path argument (if provided)
        2. CHORA_REGISTRY_PATH environment variable
        3. Workspace-relative path (cwd/chora-mcp-gateway/config/registry.yaml)
        4. User home directory (~/.chora/registry.yaml)
        5. If none exist, return workspace-relative path (will be created/used)

        Args:
            explicit_path: Optional explicit path to registry file

        Returns:
            Resolved Path object to registry.yaml
        """
        # Priority 1: Explicit path
        if explicit_path:
            path = Path(explicit_path)
            # Make absolute if relative
            if not path.is_absolute():
                path = Path.cwd() / path
            return path.resolve()

        # Priority 2: Environment variable
        env_path = os.getenv("CHORA_REGISTRY_PATH")
        if env_path:
            path = Path(env_path)
            if not path.is_absolute():
                path = Path.cwd() / path
            if path.exists():
                return path.resolve()

        # Priority 3: Workspace-relative (current working directory)
        workspace_path = Path.cwd() / "chora-mcp-gateway" / "config" / "registry.yaml"
        if workspace_path.exists():
            return workspace_path.resolve()

        # Priority 4: User home directory
        home_path = Path.home() / ".chora" / "registry.yaml"
        if home_path.exists():
            return home_path.resolve()

        # Priority 5: Default to workspace-relative (even if doesn't exist yet)
        # This allows creating the file in the expected location
        return workspace_path.resolve()

    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from YAML file using pathlib."""
        try:
            if not self.registry_path.exists():
                # Return empty registry if file doesn't exist
                return {"version": "1.0", "servers": []}

            with self.registry_path.open('r', encoding='utf-8') as f:
                registry = yaml.safe_load(f)

            # Validate basic registry structure
            if not isinstance(registry, dict):
                raise ValueError(f"Invalid registry format in {self.registry_path}: expected dict, got {type(registry)}")

            if "servers" not in registry:
                registry["servers"] = []

            return registry

        except FileNotFoundError:
            return {"version": "1.0", "servers": []}
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse registry YAML at {self.registry_path}: {e}")

    def _get_server_def(self, namespace: str) -> ServerDefinition:
        """Get server definition by namespace."""
        for server in self.registry.get("servers", []):
            if server["namespace"] == namespace:
                return ServerDefinition(
                    namespace=server["namespace"],
                    name=server["name"],
                    docker_image=server["docker_image"],
                    port=server["port"],
                    health_url=server.get("health_url", ""),
                    tools=server.get("tools", []),
                    volumes=server.get("volumes")
                )
        raise ValueError(f"Namespace '{namespace}' not found in registry")

    def _ensure_network(self) -> None:
        """Ensure mcp-network exists."""
        try:
            self.client.networks.get("mcp-network")
        except docker.errors.NotFound:
            self.client.networks.create("mcp-network", driver="bridge")

    def _wait_for_health(self, container_name: str, health_url: str, timeout: int = 30) -> bool:
        """Wait for container to become healthy."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check Docker health status
                container = self.client.containers.get(container_name)
                health_status = container.attrs.get("State", {}).get("Health", {}).get("Status")

                if health_status == "healthy":
                    return True

                # Also try HTTP health check
                if health_url:
                    try:
                        response = httpx.get(health_url.replace(container_name, "localhost"), timeout=2.0)
                        if response.status_code == 200:
                            return True
                    except:
                        pass

            except Exception:
                pass

            time.sleep(2)

        return False

    def _get_container_by_namespace(self, namespace: str) -> Any:
        """Find container by namespace."""
        container_name = f"chora-mcp-{namespace}"
        try:
            return self.client.containers.get(container_name)
        except docker.errors.NotFound:
            raise ValueError(f"Server not found: {namespace}")

    def init(self) -> Dict[str, Any]:
        """
        Initialize MCP ecosystem with gateway and manifest.

        Returns:
            Status dictionary with initialized services
        """
        self._ensure_network()

        services = []

        # Deploy gateway and manifest
        for namespace in ["gateway", "manifest"]:
            try:
                result = self.deploy(namespace)
                services.append({
                    "name": namespace,
                    "status": "healthy" if result.get("health_status") == "healthy" else "unhealthy",
                    "port": result.get("port")
                })
            except Exception as e:
                services.append({
                    "name": namespace,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "status": "initialized",
            "services": services,
            "network": "mcp-network"
        }

    def deploy(self, namespace: str) -> Dict[str, Any]:
        """
        Deploy an MCP server container.

        Args:
            namespace: Server namespace from registry

        Returns:
            Deployment status dictionary
        """
        server_def = self._get_server_def(namespace)
        self._ensure_network()

        # Check if container already exists
        container_name = f"chora-mcp-{namespace}"
        try:
            existing = self.client.containers.get(container_name)
            existing.stop()
            existing.remove()
        except docker.errors.NotFound:
            pass

        # Prepare volumes
        volumes = server_def.volumes or {}

        # Special handling: auto-mount config for gateway if not specified
        if namespace == "gateway" and not any("/app/config" in str(v) for v in volumes.values()):
            # Try to find config directory in workspace (using pathlib)
            workspace_root = Path.cwd()
            config_path = workspace_root / "chora-mcp-gateway" / "config"
            if config_path.exists():
                volumes[str(config_path)] = {'bind': '/app/config', 'mode': 'rw'}

        # Run container
        container = self.client.containers.run(
            server_def.docker_image,
            name=container_name,
            ports={f"{server_def.port}/tcp": server_def.port},
            network="mcp-network",
            volumes=volumes if volumes else None,
            detach=True,
            remove=False
        )

        # Wait for health check
        health_status = "healthy" if self._wait_for_health(container_name, server_def.health_url) else "unhealthy"

        return {
            "status": "deployed",
            "namespace": namespace,
            "container_id": container.id,
            "port": server_def.port,
            "health_status": health_status
        }

    def list(self) -> Dict[str, Any]:
        """
        List all running MCP servers.

        Returns:
            Dictionary with list of servers
        """
        containers = self.client.containers.list(filters={"network": "mcp-network"})

        servers = []
        for container in containers:
            # Extract namespace from container name
            name = container.name
            namespace = name.replace("chora-mcp-", "") if name.startswith("chora-mcp-") else name

            # Get port mapping
            ports = container.attrs.get("NetworkSettings", {}).get("Ports", {})
            port = None
            for port_spec, bindings in ports.items():
                if bindings:
                    port = int(bindings[0]["HostPort"])
                    break

            # Get health status
            health = container.attrs.get("State", {}).get("Health", {}).get("Status", "unknown")

            # Calculate uptime
            started_at = container.attrs.get("State", {}).get("StartedAt", "")
            uptime = "unknown"  # Simplified for now

            servers.append({
                "namespace": namespace,
                "container_id": container.id[:12],
                "status": container.status,
                "health": health,
                "port": port,
                "uptime": uptime
            })

        return {"servers": servers}

    def health(self, namespace: str) -> Dict[str, Any]:
        """
        Get health status for a server.

        Args:
            namespace: Server namespace

        Returns:
            Health status dictionary
        """
        container = self._get_container_by_namespace(namespace)
        server_def = self._get_server_def(namespace)

        # Get Docker status
        docker_status = container.status

        # Query health endpoint
        health_response = None
        tools_count = 0

        try:
            health_url = server_def.health_url.replace(f"chora-mcp-{namespace}", "localhost")
            response = httpx.get(health_url, timeout=5.0)
            if response.status_code == 200:
                health_response = response.json()

                # Also get tools count
                tools_url = health_url.replace("/health", "/tools")
                tools_response = httpx.get(tools_url, timeout=5.0)
                if tools_response.status_code == 200:
                    tools_count = len(tools_response.json().get("tools", []))
        except Exception:
            health_response = {"error": "Health check failed"}

        return {
            "namespace": namespace,
            "container_id": container.id[:12],
            "docker_status": docker_status,
            "health_endpoint": server_def.health_url.replace(f"chora-mcp-{namespace}", "localhost"),
            "health_response": health_response,
            "tools_count": tools_count,
            "uptime": "unknown"  # Simplified
        }

    def logs(self, namespace: str, tail: int = 100) -> Dict[str, Any]:
        """
        Get logs from a server container.

        Args:
            namespace: Server namespace
            tail: Number of lines to return

        Returns:
            Dictionary with logs
        """
        container = self._get_container_by_namespace(namespace)

        logs_bytes = container.logs(tail=tail)
        logs_str = logs_bytes.decode('utf-8')
        log_lines = [line for line in logs_str.split('\n') if line.strip()]

        return {
            "namespace": namespace,
            "logs": log_lines,
            "lines": len(log_lines)
        }

    def stop(self, namespace: str, force: bool = False) -> Dict[str, Any]:
        """
        Stop a server container.

        Args:
            namespace: Server namespace
            force: If True, kill immediately; otherwise graceful shutdown

        Returns:
            Stop status dictionary
        """
        container = self._get_container_by_namespace(namespace)

        if force:
            container.kill()
            graceful = False
        else:
            container.stop(timeout=10)
            graceful = True

        return {
            "status": "stopped",
            "namespace": namespace,
            "graceful": graceful
        }

    def status(self) -> Dict[str, Any]:
        """
        Get comprehensive orchestration status.

        Returns:
            Status dictionary with all information
        """
        # Check Docker daemon
        try:
            self.client.ping()
            docker_status = "connected"
        except Exception:
            docker_status = "disconnected"
            return {
                "docker_status": docker_status,
                "error": "Docker daemon not accessible"
            }

        # Get running servers
        list_result = self.list()
        servers = list_result["servers"]
        servers_running = len(servers)
        servers_healthy = sum(1 for s in servers if s["health"] == "healthy")

        # Check gateway
        gateway_status = {"status": "unknown"}
        gateway_tools_count = 0

        try:
            response = httpx.get("http://localhost:8080/health", timeout=5.0)
            if response.status_code == 200:
                gateway_status = response.json()

                # Get tools count
                tools_response = httpx.get("http://localhost:8080/tools", timeout=5.0)
                if tools_response.status_code == 200:
                    gateway_tools_count = len(tools_response.json().get("tools", []))
        except Exception:
            gateway_status = {"status": "unreachable"}

        return {
            "docker_status": docker_status,
            "network": "mcp-network",
            "gateway": {
                "status": gateway_status.get("status"),
                "url": "http://localhost:8080",
                "tools_count": gateway_tools_count
            },
            "servers_running": servers_running,
            "servers_healthy": servers_healthy,
            "servers": servers
        }
