"""Custom tree widget for displaying directory structure."""

from pathlib import Path
from typing import Optional, List
from textual.widget import Widget
from textual.geometry import Size
from textual.containers import ScrollableContainer
from textual.app import ComposeResult
from rich.console import RenderableType
from rich.text import Text

from .file_node import FileNode
from .file_utils import get_file_icon, format_size, is_executable


class TreeContent(Widget):
    """Content widget that renders the tree structure."""

    # Enable vertical scrolling for this widget
    can_focus = True

    # Add virtual size to enable proper scrolling
    DEFAULT_CSS = """
    TreeContent {
        height: auto;
        width: 100%;
    }
    """

    def __init__(
        self,
        root_node: FileNode,
        *,
        show_hidden: bool = False,
        show_permissions: bool = False,
        show_disk_usage: bool = False,
        gitignore_spec=None,
        selected_index: int = 0,
        name: Optional[str] = None,
    ):
        super().__init__(name=name)
        self.root_node = root_node
        self.show_hidden = show_hidden
        self.show_permissions = show_permissions
        self.show_disk_usage = show_disk_usage
        self.gitignore_spec = gitignore_spec
        self.selected_index = selected_index
        self.flat_nodes: List[FileNode] = []
        self.flat_ancestors: List[List[bool]] = []
        self._rebuild_flat_list()

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Return the height of the content."""
        # Return the total number of lines needed to display all nodes
        return max(len(self.flat_nodes), 1)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Return the width of the content."""
        # Use full container width
        return container.width

    def _rebuild_flat_list(self):
        """Rebuild the flat list of visible nodes."""
        self.flat_nodes = []
        self.flat_ancestors = []
        self._add_node_to_flat_list(self.root_node, [])

        # Update virtual size to reflect the new content height
        # This tells the parent ScrollableContainer how much content there is
        num_lines = max(len(self.flat_nodes), 1)
        # Set virtual size - the height is critical for vertical scrolling
        self.virtual_size = Size(self.size.width, num_lines)

        # Force a size update to notify parent container
        self.refresh(layout=True)

    def _add_node_to_flat_list(self, node: FileNode, ancestors: List[bool]):
        """Recursively add nodes to flat list with tree structure info."""
        self.flat_nodes.append(node)
        self.flat_ancestors.append(ancestors.copy())

        if node.is_dir and node.expanded:
            children = node.load_children(self.show_hidden, self.gitignore_spec)
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                self._add_node_to_flat_list(child, ancestors + [is_last])

    def _get_tree_prefix(self, ancestors: List[bool]) -> str:
        """Generate tree prefix string (├──, └──, │)."""
        if not ancestors:
            return ""

        prefix = ""
        for is_last in ancestors[:-1]:
            if is_last:
                prefix += "    "
            else:
                prefix += "│   "

        if ancestors:
            if ancestors[-1]:
                prefix += "└── "
            else:
                prefix += "├── "

        return prefix

    def render(self) -> RenderableType:
        """Render the entire tree."""
        if not self.flat_nodes:
            return Text("No items to display", style="dim")

        lines = []
        for i, (node, ancestors) in enumerate(
            zip(self.flat_nodes, self.flat_ancestors)
        ):
            prefix = self._get_tree_prefix(ancestors)
            icon = get_file_icon(node.path)
            name = node.name

            # Add symlink target
            if node.is_symlink:
                target = node.get_symlink_target()
                if target:
                    name += f" -> {target}"

            # Add expand/collapse indicator and count for directories
            if node.is_dir:
                # Get direct child count
                count = node.get_direct_child_count(
                    self.show_hidden, self.gitignore_spec
                )

                # Add indicator
                if node.expanded:
                    indicator = "[-]"
                else:
                    indicator = "[+]"

                # Add count in parentheses after directory name
                name = f"{indicator} {name} ({count})"

            # Add permissions and size if enabled
            suffix = ""
            if self.show_permissions:
                perms = node.get_permissions()
                suffix += f" {perms}"
            if self.show_disk_usage and node.is_file:
                size = format_size(node.get_size())
                suffix += f" {size}"

            # Build the line
            line_text = f"{prefix}{icon} {name}{suffix}"

            # Apply styling based on node type and selection
            if i == self.selected_index:
                # Selected item - highlight background
                style = "reverse"
            elif node.is_dir:
                style = "bold cyan"
            elif node.is_symlink:
                style = "magenta"
            elif is_executable(node.path):
                style = "green"
            else:
                style = ""

            text = Text(line_text, style=style)
            lines.append(text)

        # Combine all lines
        result = Text()
        for i, line in enumerate(lines):
            result.append(line)
            if i < len(lines) - 1:
                result.append("\n")

        return result

    def get_selected_node(self) -> Optional[FileNode]:
        """Get the currently selected node."""
        if 0 <= self.selected_index < len(self.flat_nodes):
            return self.flat_nodes[self.selected_index]
        return None

    def get_line_count(self) -> int:
        """Get the number of lines in the tree."""
        return len(self.flat_nodes)


