"""CLI commands for chora-mcp-orchestration."""

import click
import json
from .orchestrator import DockerOrchestrator


@click.group()
@click.option('--registry', default=None, help='Path to registry.yaml')
@click.pass_context
def cli(ctx, registry):
    """Chora MCP Orchestration CLI."""
    ctx.ensure_object(dict)
    ctx.obj['registry'] = registry


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize MCP ecosystem with gateway and manifest."""
    try:
        orch = DockerOrchestrator(registry_path=ctx.obj.get('registry'))
        result = orch.init()
        
        click.echo(f"Status: {result['status']}")
        click.echo(f"Network: {result['network']}")
        click.echo("Services:")
        for svc in result['services']:
            click.echo(f"  {svc['name']}: {svc['status']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('namespace')
@click.pass_context
def deploy(ctx, namespace):
    """Deploy MCP server by namespace."""
    try:
        orch = DockerOrchestrator(registry_path=ctx.obj.get('registry'))
        result = orch.deploy(namespace)
        
        click.echo(f"Status: {result['status']}")
        click.echo(f"Namespace: {result['namespace']}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command(name='list')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def list_servers(ctx, format):
    """List all running MCP servers."""
    try:
        orch = DockerOrchestrator(registry_path=ctx.obj.get('registry'))
        result = orch.list()
        
        if format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            for server in result['servers']:
                click.echo(f"{server['namespace']} - {server.get('status', 'unknown')}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('namespace')
@click.pass_context
def health(ctx, namespace):
    """Get health status for a server."""
    try:
        orch = DockerOrchestrator(registry_path=ctx.obj.get('registry'))
        result = orch.health(namespace)
        
        click.echo(f"Namespace: {result['namespace']}")
        click.echo(f"Docker Status: {result['docker_status']}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('namespace')
@click.option('--tail', default=100, help='Number of lines to show')
@click.pass_context
def logs(ctx, namespace, tail):
    """Get logs from a server container."""
    try:
        orch = DockerOrchestrator(registry_path=ctx.obj.get('registry'))
        result = orch.logs(namespace, tail=tail)
        
        for line in result['logs']:
            click.echo(line)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('namespace')
@click.option('--force', is_flag=True, help='Force kill immediately')
@click.pass_context
def stop(ctx, namespace, force):
    """Stop a running server."""
    try:
        orch = DockerOrchestrator(registry_path=ctx.obj.get('registry'))
        result = orch.stop(namespace, force=force)
        
        click.echo(f"Status: {result['status']}")
        click.echo(f"Namespace: {result['namespace']}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def status(ctx, format):
    """Get comprehensive orchestration status."""
    try:
        orch = DockerOrchestrator(registry_path=ctx.obj.get('registry'))
        result = orch.status()

        if format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Docker: {result['docker_status']}")
            click.echo(f"Servers running: {result['servers_running']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def mcp():
    """Start MCP server in stdio mode (for AI clients like Cline, Claude Desktop)."""
    from .mcp_stdio import main as stdio_main
    stdio_main()


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == '__main__':
    main()
