"""
Searcher module for Odino CLI
Handles semantic search queries and result formatting
"""

from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# Lazy import of heavy ML libs to avoid CLI startup freeze
from typing import Any

from .utils import load_config
import json
import os
import time


class SearchResult:
    """Represents a single search result."""

    def __init__(
        self,
        file_path: str,
        content: str,
        score: float,
        start_line: int,
        end_line: int,
        metadata: Dict,
    ):
        self.file_path = file_path
        self.content = content
        self.score = score
        self.start_line = start_line
        self.end_line = end_line
        self.metadata = metadata


class Searcher:
    """Handles semantic search queries."""

    def __init__(self, project_root: Path, console: Optional[Console] = None):
        self.project_root = project_root
        self.console = console or Console()
        self.config = load_config(project_root)
        self.model: Optional[Any] = None

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(project_root / ".odino" / "chroma_db"),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.config["collection_name"]
            )
        except Exception as e:
            self.console.print(
                f"[red]Error: Collection not found. Please run 'odino index' first.[/red]"
            )
            raise

        # Defer model loading until needed
        self.console.print("Preparing searcher...")

    def _load_model(self) -> None:
        """Load the embedding model lazily with feedback and error handling."""
        if self.model is not None:
            return
        try:
            self.console.print(f"Loading embedding model: {self.config['model_name']}")
            from sentence_transformers import SentenceTransformer  # type: ignore

            self.model = SentenceTransformer(self.config["model_name"])
            self.console.print("Model loaded successfully")
        except KeyboardInterrupt:
            self.console.print("[red]Model loading cancelled by user[/red]")
            raise
        except Exception as e:
            self.console.print(f"[red]Failed to load embedding model: {e}[/red]")
            raise

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None,
    ) -> List[SearchResult]:
        """Perform semantic search and return results."""
        if top_k is None:
            top_k = self.config.get("max_results", 10)

        # Generate query embedding
        self.console.print("Processing query...")
        self._load_model()
        try:
            query_embedding = self.model.encode([query])
        except KeyboardInterrupt:
            self.console.print("[red]Query processing cancelled by user[/red]")
            raise
        except Exception as e:
            self.console.print(f"[red]Failed to process query: {e}[/red]")
            return []

        # Search in ChromaDB
        self.console.print("Searching...")
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(), n_results=top_k
        )

        if not results["ids"][0]:
            return []

        # Convert to SearchResult objects
        search_results = []

        for i, doc_id in enumerate(results["ids"][0]):
            document = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            # Convert distance to similarity score (0-1)
            score = 1.0 - distance

            result = SearchResult(
                file_path=metadata["file_path"],
                content=document,
                score=score,
                start_line=metadata["start_line"],
                end_line=metadata["end_line"],
                metadata=metadata,
            )

            search_results.append(result)

        # Apply include/exclude filtering if provided
        if include_pattern or exclude_pattern:
            import fnmatch

            filtered = []
            for r in search_results:
                fp = r.file_path.lower()
                if include_pattern and not fnmatch.fnmatch(fp, include_pattern.lower()):
                    continue
                if exclude_pattern and fnmatch.fnmatch(fp, exclude_pattern.lower()):
                    continue
                filtered.append(r)
            return filtered

        return search_results

    def format_results(self, results: List[SearchResult], query: str) -> None:
        """Format and display search results."""
        if not results:
            self.console.print("[yellow]No results found.[/yellow]")
            return

        self.console.print(
            f"\n[bold green]Found {len(results)} results:[/bold green]\n"
        )

        for i, result in enumerate(results, 1):
            # Create a panel for each result
            score_color = (
                "green"
                if result.score > 0.7
                else "yellow" if result.score > 0.4 else "red"
            )

            # File header
            header = f"[bold cyan]{result.file_path}[/bold cyan]"
            if result.start_line != result.end_line:
                header += f" [dim](lines {result.start_line}-{result.end_line})[/dim]"
            else:
                header += f" [dim](line {result.start_line})[/dim]"

            header += (
                f" [bold {score_color}](score: {result.score:.3f})[/bold {score_color}]"
            )

            # Content preview
            content = result.content.strip()
            if len(content) > 500:
                content = content[:500] + "..."

            # Try to detect language for syntax highlighting
            language = self._detect_language(result.file_path)

            if language:
                syntax = Syntax(content, language, theme="monokai", line_numbers=True)
                content_panel = Panel(syntax, title=header, border_style="blue")
            else:
                content_panel = Panel(content, title=header, border_style="blue")

            self.console.print(content_panel)
            self.console.print()

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml",
            ".sql": "sql",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "zsh",
            ".fish": "fish",
            ".vim": "vim",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
            ".m": "objective-c",
            ".mm": "objective-c",
            ".pl": "perl",
            ".lua": "lua",
            ".dart": "dart",
            ".vue": "vue",
            ".tex": "latex",
            ".md": "markdown",
            ".rst": "rst",
        }

        import os

        _, ext = os.path.splitext(file_path.lower())
        return ext_to_lang.get(ext)

    def search_with_filter(
        self,
        query: str,
        include_pattern: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        """Search with file type filtering."""
        results = self.search(query, top_k)

        if include_pattern:
            import fnmatch

            filtered_results = []

            for result in results:
                if fnmatch.fnmatch(result.file_path.lower(), include_pattern.lower()):
                    filtered_results.append(result)

            return filtered_results

        return results

    def get_index_info(self) -> Dict[str, Optional[str]]:
        """Return basic index information for status command."""
        try:
            total_chunks = self.collection.count()  # type: ignore[attr-defined]
        except Exception:
            total_chunks = 0
        indexed_files_count = 0
        last_updated_str: Optional[str] = None
        try:
            index_file = self.project_root / ".odino" / "indexed_files.json"
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        indexed_files_count = len(data)
                mtime = os.path.getmtime(index_file)
                last_updated_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(mtime)
                )
        except Exception:
            pass
        return {
            "total_chunks": str(total_chunks),
            "indexed_files": str(indexed_files_count),
            "last_updated": last_updated_str or "unknown",
        }
