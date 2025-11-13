"""Command-line interface for Conciliate."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
import sys

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .config import (
    ConciliateConfig,
    load_config,
    create_default_config,
    ensure_output_dir,
)
from .server import ConciliateServer
from .watcher import FileWatcher
from .spec_generator import SpecGenerator, SpecGeneratorError
from .summarizer import APISummarizer
from .diff_engine import DiffEngine

app = typer.Typer(
    name="conciliate",
    help="AI context synchronization for frontend/backend development",
    add_completion=False,
)

console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@app.command()
def init(
    path: Optional[Path] = typer.Argument(
        None,
        help="Directory to initialize (default: current directory)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing config file"
    ),
) -> None:
    """Initialize a new Conciliate configuration."""
    target_dir = path or Path.cwd()
    config_file = target_dir / ".conciliate.yaml"
    
    if config_file.exists() and not force:
        console.print(
            f"[yellow]Config file already exists at {config_file}[/yellow]"
        )
        console.print("Use --force to overwrite")
        raise typer.Exit(1)
    
    try:
        create_default_config(config_file)
        console.print(f"[green]OK[/green] Created config file at {config_file}")
        console.print("\nNext steps:")
        console.print("1. Edit .conciliate.yaml to configure your backend path")
        console.print("2. Run 'conciliate watch' to start monitoring")
    except Exception as e:
        console.print(f"[red]Error creating config: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def watch(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
) -> None:
    """Watch backend for changes and run Conciliate server."""
    setup_logging(verbose)
    
    try:
        # Load config
        config = load_config(config_path)
        console.print(f"[green]OK[/green] Loaded config")
        console.print(f"Watching: {config.backend_path}")
        console.print(f"Server: http://127.0.0.1:{config.port}")
        
        # Create server
        server = ConciliateServer(config)
        
        # Create file watcher
        watcher = FileWatcher(config, lambda: asyncio.create_task(server.on_file_change()))
        
        # Run both server and watcher
        async def run_all():
            # Start watcher in background
            watcher_task = asyncio.create_task(watcher.start())
            
            # Note: server.run() is blocking, so we need different approach
            console.print("[yellow]Starting file watcher and server...[/yellow]")
            
            # Keep running
            await watcher_task
        
        # For now, just run the server (watcher integration needs refinement)
        console.print("\n[cyan]Press Ctrl+C to stop[/cyan]\n")
        server.run()
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("Run 'conciliate init' first")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def serve(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file"
    ),
    port: Optional[int] = typer.Option(
        None,
        "--port",
        "-p",
        help="Port to run server on"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
) -> None:
    """Run the Conciliate server without file watching."""
    setup_logging(verbose)
    
    try:
        config = load_config(config_path)
        console.print(f"[green]OK[/green] Loaded config")
        
        server = ConciliateServer(config)
        
        server_port = port or config.port
        console.print(f"[cyan]Starting server on http://127.0.0.1:{server_port}[/cyan]")
        console.print("\n[cyan]Press Ctrl+C to stop[/cyan]\n")
        
        server.run(port=server_port)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def summary(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save summary to file"
    ),
) -> None:
    """Generate and display API summary."""
    try:
        config = load_config(config_path)
        
        # Generate spec
        generator = SpecGenerator(config)
        spec = generator.generate()
        
        # Generate summary
        summarizer = APISummarizer(config.summary_max_tokens)
        summary_text = summarizer.summarize(spec)
        
        if output:
            output.write_text(summary, encoding="utf-8")
            console.print(f"[green]OK[/green] Summary saved to {output}")
        else:
            console.print(summary_text)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except SpecGeneratorError as e:
        console.print(f"[red]Spec generation error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def diff(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file"
    ),
) -> None:
    """Show the latest API changes."""
    try:
        config = load_config(config_path)
        output_dir = ensure_output_dir(config)
        
        diff_file = output_dir / "api_diff.json"
        diff_summary_file = output_dir / "api_diff_summary.txt"
        
        if diff_summary_file.exists():
            summary = diff_summary_file.read_text(encoding="utf-8")
            console.print(summary)
        elif diff_file.exists():
            with open(diff_file, "r", encoding="utf-8") as f:
                diff_data = json.load(f)
            console.print(json.dumps(diff_data, indent=2))
        else:
            console.print("[yellow]No diff available yet[/yellow]")
            console.print("Run 'conciliate watch' to start tracking changes")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file"
    ),
) -> None:
    """Show Conciliate status and configuration."""
    try:
        config = load_config(config_path)
        output_dir = ensure_output_dir(config)
        
        # Create status table
        table = Table(title="Conciliate Status")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Backend Path", config.backend_path)
        if config.frontend_path:
            table.add_row("Frontend Path", config.frontend_path)
        table.add_row("Framework", config.framework)
        table.add_row("Server Port", str(config.port))
        table.add_row("Output Directory", config.output_dir)
        
        # Check for existing files
        spec_file = output_dir / "api_spec.json"
        if spec_file.exists():
            table.add_row("Spec Status", "[green]Available[/green]")
        else:
            table.add_row("Spec Status", "Not generated")
        
        console.print(table)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("Run 'conciliate init' first")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def mcp(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
) -> None:
    """Run the MCP (Model Context Protocol) server for AI assistants."""
    # Configure logging to file only (stdio is used for MCP protocol)
    import logging
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=".conciliate/mcp_server.log" if Path(".conciliate").exists() else None,
        filemode="a",
    )
    
    try:
        config = load_config(config_path)
        
        # Import and run MCP server (no console output - stdio is for MCP)
        from .mcp_server import run_mcp_server
        asyncio.run(run_mcp_server(config))
        
    except FileNotFoundError as e:
        # Log to stderr (not stdout which is reserved for MCP)
        import sys
        sys.stderr.write(f"Error: {e}\n")
        sys.stderr.write("Run 'conciliate init' first\n")
        raise typer.Exit(1)
    except Exception as e:
        import sys
        sys.stderr.write(f"Error: {e}\n")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show Conciliate version."""
    from . import __version__
    console.print(f"Conciliate version {__version__}")


if __name__ == "__main__":
    app()
