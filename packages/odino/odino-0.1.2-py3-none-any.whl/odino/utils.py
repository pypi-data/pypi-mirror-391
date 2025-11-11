"""Utility functions for Odino semantic search CLI."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import pathspec


DEFAULT_CONFIG = {
    "model_name": "EmmanuelEA/eea-embedding-gemma",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "max_results": 2,
    "collection_name": "odino",
    "embedding_batch_size": 32,  # Smaller batch size for MPS memory efficiency
    "device_preference": "auto",  # auto, cpu, cuda, mps
    "exclude_patterns": [
        ".git",
        ".svn",
        ".hg",
        ".odino",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
        "Thumbs.db",
        "*.egg-info",
        "dist",
        "build",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".env",
        "*.lock",
        "*.log",
        ".gitignore",
        ".odinoignore",
    ],
}


def get_odino_dir(path: Path) -> Path:
    """Get the .odino directory for a given path."""
    return path / ".odino"


def get_config_path(path: Path) -> Path:
    """Get the config file path for a given directory."""
    return get_odino_dir(path) / "config.json"


def load_config(path: Path) -> Dict:
    """Load configuration from .odino/config.json."""
    config_path = get_config_path(path)
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(path: Path, config: Dict) -> None:
    """Save configuration to .odino/config.json."""
    odino_dir = get_odino_dir(path)
    odino_dir.mkdir(exist_ok=True)
    config_path = get_config_path(path)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def load_ignore_patterns(path: Path) -> pathspec.PathSpec:
    """Load ignore patterns from .odinoignore and .gitignore files and merge defaults."""
    patterns: List[str] = []

    # Load from .odinoignore
    odinoignore_file = path / ".odinoignore"
    if odinoignore_file.exists():
        try:
            with open(odinoignore_file, "r", encoding="utf-8") as f:
                patterns.extend(
                    [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                )
        except IOError:
            pass

    # Load from .gitignore
    gitignore_file = path / ".gitignore"
    if gitignore_file.exists():
        try:
            with open(gitignore_file, "r", encoding="utf-8") as f:
                patterns.extend(
                    [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                )
        except IOError:
            pass

    # Add default patterns
    patterns.extend(DEFAULT_CONFIG["exclude_patterns"])

    # Remove duplicates while preserving order
    unique_patterns = []
    seen = set()
    for p in patterns:
        if p not in seen:
            unique_patterns.append(p)
            seen.add(p)

    return pathspec.PathSpec.from_lines("gitwildmatch", unique_patterns)


def should_ignore_file(file_path: Path, root: Path, spec: pathspec.PathSpec) -> bool:
    """Return True if the file should be ignored based on the compiled spec."""
    try:
        rel = file_path.relative_to(root).as_posix()
        return spec.match_file(rel)
    except ValueError:
        # If file_path not under root, don't ignore
        return False
    except Exception:
        return False


def is_text_file(file_path: Path) -> bool:
    """Heuristic to check if a file is text."""
    ext = file_path.suffix.lower()
    text_exts = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".json",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".html",
        ".css",
        ".sql",
        ".xml",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".java",
        ".c",
        ".h",
        ".hpp",
        ".cpp",
        ".rs",
        ".go",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
        ".r",
        ".pl",
        ".lua",
        ".dart",
    }
    if ext in text_exts:
        return True
    binary_exts = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".tiff",
        ".ico",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".rar",
        ".7z",
        ".mp3",
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
    }
    if ext in binary_exts:
        return False
    try:
        with open(file_path, "rb") as f:
            sample = f.read(4096)
        if b"\x00" in sample:
            return False
        sample.decode("utf-8")
        return True
    except Exception:
        return False


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[Dict]:
    """Split text into overlapping chunks and return metadata.

    Returns list of dicts with keys: text, start_line, end_line, chunk_id.
    """
    if chunk_size <= 0:
        chunk_size = 256
    if overlap < 0:
        overlap = 0
    lines = text.splitlines()
    chunks: List[Dict] = []
    start = 0
    chunk_id = 0
    while start < len(lines):
        end = min(start + max(1, chunk_size // 4), len(lines))  # approx by lines
        chunk_text_str = "\n".join(lines[start:end])
        chunks.append(
            {
                "text": chunk_text_str,
                "start_line": start + 1,
                "end_line": end,
                "chunk_id": chunk_id,
            }
        )
        if end == len(lines):
            break
        start = max(0, end - max(0, overlap // 4))
        chunk_id += 1
    return chunks


def format_file_size(size_bytes: int) -> str:
    """Human readable file size."""
    try:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        kb = size_bytes / 1024.0
        if kb < 1024:
            return f"{kb:.1f} KB"
        mb = kb / 1024.0
        if mb < 1024:
            return f"{mb:.1f} MB"
        gb = mb / 1024.0
        return f"{gb:.1f} GB"
    except Exception:
        return str(size_bytes)
