"""File node data structure for representing files and directories."""

from pathlib import Path
from typing import Optional, List
import stat
import os


class FileNode:
    """Represents a file or directory in the tree structure."""

    def __init__(self, path: Path, parent: Optional["FileNode"] = None):
        self.path = path
        self.parent = parent
        self.name = path.name
        self._children: Optional[List["FileNode"]] = None
        self.expanded = False
        self._loaded = False
        self._item_count: Optional[int] = None
        self._size_cache: Optional[int] = None
        self._permissions_cache: Optional[str] = None

    @property
    def is_dir(self) -> bool:
        """Check if this node is a directory."""
        return self.path.is_dir()

    @property
    def is_file(self) -> bool:
        """Check if this node is a file."""
        return self.path.is_file()

    @property
    def is_symlink(self) -> bool:
        """Check if this node is a symlink."""
        return self.path.is_symlink()

    @property
    def children(self) -> List["FileNode"]:
        """Get children nodes, loading them if necessary."""
        if self._children is None:
            self._children = []
        return self._children

    @property
    def has_children(self) -> bool:
        """Check if this node has children (without loading them)."""
        if not self.is_dir:
            return False
        if self._children is not None:
            return len(self._children) > 0
        # Check if directory has any contents without loading
        try:
            return any(True for _ in self.path.iterdir())
        except (PermissionError, OSError):
            return False

    def load_children(
        self,
        show_hidden: bool = False,
        gitignore_spec=None,
    ) -> List["FileNode"]:
        """Load children nodes from filesystem using fast os.scandir."""
        if not self.is_dir or self._loaded:
            return self.children

        try:
            # Use os.scandir which is significantly faster than iterdir()
            with os.scandir(self.path) as entries:
                # Collect entries first to sort them
                dirs = []
                files = []
                
                for entry in entries:
                    # Skip hidden files if not showing them
                    if not show_hidden and entry.name.startswith("."):
                        continue

                    # Check gitignore patterns
                    if gitignore_spec:
                        try:
                            if gitignore_spec.match_file(entry.path):
                                continue
                        except Exception:
                            pass  # Ignore gitignore errors

                    # Separate dirs and files for sorting
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            dirs.append(entry)
                        else:
                            files.append(entry)
                    except OSError:
                        # If we can't determine type, treat as file
                        files.append(entry)

            # Sort directories and files separately, then combine
            dirs.sort(key=lambda e: e.name.lower())
            files.sort(key=lambda e: e.name.lower())
            
            self._children = []
            for entry in dirs + files:
                node = FileNode(Path(entry.path), parent=self)
                self._children.append(node)

            self._loaded = True
        except (PermissionError, OSError):
            self._children = []
            self._loaded = True

        return self.children

    def get_direct_child_count(
        self, show_hidden: bool = False, gitignore_spec=None
    ) -> int:
        """Get count of direct children in this directory (non-recursive)."""
        if not self.is_dir:
            return 0

        # If children are already loaded, return their count
        if self._loaded and self._children is not None:
            return len(self._children)

        # Use fast os.scandir for counting (significantly faster than iterdir)
        count = 0
        try:
            with os.scandir(self.path) as entries:
                for entry in entries:
                    # Skip hidden files if not showing them
                    if not show_hidden and entry.name.startswith("."):
                        continue

                    # Check gitignore patterns
                    if gitignore_spec:
                        try:
                            if gitignore_spec.match_file(entry.path):
                                continue
                        except Exception:
                            pass

                    count += 1
        except (PermissionError, OSError):
            return 0

        return count

    def get_item_count(self) -> int:
        """Get total item count for this directory (including subdirectories)."""
        if not self.is_dir:
            return 0

        if self._item_count is not None:
            return self._item_count

        # Use os.walk which is faster than rglob for counting
        count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(self.path):
                # Filter out inaccessible directories
                dirnames[:] = [d for d in dirnames if os.access(os.path.join(dirpath, d), os.R_OK)]
                count += len(dirnames) + len(filenames)
            self._item_count = count
        except (PermissionError, OSError):
            self._item_count = 0

        return self._item_count or 0

    def get_size(self) -> int:
        """Get file size in bytes with caching."""
        if self._size_cache is not None:
            return self._size_cache

        try:
            if self.is_dir:
                # Use os.walk which is faster than rglob for large directories
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(self.path):
                    # Filter out permission errors gracefully
                    dirnames[:] = [d for d in dirnames if os.access(os.path.join(dirpath, d), os.R_OK)]
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                        except (OSError, PermissionError):
                            continue
                self._size_cache = total_size
                return total_size
            else:
                size = self.path.stat().st_size
                self._size_cache = size
                return size
        except (PermissionError, OSError):
            self._size_cache = 0
            return 0

    def get_permissions(self) -> str:
        """Get file permissions as string (e.g., 'rwxr-xr-x') with caching."""
        if self._permissions_cache is not None:
            return self._permissions_cache

        try:
            mode = self.path.stat().st_mode
            perms = []
            for who in "USR", "GRP", "OTH":
                for perm in "R", "W", "X":
                    if mode & getattr(stat, f"S_I{perm}{who}"):
                        perms.append(perm.lower())
                    else:
                        perms.append("-")
            result = "".join(perms)
            self._permissions_cache = result
            return result
        except (PermissionError, OSError):
            self._permissions_cache = "---------"
            return "---------"

    def get_symlink_target(self) -> Optional[str]:
        """Get symlink target if this is a symlink."""
        if self.is_symlink:
            try:
                return str(self.path.readlink())
            except (OSError, PermissionError):
                return None
        return None

    def expand_all(self, show_hidden: bool = False, gitignore_spec=None):
        """Recursively expand all subdirectories."""
        if not self.is_dir:
            return

        self.expanded = True
        self.load_children(show_hidden, gitignore_spec)

        for child in self.children:
            if child.is_dir:
                child.expand_all(show_hidden, gitignore_spec)

    def collapse_all(self):
        """Recursively collapse all subdirectories."""
        self.expanded = False
        for child in self.children:
            if child.is_dir:
                child.collapse_all()

    def find_node_by_path(self, target_path: Path) -> Optional["FileNode"]:
        """Find a node by its path in the tree."""
        if self.path == target_path:
            return self

        for child in self.children:
            result = child.find_node_by_path(target_path)
            if result:
                return result

        return None
