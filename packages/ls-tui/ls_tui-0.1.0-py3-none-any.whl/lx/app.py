"""Main Textual application for lx directory explorer."""

import os
import shutil
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Input, Static
from textual.binding import Binding

from .file_node import FileNode
from .file_utils import build_gitignore_spec
from .tree_widget import TreeWidget

if TYPE_CHECKING:
    from pathspec import PathSpec


class LxApp(App):
    """Main application class for lx directory explorer."""

    TITLE = "lx - Directory Tree Explorer"
    CSS_PATH = os.path.join(os.path.dirname(__file__), "styles.tcss")

    BINDINGS = [
        Binding("up", "move_up", "Move Up", priority=True),
        Binding("down", "move_down", "Move Down", priority=True),
        Binding("space", "toggle_expand", "Toggle Expand/Collapse", priority=True),
        Binding("right", "navigate_into", "Navigate Into Directory", priority=True),
        Binding("left", "navigate_up", "Go to Parent Directory", priority=True),
        Binding(
            "enter", "navigate_and_quit", "Navigate to Selected & Quit", priority=True
        ),
        Binding("tab", "toggle_expand_all", "Toggle Expand/Collapse All", priority=True),
        Binding("shift+tab", "collapse_all", "Collapse All", priority=True),
        Binding("a", "toggle_hidden", "Toggle Hidden", priority=True),
        Binding("s", "toggle_permissions", "Toggle Permissions", priority=True),
        Binding("g", "toggle_gitignore", "Toggle Gitignore", priority=True),
        Binding("d", "toggle_disk_usage", "Toggle Disk Usage", priority=True),
        Binding("/", "search", "Search", priority=True),
        Binding("delete", "delete_item", "Delete", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "quit", "Quit", priority=True),
    ]

    def __init__(self, path: Optional[Path] = None):
        super().__init__()
        self.start_path = path or Path.cwd()
        self.current_path = self.start_path  # Track current directory
        self.show_hidden = False
        self.show_permissions = False
        self.show_disk_usage = False
        self.use_gitignore = False
        self.gitignore_spec: Optional["PathSpec"] = None
        self.search_mode = False
        self.confirmation_mode = False  # Whether we're showing a delete confirmation
        self.pending_delete_node: Optional[FileNode] = None  # Node pending deletion
        self.tree_widget: Optional[TreeWidget] = None
        self.exit_path: Optional[Path] = None  # Path to navigate to on exit
        self._tree_counter = 0  # Counter for unique tree widget IDs

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Container(id="main-container"):
            yield Static("", id="status-bar")
            self._tree_counter += 1
            yield TreeWidget(
                FileNode(self.start_path),
                show_hidden=self.show_hidden,
                show_permissions=self.show_permissions,
                show_disk_usage=self.show_disk_usage,
                gitignore_spec=self.gitignore_spec,
                id=f"tree-{self._tree_counter}",
            )
            yield Input(placeholder="Search...", id="search-input", classes="hidden")

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.tree_widget = self.query_one(TreeWidget)
        root_node = self.tree_widget.root_node
        # Initially expand first level
        if root_node.is_dir:
            root_node.expanded = True
            root_node.load_children(self.show_hidden, self.gitignore_spec)
            if self.tree_widget._content:
                self.tree_widget._content._rebuild_flat_list()
            self.tree_widget.refresh()

        # Update gitignore if enabled
        if self.use_gitignore:
            self._update_gitignore()

        self._update_status_bar()

    def _update_gitignore(self) -> None:
        """Update gitignore patterns."""
        if self.use_gitignore:
            spec = build_gitignore_spec(self.start_path)
            self.gitignore_spec = spec
        else:
            self.gitignore_spec = None

        if self.tree_widget:
            self.tree_widget.update_settings(gitignore_spec=self.gitignore_spec)

    def _update_status_bar(self) -> None:
        """Update the status bar with current settings."""
        status_bar = self.query_one("#status-bar", Static)

        # Show confirmation message if in confirmation mode
        if self.confirmation_mode and self.pending_delete_node:
            node = self.pending_delete_node
            item_type = "directory" if node.is_dir else "file"

            # For directories, show a simple confirmation without expensive counting
            # to avoid blocking the UI with slow filesystem operations
            if node.is_dir:
                status_text = f"Delete directory {node.path.name} and all its contents? [y/n]"
            else:
                status_text = f"Delete {item_type} {node.path.name}? [y/n]"

            status_bar.update(status_text)
            return

        # Normal status bar display
        status_parts = []
        if self.show_hidden:
            status_parts.append("Hidden: ON")
        if self.show_permissions:
            status_parts.append("Perms: ON")
        if self.show_disk_usage:
            status_parts.append("Disk: ON")
        if self.use_gitignore:
            status_parts.append("Gitignore: ON")
        if self.search_mode:
            status_parts.append("Search Mode")

        node = self.tree_widget.get_selected_node() if self.tree_widget else None
        if node:
            status_parts.append(f"Selected: {node.path}")

        # Show current directory
        status_parts.insert(0, f"Directory: {self.current_path}")

        status_text = " | ".join(status_parts) if status_parts else "Ready"
        status_bar.update(status_text)

    def action_move_up(self) -> None:
        """Move selection up."""
        if not self.search_mode and not self.confirmation_mode and self.tree_widget:
            self.tree_widget.move_selection(-1)
            self._update_status_bar()

    def action_move_down(self) -> None:
        """Move selection down."""
        if not self.search_mode and not self.confirmation_mode and self.tree_widget:
            self.tree_widget.move_selection(1)
            self._update_status_bar()

    def action_toggle_expand(self) -> None:
        """Toggle expand/collapse of selected directory."""
        if not self.search_mode and not self.confirmation_mode and self.tree_widget:
            self.tree_widget.toggle_expand()
            self._update_status_bar()

    async def action_navigate_into(self) -> None:
        """Navigate into the selected directory."""
        if not self.search_mode and self.tree_widget:
            node = self.tree_widget.get_selected_node()
            if node and node.is_dir:
                # Change to the selected directory
                self.current_path = node.path
                await self._change_directory(node.path)
            else:
                # If it's a file, just toggle expand (does nothing for files)
                self.tree_widget.toggle_expand()
            self._update_status_bar()

    async def action_navigate_up(self) -> None:
        """Navigate to parent directory."""
        if not self.search_mode:
            parent = self.current_path.parent
            if parent != self.current_path:  # Check we're not at root
                # Remember the directory we're coming from to highlight it
                child_to_highlight = self.current_path
                self.current_path = parent
                await self._change_directory(parent, highlight_child=child_to_highlight)
                self._update_status_bar()

    async def _change_directory(
        self, new_path: Path, highlight_child: Optional[Path] = None
    ) -> None:
        """Change the root directory of the tree."""
        if not new_path.exists() or not new_path.is_dir():
            return

        # Get the container first
        container = self.query_one("#main-container")

        # Remove old tree widget
        if self.tree_widget:
            await self.tree_widget.remove()

        # Increment counter for unique ID
        self._tree_counter += 1

        # Create new tree widget with new root
        new_tree = TreeWidget(
            FileNode(new_path),
            show_hidden=self.show_hidden,
            show_permissions=self.show_permissions,
            show_disk_usage=self.show_disk_usage,
            gitignore_spec=self.gitignore_spec,
            id=f"tree-{self._tree_counter}",
        )

        # Mount the new tree
        await container.mount(new_tree)
        self.tree_widget = new_tree

        # Initialize the tree
        root_node = self.tree_widget.root_node
        if root_node.is_dir:
            root_node.expanded = True
            root_node.load_children(self.show_hidden, self.gitignore_spec)
            if self.tree_widget._content:
                self.tree_widget._content._rebuild_flat_list()

                # If we need to highlight a specific child directory, find it and select it
                if highlight_child:
                    self.tree_widget.select_node_by_path(highlight_child)

                self.tree_widget.refresh()

    def action_expand(self) -> None:
        """Expand selected directory."""
        if not self.search_mode and self.tree_widget:
            self.tree_widget.expand_selected()
            self._update_status_bar()

    def action_collapse(self) -> None:
        """Collapse selected directory."""
        if not self.search_mode and self.tree_widget:
            self.tree_widget.collapse_selected()
            self._update_status_bar()

    def action_toggle_expand_all(self) -> None:
        """Toggle between expanding and collapsing all subdirectories of selected node."""
        if not self.search_mode and self.tree_widget:
            self.tree_widget.toggle_expand_all_subdirectories()
            self._update_status_bar()

    def action_expand_all(self) -> None:
        """Expand all subdirectories of selected node."""
        if not self.search_mode and self.tree_widget:
            self.tree_widget.expand_all_subdirectories()
            self._update_status_bar()

    def action_collapse_all(self) -> None:
        """Collapse all subdirectories of selected node."""
        if not self.search_mode and self.tree_widget:
            self.tree_widget.collapse_all_subdirectories()
            self._update_status_bar()

    def action_toggle_hidden(self) -> None:
        """Toggle showing hidden files."""
        if not self.search_mode:
            self.show_hidden = not self.show_hidden
            if self.tree_widget:
                self.tree_widget.update_settings(show_hidden=self.show_hidden)
            self._update_status_bar()

    def action_toggle_permissions(self) -> None:
        """Toggle showing permissions and sizes."""
        if not self.search_mode:
            self.show_permissions = not self.show_permissions
            if self.tree_widget:
                self.tree_widget.update_settings(show_permissions=self.show_permissions)
            self._update_status_bar()

    def action_toggle_gitignore(self) -> None:
        """Toggle gitignore filtering."""
        if not self.search_mode:
            self.use_gitignore = not self.use_gitignore
            self._update_gitignore()
            self._update_status_bar()

    def action_toggle_disk_usage(self) -> None:
        """Toggle showing disk usage."""
        if not self.search_mode:
            self.show_disk_usage = not self.show_disk_usage
            if self.tree_widget:
                self.tree_widget.update_settings(show_disk_usage=self.show_disk_usage)
            self._update_status_bar()

    def action_search(self) -> None:
        """Enter search mode."""
        if not self.search_mode:
            self.search_mode = True
            search_input = self.query_one("#search-input", Input)
            search_input.remove_class("hidden")
            search_input.focus()
            self._update_status_bar()

    def action_navigate_and_quit(self) -> None:
        """Navigate to current directory and quit."""
        # Set exit path to the current directory being viewed
        self.exit_path = self.current_path
        self.exit()

    def action_delete_item(self) -> None:
        """Enter delete confirmation mode for the selected file or folder."""
        if not self.search_mode and not self.confirmation_mode and self.tree_widget:
            node = self.tree_widget.get_selected_node()
            if node:
                # Don't allow deleting the root directory being viewed
                if node.path == self.current_path:
                    return

                # Enter confirmation mode
                self.confirmation_mode = True
                self.pending_delete_node = node
                self._update_status_bar()

    def _confirm_delete(self) -> None:
        """Perform the deletion after confirmation."""
        if self.pending_delete_node:
            try:
                node = self.pending_delete_node
                # Delete the file or directory
                if node.path.is_dir():
                    shutil.rmtree(node.path)
                else:
                    node.path.unlink()

                # Refresh the tree by reloading the parent node
                parent_node = self._find_parent_node(node)
                if parent_node:
                    # Force reload by resetting the loaded flag
                    parent_node._loaded = False
                    parent_node.load_children(self.show_hidden, self.gitignore_spec)
                    if self.tree_widget._content:
                        self.tree_widget._content._rebuild_flat_list()
                        # Move selection to a valid position
                        if self.tree_widget._content.selected_index >= len(
                            self.tree_widget._content.flat_nodes
                        ):
                            self.tree_widget._content.selected_index = max(
                                0, len(self.tree_widget._content.flat_nodes) - 1
                            )
                    self.tree_widget.refresh()
            except Exception:
                # If deletion fails, silently continue
                pass
            finally:
                # Exit confirmation mode
                self.confirmation_mode = False
                self.pending_delete_node = None
                self._update_status_bar()

    def _cancel_delete(self) -> None:
        """Cancel the pending deletion."""
        self.confirmation_mode = False
        self.pending_delete_node = None
        self._update_status_bar()

    def _find_parent_node(self, node: FileNode) -> Optional[FileNode]:
        """Find the parent node of a given node in the tree."""
        if not self.tree_widget:
            return None

        def search_tree(current: FileNode, target: FileNode) -> Optional[FileNode]:
            """Recursively search for the target node's parent."""
            if current.children:
                for child in current.children:
                    if child == target:
                        return current
                    found = search_tree(child, target)
                    if found:
                        return found
            return None

        return search_tree(self.tree_widget.root_node, node)

    async def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "search-input":
            search_term = event.value
            if self.tree_widget:
                if search_term:
                    self.tree_widget.filter_nodes(search_term)
                else:
                    # Clear filter
                    if self.tree_widget._content:
                        self.tree_widget._content._rebuild_flat_list()
                    self.tree_widget.refresh()
            self._update_status_bar()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            search_term = event.value
            if self.tree_widget:
                if search_term:
                    self.tree_widget.filter_nodes(search_term)
                else:
                    # Clear filter
                    if self.tree_widget._content:
                        self.tree_widget._content._rebuild_flat_list()
                    self.tree_widget.refresh()

    def on_key(self, event) -> None:
        """Handle key events."""
        # Handle confirmation mode y/n keys
        if self.confirmation_mode:
            if event.key == "y":
                self._confirm_delete()
                event.stop()
                return
            elif event.key == "n" or event.key == "escape":
                self._cancel_delete()
                event.stop()
                return

        if self.search_mode and event.key == "escape":
            # Exit search mode
            self.search_mode = False
            search_input = self.query_one("#search-input", Input)
            search_input.add_class("hidden")
            search_input.value = ""
            if self.tree_widget and self.tree_widget._content:
                self.tree_widget._content._rebuild_flat_list()
                self.tree_widget.refresh()
            self._update_status_bar()
            event.stop()