class TreeWidget(ScrollableContainer):
    """Widget that displays a directory tree structure with scrolling."""

    def __init__(
        self,
        root_node: FileNode,
        *,
        show_hidden: bool = False,
        show_permissions: bool = False,
        show_disk_usage: bool = False,
        gitignore_spec=None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.root_node = root_node
        self.show_hidden = show_hidden
        self.show_permissions = show_permissions
        self.show_disk_usage = show_disk_usage
        self.gitignore_spec = gitignore_spec
        self.selected_index = 0
        self._content: Optional[TreeContent] = None

    def compose(self) -> ComposeResult:
        """Compose the tree widget with its content."""
        self._content = TreeContent(
            self.root_node,
            show_hidden=self.show_hidden,
            show_permissions=self.show_permissions,
            show_disk_usage=self.show_disk_usage,
            gitignore_spec=self.gitignore_spec,
            selected_index=self.selected_index,
        )
        yield self._content

    def get_selected_node(self) -> Optional[FileNode]:
        """Get the currently selected node."""
        if self._content:
            return self._content.get_selected_node()
        return None

    def move_selection(self, direction: int):
        """Move selection up or down."""
        if not self._content:
            return

        old_index = self.selected_index
        if direction < 0:
            self.selected_index = max(0, self.selected_index - 1)
        else:
            line_count = self._content.get_line_count()
            self.selected_index = min(line_count - 1, self.selected_index + 1)

        # Only update if selection changed
        if old_index != self.selected_index:
            self._content.selected_index = self.selected_index
            self._content.refresh()
            self._ensure_selection_visible()

    def _ensure_selection_visible(self):
        """Ensure the selected item is visible in the viewport."""
        if not self._content:
            return

        # Get viewport dimensions
        viewport_height = self.size.height
        if viewport_height <= 0:
            return

        # Calculate the selected line position
        selected_y = self.selected_index
        current_scroll_y = int(self.scroll_y)

        # Add some padding to make scrolling more comfortable
        padding = 2

        # Check if selected item is above the visible area
        if selected_y < current_scroll_y + padding:
            # Scroll up to show the selected item near the top
            new_scroll_y = max(0, selected_y - padding)
            self.scroll_to(y=new_scroll_y, animate=False, force=True)

        # Check if selected item is below the visible area
        elif selected_y >= current_scroll_y + viewport_height - padding:
            # Scroll down to show the selected item near the bottom
            new_scroll_y = selected_y - viewport_height + padding + 1
            self.scroll_to(y=max(0, new_scroll_y), animate=False, force=True)

    def toggle_expand(self):
        """Toggle expand/collapse of selected directory."""
        if not self._content:
            return
        node = self.get_selected_node()
        if node and node.is_dir:
            node.expanded = not node.expanded
            if node.expanded:
                node.load_children(self.show_hidden, self.gitignore_spec)
            self._content._rebuild_flat_list()
            # Single refresh call instead of multiple
            self._content.refresh()
            self._ensure_selection_visible()

    def expand_selected(self):
        """Expand selected directory."""
        if not self._content:
            return
        node = self.get_selected_node()
        if node and node.is_dir and not node.expanded:
            node.expanded = True
            node.load_children(self.show_hidden, self.gitignore_spec)
            self._content._rebuild_flat_list()
            self._content.refresh()
            self._ensure_selection_visible()

    def collapse_selected(self):
        """Collapse selected directory."""
        if not self._content:
            return
        node = self.get_selected_node()
        if node and node.is_dir and node.expanded:
            node.expanded = False
            self._content._rebuild_flat_list()
            self._content.refresh()
            self._ensure_selection_visible()

    def expand_all_subdirectories(self):
        """Expand all subdirectories of selected node."""
        if not self._content:
            return
        node = self.get_selected_node()
        if node and node.is_dir:
            node.expand_all(self.show_hidden, self.gitignore_spec)
            self._content._rebuild_flat_list()
            self._content.refresh()
            self._ensure_selection_visible()

    def collapse_all_subdirectories(self):
        """Collapse all subdirectories of selected node."""
        if not self._content:
            return
        node = self.get_selected_node()
        if node and node.is_dir:
            node.collapse_all()
            self._content._rebuild_flat_list()
            self._content.refresh()
            self._ensure_selection_visible()

    def toggle_expand_all_subdirectories(self):
        """Toggle between expanding and collapsing all subdirectories of selected node."""
        if not self._content:
            return
        node = self.get_selected_node()
        if node and node.is_dir:
            # Check if node has any collapsed children
            if self._has_collapsed_children(node):
                # Expand all if any children are collapsed
                node.expand_all(self.show_hidden, self.gitignore_spec)
            else:
                # Collapse all if everything is expanded
                node.collapse_all()
            self._content._rebuild_flat_list()
            self._content.refresh()
            self._ensure_selection_visible()

    def _has_collapsed_children(self, node: FileNode) -> bool:
        """Check if a node has any collapsed directory children (recursively)."""
        if not node.is_dir:
            return False
        
        # If node itself is not expanded, it has collapsed children
        if not node.expanded:
            return True
        
        # Check children recursively
        for child in node.children:
            if child.is_dir:
                if not child.expanded or self._has_collapsed_children(child):
                    return True
        
        return False

    def update_settings(
        self,
        show_hidden: Optional[bool] = None,
        show_permissions: Optional[bool] = None,
        show_disk_usage: Optional[bool] = None,
        gitignore_spec=None,
    ):
        """Update display settings and rebuild tree efficiently."""
        if not self._content:
            return
        
        settings_changed = False
        
        if show_hidden is not None and self.show_hidden != show_hidden:
            self.show_hidden = show_hidden
            self._content.show_hidden = show_hidden
            settings_changed = True
            
        if show_permissions is not None and self.show_permissions != show_permissions:
            self.show_permissions = show_permissions
            self._content.show_permissions = show_permissions
            settings_changed = True
            
        if show_disk_usage is not None and self.show_disk_usage != show_disk_usage:
            self.show_disk_usage = show_disk_usage
            self._content.show_disk_usage = show_disk_usage
            settings_changed = True
            
        if gitignore_spec is not None and self.gitignore_spec != gitignore_spec:
            self.gitignore_spec = gitignore_spec
            self._content.gitignore_spec = gitignore_spec
            settings_changed = True

        # Only rebuild if settings actually changed
        if not settings_changed:
            return

        # Rebuild the list (this also updates virtual_size)
        self._content._rebuild_flat_list()

        # Ensure selected index is still valid
        line_count = self._content.get_line_count()
        if line_count > 0:
            self.selected_index = min(self.selected_index, line_count - 1)
            self._content.selected_index = self.selected_index

        # Single refresh with layout update
        self._content.refresh()
        self._ensure_selection_visible()

    def select_node_by_path(self, target_path: Path) -> None:
        """Select a node by its path."""
        if not self._content:
            return

        # Find the node in the flat list
        for i, node in enumerate(self._content.flat_nodes):
            if node.path == target_path:
                self.selected_index = i
                self._content.selected_index = i
                self._ensure_selection_visible()
                return

    def filter_nodes(self, search_term: str):
        """Filter nodes based on search term with optimized iteration."""
        if not self._content:
            return
        if not search_term:
            self._content._rebuild_flat_list()
            self._content.refresh()
            return

        search_lower = search_term.lower()
        matching_nodes = []

        def collect_matching(node: FileNode, ancestors: List[bool]):
            # Check if current node matches
            is_match = search_lower in node.name.lower()
            if is_match:
                matching_nodes.append((node, ancestors))
            
            # Only traverse directories
            if node.is_dir:
                children = node.load_children(self.show_hidden, self.gitignore_spec)
                # Pre-calculate is_last values to avoid repeated index() calls
                for i, child in enumerate(children):
                    is_last = (i == len(children) - 1)
                    collect_matching(child, ancestors + [is_last])

        collect_matching(self.root_node, [])

        # Batch expand all ancestor paths for matched nodes
        # Use a set to avoid redundant expansions
        nodes_to_expand = set()
        for node, _ in matching_nodes:
            current = node.parent
            while current and current != self.root_node:
                if current not in nodes_to_expand:
                    nodes_to_expand.add(current)
                    current.expanded = True
                    current.load_children(self.show_hidden, self.gitignore_spec)
                current = current.parent

        self._content._rebuild_flat_list()
        self._content.refresh()
        self._ensure_selection_visible()
