"""Command-line interface for IOWarp Agent Toolkit."""

import click
import sys
from pathlib import Path


@click.group()
@click.version_option()
def main():
    """IOWarp Agent Toolkit - MCP Servers, Clients, and Tools for AI Agents.

    A comprehensive collection of Model Context Protocol (MCP) servers
    for scientific computing, HPC resources, and research datasets.
    """
    pass


@main.command()
def list_servers():
    """List all available MCP servers."""
    servers = [
        ("hdf5", "HDF5 FastMCP - Scientific Data Access"),
        ("parquet", "Parquet FastMCP - Apache Parquet Data Access"),
        ("pandas", "Pandas FastMCP - Data Analysis and Manipulation"),
        ("slurm", "Slurm FastMCP - HPC Job Management"),
        ("arxiv", "ArXiv FastMCP - Research Paper Discovery"),
        ("plot", "Plot FastMCP - Data Visualization"),
        ("compression", "Compression FastMCP - File Compression Tools"),
        ("lmod", "Lmod FastMCP - Environment Module Management"),
        ("chronolog", "ChronoLog FastMCP - Data Logging"),
        ("adios", "ADIOS FastMCP - Advanced I/O System"),
        ("ndp", "NDP FastMCP - NDP Dataset Discovery"),
        ("darshan", "Darshan FastMCP - I/O Characterization"),
        ("jarvis", "Jarvis FastMCP - System Configuration"),
        ("node-hardware", "Node Hardware FastMCP - Hardware Information"),
        ("parallel-sort", "Parallel Sort FastMCP - Parallel Sorting"),
    ]

    click.echo("\nAvailable MCP Servers:")
    click.echo("=" * 60)
    for name, description in servers:
        click.echo(f"\n  {name}")
        click.echo(f"    {description}")
    click.echo("\n" + "=" * 60)
    click.echo("\nTo use a server, install with: pip install iowarp-agent-toolkit[<server-name>]")
    click.echo("To install all servers: pip install iowarp-agent-toolkit[all]")


@main.command()
@click.argument('server_name')
def info(server_name):
    """Show detailed information about a specific MCP server."""
    server_info = {
        "hdf5": {
            "description": "HDF5 FastMCP - Scientific Data Access for AI Agents",
            "package": "hdf5-mcp",
            "dependencies": ["h5py", "numpy"],
        },
        "parquet": {
            "description": "Parquet FastMCP - Apache Parquet Data Access",
            "package": "parquet-mcp",
            "dependencies": ["pyarrow", "pandas"],
        },
        "pandas": {
            "description": "Pandas FastMCP - Data Analysis and Manipulation",
            "package": "pandas-mcp",
            "dependencies": ["pandas", "numpy"],
        },
        "slurm": {
            "description": "Slurm FastMCP - HPC Job Management",
            "package": "slurm-mcp",
            "dependencies": ["pydantic"],
        },
        "arxiv": {
            "description": "ArXiv FastMCP - Research Paper Discovery",
            "package": "arxiv-mcp",
            "dependencies": ["arxiv", "pydantic"],
        },
        "plot": {
            "description": "Plot FastMCP - Data Visualization",
            "package": "plot-mcp",
            "dependencies": ["matplotlib", "numpy"],
        },
    }

    if server_name not in server_info:
        click.echo(f"Error: Unknown server '{server_name}'", err=True)
        click.echo("\nUse 'iowarp-agent-toolkit list-servers' to see all available servers.")
        sys.exit(1)

    info = server_info[server_name]
    click.echo(f"\n{server_name} MCP Server")
    click.echo("=" * 60)
    click.echo(f"\nDescription: {info['description']}")
    click.echo(f"Package: {info['package']}")
    click.echo(f"Dependencies: {', '.join(info['dependencies'])}")
    click.echo("\n" + "=" * 60)


@main.command()
def version():
    """Show the version of IOWarp Agent Toolkit."""
    from iowarp_agent_toolkit import __version__
    click.echo(f"IOWarp Agent Toolkit version {__version__}")


if __name__ == "__main__":
    main()
