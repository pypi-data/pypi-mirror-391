"""MCP HTTP server for orchestration tools."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .orchestrator import DockerOrchestrator

app = FastAPI(title="Chora MCP Orchestration", version="0.1.0")


# Pydantic models for request/response
class InitRequest(BaseModel):
    registry_path: Optional[str] = None


class DeployRequest(BaseModel):
    namespace: str


class HealthRequest(BaseModel):
    namespace: str


class LogsRequest(BaseModel):
    namespace: str
    tail: Optional[int] = 100


class StopRequest(BaseModel):
    namespace: str
    force: Optional[bool] = False


class StatusRequest(BaseModel):
    pass


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/tools")
def list_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {"name": "init", "description": "Initialize MCP ecosystem"},
            {"name": "deploy", "description": "Deploy MCP server"},
            {"name": "list", "description": "List running servers"},
            {"name": "health", "description": "Get server health"},
            {"name": "logs", "description": "Get server logs"},
            {"name": "stop", "description": "Stop a server"},
            {"name": "status", "description": "Get orchestration status"}
        ]
    }


@app.post("/tools/init")
def init_tool(request: InitRequest):
    """Initialize MCP ecosystem."""
    try:
        orch = DockerOrchestrator(registry_path=request.registry_path)
        result = orch.init()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/deploy")
def deploy_tool(request: DeployRequest):
    """Deploy MCP server."""
    try:
        orch = DockerOrchestrator()
        result = orch.deploy(request.namespace)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/list")
def list_tool(request: dict):
    """List running servers."""
    try:
        orch = DockerOrchestrator()
        result = orch.list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/health")
def health_tool(request: HealthRequest):
    """Get server health."""
    try:
        orch = DockerOrchestrator()
        result = orch.health(request.namespace)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/logs")
def logs_tool(request: LogsRequest):
    """Get server logs."""
    try:
        orch = DockerOrchestrator()
        result = orch.logs(request.namespace, tail=request.tail)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/stop")
def stop_tool(request: StopRequest):
    """Stop a server."""
    try:
        orch = DockerOrchestrator()
        result = orch.stop(request.namespace, force=request.force)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/status")
def status_tool(request: dict):
    """Get orchestration status."""
    try:
        orch = DockerOrchestrator()
        result = orch.status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Entry point for MCP HTTP server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)


if __name__ == "__main__":
    main()
