"""MCP stdio server for orchestration tools with gateway proxying."""

import sys
import json
import logging
from typing import Dict, Any, Optional
import httpx
from .orchestrator import DockerOrchestrator

# Configure logging to stderr (stdout reserved for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global state for gateway URL (set after init)
_gateway_url: Optional[str] = None


def get_orchestration_tool_definitions() -> list[Dict[str, Any]]:
    """Return native orchestration tool definitions."""
    return [
        {
            "name": "init",
            "description": "Initialize MCP ecosystem with gateway and manifest",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "registry_path": {"type": "string", "description": "Path to registry.yaml (optional)"}
                }
            }
        },
        {
            "name": "deploy",
            "description": "Deploy MCP server by namespace",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Server namespace from registry"}
                },
                "required": ["namespace"]
            }
        },
        {
            "name": "list",
            "description": "List all running MCP servers",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "health",
            "description": "Get health status for a server",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Server namespace"}
                },
                "required": ["namespace"]
            }
        },
        {
            "name": "logs",
            "description": "Get logs from a server container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Server namespace"},
                    "tail": {"type": "number", "description": "Number of lines to show", "default": 100}
                },
                "required": ["namespace"]
            }
        },
        {
            "name": "stop",
            "description": "Stop a running server",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Server namespace"},
                    "force": {"type": "boolean", "description": "Force kill immediately", "default": False}
                },
                "required": ["namespace"]
            }
        },
        {
            "name": "status",
            "description": "Get comprehensive orchestration status",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]


def get_gateway_tools() -> list[Dict[str, Any]]:
    """Fetch tools from gateway if available."""
    global _gateway_url

    if not _gateway_url:
        logger.debug("Gateway URL not set, skipping gateway tools")
        return []

    try:
        response = httpx.get(f"{_gateway_url}/tools", timeout=2.0)
        if response.status_code == 200:
            gateway_data = response.json()
            tools = gateway_data.get("tools", [])
            logger.info(f"Fetched {len(tools)} tools from gateway")
            return tools
    except httpx.RequestError as e:
        logger.warning(f"Failed to fetch gateway tools: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error fetching gateway tools: {e}")

    return []


def get_tool_definitions() -> list[Dict[str, Any]]:
    """Return all MCP tool definitions (orchestration + gateway)."""
    # Start with native orchestration tools
    tools = get_orchestration_tool_definitions()

    # Add gateway tools if gateway is running
    gateway_tools = get_gateway_tools()
    tools.extend(gateway_tools)

    logger.debug(f"Total tools: {len(tools)} ({len(tools) - len(gateway_tools)} orchestration + {len(gateway_tools)} gateway)")
    return tools


def call_gateway_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Proxy tool call to gateway."""
    global _gateway_url

    if not _gateway_url:
        raise ValueError("Gateway not available. Run 'init' first.")

    try:
        # Call gateway tool via HTTP POST
        response = httpx.post(
            f"{_gateway_url}/tools/{name}",
            json=arguments,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Gateway tool call failed: {e.response.status_code} - {e.response.text}")
        raise ValueError(f"Gateway error: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Gateway connection failed: {e}")
        raise ValueError(f"Cannot connect to gateway: {e}")


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute tool (orchestration or gateway) and return result."""
    global _gateway_url

    # List of native orchestration tool names
    orchestration_tools = {"init", "deploy", "list", "health", "logs", "stop", "status"}

    try:
        # Route to orchestration or gateway based on tool name
        if name in orchestration_tools:
            # Native orchestration tool
            registry_path = arguments.get("registry_path") if name == "init" else None
            orch = DockerOrchestrator(registry_path=registry_path)

            if name == "init":
                result = orch.init()
                # Set gateway URL after successful init
                _gateway_url = "http://localhost:8080"
                logger.info(f"Gateway URL set to: {_gateway_url}")
                return result
            elif name == "deploy":
                return orch.deploy(arguments["namespace"])
            elif name == "list":
                return orch.list()
            elif name == "health":
                return orch.health(arguments["namespace"])
            elif name == "logs":
                tail = arguments.get("tail", 100)
                return orch.logs(arguments["namespace"], tail=tail)
            elif name == "stop":
                force = arguments.get("force", False)
                return orch.stop(arguments["namespace"], force=force)
            elif name == "status":
                return orch.status()
        else:
            # Proxy to gateway
            logger.info(f"Proxying tool '{name}' to gateway")
            return call_gateway_tool(name, arguments)

    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        raise


def send_response(request_id: Any, result: Any = None, error: Any = None):
    """Send JSON-RPC response to stdout."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }
    
    if error:
        response["error"] = {
            "code": -32603,
            "message": str(error)
        }
    else:
        response["result"] = result
    
    print(json.dumps(response), flush=True)


def main():
    """stdio MCP server main loop."""
    logger.info("Starting orchestration MCP server (stdio mode)")
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                request_id = request.get("id")
                method = request.get("method")
                params = request.get("params", {})
                
                logger.info(f"Received request: method={method}, id={request_id}")
                
                if method == "tools/list":
                    tools = get_tool_definitions()
                    send_response(request_id, {"tools": tools})
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                    result = handle_tool_call(tool_name, arguments)
                    send_response(request_id, result)
                
                else:
                    send_response(request_id, error=f"Unknown method: {method}")
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                send_response(None, error=f"Invalid JSON: {e}")
            
            except Exception as e:
                logger.error(f"Request handling error: {e}", exc_info=True)
                send_response(request_id if 'request_id' in locals() else None, error=str(e))
    
    except KeyboardInterrupt:
        logger.info("Shutting down stdio MCP server")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
