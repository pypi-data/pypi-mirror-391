"""File system utilities for directory scanning, gitignore, and file operations."""

from pathlib import Path
from typing import Optional, List, Dict
import os
import stat

try:
    from pathspec import PathSpec
    from pathspec.patterns.gitwildmatch import GitWildMatchPattern

    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False

# Cache for gitignore specs to avoid rebuilding
_gitignore_cache: Dict[Path, Optional[PathSpec]] = {}


def find_gitignore_files(start_path: Path) -> List[Path]:
    """Find all .gitignore files from start_path up to root."""
    gitignore_files = []
    current = start_path.resolve()

    while current != current.parent:
        gitignore_path = current / ".gitignore"
        if gitignore_path.exists():
            gitignore_files.append(gitignore_path)
        current = current.parent

    return gitignore_files


def parse_gitignore(gitignore_path: Path) -> List[str]:
    """Parse a .gitignore file and return list of patterns."""
    patterns = []
    try:
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    except (OSError, PermissionError):
        pass
    return patterns


def build_gitignore_spec(start_path: Path) -> Optional[PathSpec]:
    """Build a PathSpec from all .gitignore files with caching."""
    if not HAS_PATHSPEC:
        return None

    # Check cache first
    resolved_path = start_path.resolve()
    if resolved_path in _gitignore_cache:
        return _gitignore_cache[resolved_path]

    gitignore_files = find_gitignore_files(resolved_path)
    if not gitignore_files:
        _gitignore_cache[resolved_path] = None
        return None

    all_patterns = []
    for gitignore_file in gitignore_files:
        patterns = parse_gitignore(gitignore_file)
        # Make patterns relative to the gitignore file's directory
        gitignore_dir = gitignore_file.parent
        for pattern in patterns:
            # Convert to absolute pattern if needed
            if pattern.startswith("/"):
                pattern = str(gitignore_dir / pattern[1:])
            else:
                pattern = str(gitignore_dir / pattern)
            all_patterns.append(pattern)

    try:
        spec = PathSpec.from_lines(GitWildMatchPattern, all_patterns)
        _gitignore_cache[resolved_path] = spec
        return spec
    except Exception:
        _gitignore_cache[resolved_path] = None
        return None


def is_executable(path: Path) -> bool:
    """Check if a file is executable."""
    try:
        return os.access(path, os.X_OK) or (path.stat().st_mode & stat.S_IEXEC) != 0
    except (OSError, PermissionError):
        return False


def get_file_icon(path: Path) -> str:
    """Get an icon for a file based on its extension or type."""
    if path.is_dir():
        return "📁"
    if path.is_symlink():
        return "🔗"

    suffix = path.suffix.lower()
    icon_map = {
        ".py": "🐍",
        ".js": "📜",
        ".ts": "📘",
        ".html": "🌐",
        ".css": "🎨",
        ".json": "📋",
        ".xml": "📄",
        ".yaml": "⚙️",
        ".yml": "⚙️",
        ".md": "📝",
        ".txt": "📄",
        ".sh": "💻",
        ".bash": "💻",
        ".zsh": "💻",
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".png": "🖼️",
        ".gif": "🖼️",
        ".svg": "🖼️",
        ".pdf": "📕",
        ".zip": "📦",
        ".tar": "📦",
        ".gz": "📦",
        ".mp3": "🎵",
        ".mp4": "🎬",
        ".avi": "🎬",
        ".mov": "🎬",
    }

    if suffix in icon_map:
        return icon_map[suffix]

    if is_executable(path):
        return "⚡"

    return "📄"


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    size: float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


def get_disk_usage(path: Path) -> int:
    """Get disk usage of a path in bytes using optimized os.walk."""
    try:
        if path.is_file():
            return path.stat().st_size

        # Use os.walk which is much faster than rglob
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            # Filter out inaccessible directories
            dirnames[:] = [d for d in dirnames if os.access(os.path.join(dirpath, d), os.R_OK)]
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except (OSError, PermissionError):
                    continue
        return total
    except (OSError, PermissionError):
        return 0
