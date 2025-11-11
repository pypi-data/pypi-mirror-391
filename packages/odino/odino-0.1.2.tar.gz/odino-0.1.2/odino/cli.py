"""CLI interface for Odino semantic search tool."""

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from .indexer import Indexer
from .searcher import Searcher
from .utils import load_config, save_config

app = typer.Typer(
    name="odino",
    help="Local semantic search CLI for codebases using embeddings",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        console.print("Odino v1.0.0 - Local Semantic Search CLI")
        console.print("Using embeddinggemma-300m model for fast indexing")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    query_text: Annotated[
        Optional[str],
        typer.Option("--query", "-q", help="Search query in natural language"),
    ] = None,
    results: Annotated[
        Optional[int],
        typer.Option(
            "--results", "-r", help="Number of results to return", min=1, max=100
        ),
    ] = None,
    include: Annotated[
        Optional[str],
        typer.Option(
            "--include", help="Include only files matching this pattern (glob)"
        ),
    ] = None,
    exclude: Annotated[
        Optional[str],
        typer.Option("--exclude", help="Exclude files matching this pattern (glob)"),
    ] = None,
    path: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            "-p",
            help="Directory to search in",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """Odino - Local semantic search CLI for codebases."""
    if ctx.invoked_subcommand is None:
        if query_text is None:
            console.print(ctx.get_help())
            raise typer.Exit()
        if path is None:
            path = Path(".")
        query(
            query_text=query_text,
            path=path,
            results=results,
            include=include,
            exclude=exclude,
        )


@app.command()
def index(
    path: Path = typer.Argument(
        ".",
        help="Directory to index",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    model: str = typer.Option(
        "EmmanuelEA/eea-embedding-gemma",
        "--model",
        "-m",
        help="Sentence transformer model to use for embeddings",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force reindex even if files haven't changed",
    ),
    chunk_size: int = typer.Option(
        512,
        "--chunk-size",
        help="Size of text chunks for indexing",
        min=100,
        max=2048,
    ),
    chunk_overlap: int = typer.Option(
        50,
        "--chunk-overlap",
        help="Overlap between chunks",
        min=0,
        max=200,
    ),
) -> None:
    """Index files in a directory for semantic search."""
    try:
        config = load_config(path)

        # Update config with command line options
        config["model_name"] = model
        config["chunk_size"] = chunk_size
        config["chunk_overlap"] = chunk_overlap

        save_config(path, config)

        console.print(
            Panel.fit(
                f"[bold blue]Indexing directory:[/bold blue] {path.absolute()}\n"
                f"[bold blue]Model:[/bold blue] {model}\n"
                f"[bold blue]Chunk size:[/bold blue] {chunk_size}\n"
                f"[bold blue]Chunk overlap:[/bold blue] {chunk_overlap}",
                title="Odino Indexer",
                border_style="blue",
            )
        )

        indexer = Indexer(path, console)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing...", total=None)

            stats = indexer.index(
                force=force,
                progress_callback=lambda msg: progress.update(task, description=msg),
            )

        console.print(
            Panel.fit(
                f"[bold green]Indexing complete![/bold green]\n"
                f"Files indexed: {stats['files_indexed']}\n"
                f"Chunks created: {stats['chunks_created']}\n"
                f"Total size: {stats['total_size_mb']:.1f} MB",
                title="Success",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[bold red]Error during indexing:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def query(
    query_text: str = typer.Option(
        ...,
        "--query",
        "-q",
        help="Search query in natural language",
    ),
    path: Path = typer.Argument(
        ".",
        help="Directory to search in",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    results: Optional[int] = typer.Option(
        None,
        "--results",
        "-r",
        help="Number of results to return",
        min=1,
        max=100,
    ),
    include: Optional[str] = typer.Option(
        None,
        "--include",
        help="Include only files matching this pattern (glob)",
    ),
    exclude: Optional[str] = typer.Option(
        None,
        "--exclude",
        help="Exclude files matching this pattern (glob)",
    ),
) -> None:
    """Search indexed files using natural language queries."""
    try:
        config = load_config(path)

        effective_results = (
            results if results is not None else config.get("max_results", 2)
        )

        console.print(
            Panel.fit(
                f"[bold blue]Searching:[/bold blue] {query_text}\n"
                f"[bold blue]Directory:[/bold blue] {path.absolute()}\n"
                f"[bold blue]Max results:[/bold blue] {effective_results}",
                title="Odino Search",
                border_style="blue",
            )
        )

        searcher = Searcher(path, console)

        with console.status("[bold blue]Searching..."):
            search_results = searcher.search(
                query_text,
                top_k=effective_results,
                include_pattern=include,
                exclude_pattern=exclude,
            )

        if not search_results:
            console.print("[yellow]No results found. Try a different query.[/yellow]")
            return

        # Display results in a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=False)
        table.add_column("Score", style="green", width=8)
        table.add_column("Content", style="white")

        for result in search_results:
            file_path = result.file_path
            score = f"{result.score:.3f}"
            content = result.content
            start_line = result.start_line

            # Create syntax highlighted content
            try:
                syntax = Syntax(
                    content,
                    "python",  # Auto-detect would be better
                    theme="monokai",
                    line_numbers=True,
                    start_line=start_line,
                    line_range=(start_line, start_line + content.count("\n") + 1),
                )
                table.add_row(file_path, score, syntax)
            except Exception:
                # Fallback to plain text
                table.add_row(file_path, score, content)

        console.print(table)
        console.print(f"\n[bold green]Found {len(search_results)} results[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error during search:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def status(
    path: Path = typer.Argument(
        ".",
        help="Directory to check status for",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Show indexing status and configuration."""
    try:
        config = load_config(path)
        odino_dir = path / ".odino"

        if not odino_dir.exists():
            console.print("[yellow]No index found. Run 'odino index' first.[/yellow]")
            return

        # Get index info
        from .searcher import Searcher

        searcher = Searcher(path, config)
        index_info = searcher.get_index_info()

        console.print(
            Panel.fit(
                f"[bold blue]Configuration:[/bold blue]\n"
                f"  Model: {config['model_name']}\n"
                f"  Chunk size: {config['chunk_size']}\n"
                f"  Chunk overlap: {config['chunk_overlap']}\n"
                f"  Max results: {config['max_results']}\n\n"
                f"[bold blue]Index Status:[/bold blue]\n"
                f"  Total chunks: {index_info['total_chunks']}\n"
                f"  Indexed files: {index_info['indexed_files']}\n"
                f"  Last updated: {index_info['last_updated']}",
                title="Odino Status",
                border_style="blue",
            )
        )

    except Exception as e:
        console.print(f"[bold red]Error getting status:[/bold red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
