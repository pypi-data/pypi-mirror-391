"""
Indexer module for Odino CLI
Handles file discovery, text processing, and embedding generation
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

import chromadb
from chromadb.config import Settings
from rich.console import Console
from rich.progress import Progress, TaskID

# Lazy import: heavy ML libs can freeze during CLI startup
from typing import Any
from tqdm import tqdm

# Try to import torch for memory management
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .utils import (
    chunk_text,
    format_file_size,
    is_text_file,
    load_config,
    load_ignore_patterns,
    should_ignore_file,
)

# Disable MPS memory limit to prevent out of memory errors on Apple Silicon
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"


class Indexer:
    """Handles indexing of files and generation of embeddings."""

    def __init__(self, project_root: Path, console: Optional[Console] = None):
        self.project_root = project_root
        self.console = console or Console()
        self.config = load_config(project_root)
        self.ignore_patterns = load_ignore_patterns(project_root)
        self.model: Optional[Any] = None

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(project_root / ".odino" / "chroma_db"),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.config["collection_name"]
        )

        # Defer model loading until embeddings are needed
        self.console.print("Preparing indexer...")

    def _is_mps_available(self) -> bool:
        """Check if MPS (Metal Performance Shaders) is available."""
        if not TORCH_AVAILABLE:
            return False
        try:
            return torch.backends.mps.is_available()
        except AttributeError:
            return False

    def _get_optimal_device(self) -> str:
        """Get the optimal device for model loading based on config and availability."""
        # Check if user has specified a device preference
        device_pref = self.config.get("device_preference", "auto")

        if device_pref != "auto":
            return device_pref

        # Auto-select best available device
        if not TORCH_AVAILABLE:
            return "cpu"
        try:
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        except AttributeError:
            return "cpu"

    def _fallback_to_cpu(self) -> None:
        """Fallback to CPU when MPS runs out of memory."""
        try:
            from sentence_transformers import SentenceTransformer

            self.console.print(
                "[yellow]Switching to CPU for memory efficiency...[/yellow]"
            )
            # Reload model on CPU
            self.model = SentenceTransformer(self.config["model_name"], device="cpu")

            # Clear MPS cache
            if TORCH_AVAILABLE and torch.backends.mps.is_available():
                torch.mps.empty_cache()

        except Exception as e:
            self.console.print(f"[red]Failed to fallback to CPU: {e}[/red]")
            raise

    def _switch_to_mps(self) -> None:
        """Switch back to MPS if available."""
        try:
            from sentence_transformers import SentenceTransformer

            if TORCH_AVAILABLE and torch.backends.mps.is_available():
                self.console.print("[yellow]Switching back to MPS...[/yellow]")
                self.model = SentenceTransformer(
                    self.config["model_name"], device="mps"
                )

        except Exception as e:
            self.console.print(f"[yellow]Could not switch back to MPS: {e}[/yellow]")
            # Stay on CPU if MPS switch fails

    def _load_model(self) -> None:
        """Load the embedding model lazily with user feedback and error handling."""
        if self.model is not None:
            return
        try:
            self.console.print(f"Loading embedding model: {self.config['model_name']}")
            # Import inside method to avoid heavy import at CLI startup
            from sentence_transformers import SentenceTransformer  # type: ignore

            # Get optimal device
            device = self._get_optimal_device()
            self.console.print(f"Using device: {device}")

            # Load model with device specification
            self.model = SentenceTransformer(self.config["model_name"], device=device)
            self.console.print("Model loaded successfully")
        except KeyboardInterrupt:
            # Allow user to cancel model load cleanly
            self.console.print("[red]Model loading cancelled by user[/red]")
            raise
        except Exception as e:
            self.console.print(f"[red]Failed to load embedding model: {e}[/red]")
            raise

    def discover_files(self, target_path: Path) -> List[Path]:
        """Discover all text files in the target directory."""
        files = []

        for file_path in target_path.rglob("*"):
            if file_path.is_file() and is_text_file(file_path):
                if not should_ignore_file(
                    file_path, self.project_root, self.ignore_patterns
                ):
                    files.append(file_path)

        return sorted(files)

    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def load_indexed_files(self) -> Dict[str, str]:
        """Load information about previously indexed files."""
        index_file = self.project_root / ".odino" / "indexed_files.json"

        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {}

    def save_indexed_files(self, indexed_files: Dict[str, str]) -> None:
        """Save information about indexed files."""
        index_file = self.project_root / ".odino" / "indexed_files.json"

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(indexed_files, f, indent=2)

    def process_file(self, file_path: Path) -> List[Dict[str, any]]:
        """Process a single file and return chunks with metadata."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                return []

            # Get relative path from project root
            relative_path = file_path.relative_to(self.project_root)

            # Chunk the content
            chunks = chunk_text(
                content,
                chunk_size=self.config["chunk_size"],
                overlap=self.config["chunk_overlap"],
            )

            # Add metadata to chunks
            for chunk in chunks:
                chunk["file_path"] = str(relative_path)
                chunk["file_size"] = file_path.stat().st_size
                chunk["modified_time"] = file_path.stat().st_mtime

            return chunks

        except Exception as e:
            self.console.print(f"[red]Error processing {file_path}: {e}[/red]")
            return []

    def index_files(
        self,
        target_path: Path,
        force: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, float]:
        """Index all files in the target directory and return stats."""
        # Ensure .odino directory exists
        odino_dir = self.project_root / ".odino"
        odino_dir.mkdir(exist_ok=True)

        # Discover files
        self.console.print("Discovering files...")
        if progress_callback:
            progress_callback("Discovering files...")
        files = self.discover_files(target_path)

        if not files:
            self.console.print("[yellow]No text files found to index.[/yellow]")
            return {"files_indexed": 0, "chunks_created": 0, "total_size_mb": 0.0}

        self.console.print(f"Found {len(files)} text files")
        if progress_callback:
            progress_callback(f"Found {len(files)} text files")

        # Load previously indexed files
        indexed_files = self.load_indexed_files()

        # Filter files that need indexing
        files_to_index = []
        if force:
            files_to_index = files
        else:
            for file_path in files:
                relative_path = str(file_path.relative_to(self.project_root))
                current_hash = self.get_file_hash(file_path)

                if (
                    relative_path not in indexed_files
                    or indexed_files[relative_path] != current_hash
                ):
                    files_to_index.append(file_path)

        if not files_to_index:
            self.console.print("[green]All files are up to date![/green]")
            return {"files_indexed": 0, "chunks_created": 0, "total_size_mb": 0.0}

        self.console.print(f"Indexing {len(files_to_index)} files...")
        if progress_callback:
            progress_callback(f"Indexing {len(files_to_index)} files...")

        # Process files with progress bar
        all_chunks = []
        total_size = 0

        with Progress() as progress:
            task = progress.add_task("Processing files...", total=len(files_to_index))

            for file_path in files_to_index:
                chunks = self.process_file(file_path)
                all_chunks.extend(chunks)
                total_size += file_path.stat().st_size

                progress.update(task, advance=1)
                if progress_callback:
                    progress_callback(f"Processed {file_path}")

        if not all_chunks:
            self.console.print("[yellow]No content to index.[/yellow]")
            return {"files_indexed": 0, "chunks_created": 0, "total_size_mb": 0.0}

        self.console.print(
            f"Generated {len(all_chunks)} chunks from {len(files_to_index)} files"
        )
        self.console.print(f"Total size: {format_file_size(total_size)}")
        if progress_callback:
            progress_callback("Generating embeddings...")

        # Generate embeddings with memory management and batch processing
        self.console.print("Generating embeddings...")
        # Ensure model is loaded lazily right before use
        self._load_model()

        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = []

        # Use configurable batch size, default to smaller size for MPS to avoid memory issues
        batch_size = self.config.get(
            "embedding_batch_size", 32 if self._is_mps_available() else 1000
        )

        try:
            self.console.print(f"Generating embeddings in batches of {batch_size}...")

            # Process embeddings in batches to reduce memory usage
            for i in tqdm(range(0, len(texts), batch_size)):
                batch_end = min(i + batch_size, len(texts))
                batch_texts = texts[i:batch_end]

                try:
                    batch_embeddings = self.model.encode(
                        batch_texts, show_progress_bar=False
                    )
                    embeddings.extend(batch_embeddings)

                    # Clear memory after each batch on MPS
                    if self._is_mps_available() and TORCH_AVAILABLE:
                        torch.mps.empty_cache()

                except RuntimeError as e:
                    if "out of memory" in str(e).lower() or "MPS" in str(e):
                        self.console.print(
                            f"[yellow]MPS memory error in batch {i//batch_size + 1}, falling back to CPU...[/yellow]"
                        )
                        # Fallback to CPU for this batch
                        self._fallback_to_cpu()
                        batch_embeddings = self.model.encode(
                            batch_texts, show_progress_bar=False
                        )
                        embeddings.extend(batch_embeddings)
                        # Switch back to MPS if available
                        self._switch_to_mps()
                    else:
                        raise

            # Convert to tensor format expected by downstream code
            if len(embeddings) > 0:
                import numpy as np

                embeddings = np.array(embeddings)

        except KeyboardInterrupt:
            self.console.print("[red]Embedding generation cancelled by user[/red]")
            raise
        except Exception as e:
            self.console.print(f"[red]Failed to generate embeddings: {e}[/red]")
            return {"files_indexed": 0, "chunks_created": 0, "total_size_mb": 0.0}

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(all_chunks):
            chunk_id = f"{chunk['file_path']}:{chunk.get('chunk_id', 0)}"
            ids.append(chunk_id)
            documents.append(chunk["text"])

            metadata = {
                "file_path": chunk["file_path"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "file_size": chunk["file_size"],
                "modified_time": chunk["modified_time"],
            }
            metadatas.append(metadata)

        # Store in ChromaDB
        self.console.print("Storing embeddings...")
        if progress_callback:
            progress_callback("Storing embeddings...")

        # Delete existing embeddings for files being reindexed
        if force:
            # Clear all existing data
            self.chroma_client.delete_collection(name=self.config["collection_name"])
            self.collection = self.chroma_client.create_collection(
                name=self.config["collection_name"]
            )

        # Add new embeddings in batches
        batch_size = 1000
        for i in tqdm(range(0, len(ids), batch_size)):
            batch_end = min(i + batch_size, len(ids))

            self.collection.add(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                embeddings=embeddings[i:batch_end].tolist(),
                metadatas=metadatas[i:batch_end],
            )

        # Update indexed files tracking
        for file_path in files_to_index:
            relative_path = str(file_path.relative_to(self.project_root))
            indexed_files[relative_path] = self.get_file_hash(file_path)

        self.save_indexed_files(indexed_files)

        self.console.print(
            f"[green]Successfully indexed {len(files_to_index)} files![/green]"
        )
        self.console.print(f"[green]Total chunks: {len(all_chunks)}[/green]")
        if progress_callback:
            progress_callback("Indexing complete")

        return {
            "files_indexed": float(len(files_to_index)),
            "chunks_created": float(len(all_chunks)),
            "total_size_mb": float(total_size) / (1024.0 * 1024.0),
        }

    def index(
        self,
        force: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, float]:
        """Convenience method to index the project root."""
        return self.index_files(
            self.project_root, force=force, progress_callback=progress_callback
        )
