# lx - Interactive Directory Tree Explorer

`lx` is a modern terminal user interface (TUI) application for exploring directory structures. Navigate your filesystem with an interactive, collapsible tree view using only your keyboard.

<p align="center">
  <img src="./assets/lx.gif" alt="Demo" width="720"/>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version"/>
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License"/>
</p>

## Features

- 🌳 **Interactive Tree View** - Collapsible directory tree with visual indicators
- ⌨️  **Keyboard Navigation** - Efficient navigation with arrow keys
- 👁️ **Hidden Files Toggle** - Show/hide dot files with a single key (`a`)
- 🔍 **Search & Filter** - Quickly find files with `/` key
- 📁 **Auto-CD** - Navigate and automatically change directory on Enter
- 🎨 **Syntax Highlighting** - Color-coded files and directories
- 📊 **File Information** - Optional display of permissions, sizes, and counts
- 🚫 **GitIgnore Support** - Respect `.gitignore` patterns
- ⚡ **Fast & Efficient** - Lazy loading for large directories
- 🔗 **Symlink Support** - Shows symlink targets

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Keybindings](#keybindings)
- [Features in Detail](#features-in-detail)
- [Shell Integration](#shell-integration)
- [Distribution & Sharing](#distribution--sharing)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

---

## Installation

### Option 1: Using pipx (Recommended)

[pipx](https://pipx.pypa.io/) is the best way to install Python CLI applications:

```bash
# Install pipx if you don't have it
pip install --user pipx
pipx ensurepath

# Install lx
pipx install lx
```

### Option 2: Using the Install Script

For development or local installation from source:

```bash
# Clone or download the repository
cd /path/to/lx

# Run the installer
./scripts/install.sh
```

The installer will:
- Check for Python 3.10+ and pip
- Install the lx package
- Ensure the `lx` command is available system-wide
- Optionally add shell integration to your `.bashrc` or `.zshrc`

### Option 3: Using pip

```bash
# Install from PyPI (when published)
pip install --user lx

# Or install from source
pip install -e .

# Or from wheel
pip install dist/lx-0.1.0-py3-none-any.whl
```

### Requirements

- Python 3.10 or higher
- Terminal with color support (256 colors recommended)
- Linux, macOS, or WSL

---

## Quick Start

### Basic Usage

```bash
# Explore current directory
lx

# Explore specific directory
lx /path/to/directory

# Explore home directory
lx ~
```

### Essential Keybindings

| Key | Action |
|-----|--------|
| **`a`** | Toggle hidden files (`.git`, `.bashrc`, etc.) |
| **↑/↓** | Navigate up/down |
| **→** | Enter directory |
| **←** | Go to parent directory |
| **Enter** | CD to directory and quit |
| **Space** | Expand/collapse directory |
| **`/`** | Search/filter |
| **`q`** | Quit |

### Quick Tips

1. **Show hidden files**: Press `a` to see `.git`, `.config`, `.bashrc`, etc.
2. **Search**: Press `/` and type to filter files
3. **Fast navigation**: Use arrow keys and Space to expand folders
4. **Auto-CD**: Press Enter to change to a directory and exit
5. **Status bar**: Check bottom of screen for current settings

---

## Keybindings

### Navigation

| Key | Action | Description |
|-----|--------|-------------|
| **↑** | Move Up | Move selection up one item |
| **↓** | Move Down | Move selection down one item |
| **→** | Navigate Into | Change directory to selected folder |
| **←** | Navigate Up | Go to parent directory |
| **Enter** | Navigate & Quit | CD to current directory and exit |

### Directory Expansion

| Key | Action | Description |
|-----|--------|-------------|
| **Space** | Toggle Expand | Expand or collapse selected directory |
| **Tab** | Toggle Expand/Collapse All | Toggle between expanding and collapsing all subdirectories |
| **Shift+Tab** | Collapse All | Force collapse all subdirectories of selection |

### Display Toggles

| Key | Action | Description |
|-----|--------|-------------|
| **`a`** | **Toggle Hidden Files** | **Show/hide files starting with `.`** |
| **`s`** | Toggle Permissions | Show/hide file permissions and sizes |
| **`d`** | Toggle Disk Usage | Show/hide file sizes |
| **`g`** | Toggle .gitignore | Enable/disable gitignore filtering |

### Search & Filter

| Key | Action | Description |
|-----|--------|-------------|
| **`/`** | Search | Enter search mode to filter files/folders |
| **Esc** | Exit Search | Exit search mode and clear filter |

### Exit

| Key | Action | Description |
|-----|--------|-------------|
| **`q`** | Quit | Exit without changing directory |
| **Esc** | Quit | Same as 'q' (when not in search mode) |

---

## Features in Detail

### Hidden Files

By default, files and directories starting with `.` are hidden. Press `a` to toggle visibility.

**Common hidden files you'll see:**
- `.git/` - Git repository data
- `.config/` - Application configurations
- `.bashrc`, `.zshrc` - Shell configurations
- `.cache/` - Application cache
- `.local/` - User data and binaries
- `.venv/` - Python virtual environments

**Status indicator**: The status bar shows `Hidden: ON` when hidden files are visible.

### Search & Filter

Press `/` to enter search mode:

1. Type your search term
2. Matching files/directories are highlighted
3. Press Esc to clear search
4. Search works on visible files (respects hidden file toggle)

### Directory Counts

Each directory shows its direct child count in parentheses:

```
[+] projects (15)
    ├── [+] lx (8)
    ├── [+] website (23)
    └── README.md
```

The count updates based on:
- Hidden files setting (with/without dot files)
- GitIgnore setting (if enabled)

### GitIgnore Support

Press `g` to toggle `.gitignore` pattern filtering:

- Reads `.gitignore` files in current and parent directories
- Hides files/folders matching patterns
- Useful for exploring projects without build artifacts
- Status bar shows `Gitignore: ON` when active

### Display Options

Press `s` to show file permissions and sizes:
```
[+] projects (15) rwxr-xr-x
    ├── README.md rwxr--r-- 2.5KB
    └── script.sh rwxr-xr-x 1.2KB
```

Press `d` to show disk usage for files.

### Colors & Icons

- **Directories**: Bold cyan with 📁 icon
- **Executables**: Green
- **Symlinks**: Magenta with target display
- **Regular files**: Default color
- **Selected item**: Highlighted background

---

## Shell Integration

To enable automatic directory navigation when you press Enter, add this function to your shell config.

### For Bash

Add to `~/.bashrc`:

```bash
# lx directory navigator
lx() {
    local exit_file="/tmp/lx_exit_$$"
    LX_SHELL_PID=$$ command lx "$@"
    local exit_code=$?
    if [ -f "$exit_file" ]; then
        local target_dir=$(cat "$exit_file")
        rm -f "$exit_file"
        if [ -d "$target_dir" ]; then
            cd "$target_dir" || return
        fi
    fi
    return $exit_code
}
```

### For Zsh

Add to `~/.zshrc`:

```zsh
# lx directory navigator
lx() {
    local exit_file="/tmp/lx_exit_$$"
    LX_SHELL_PID=$$ command lx "$@"
    local exit_code=$?
    if [[ -f "$exit_file" ]]; then
        local target_dir=$(cat "$exit_file")
        rm -f "$exit_file"
        if [[ -d "$target_dir" ]]; then
            cd "$target_dir" || return
        fi
    fi
    return $exit_code
}
```

### Activate

```bash
# Reload your config
source ~/.bashrc  # or ~/.zshrc for zsh

# Or the installer can do this automatically
./scripts/install.sh
```

**How it works**: When you press Enter, lx writes the selected directory to a temp file, then your shell function reads it and changes to that directory.

---

## Distribution & Sharing

### Building Packages

To create distributable packages:

```bash
# Build wheel and source distribution
./build.sh

# Packages created in dist/:
# - lx-0.1.0-py3-none-any.whl (wheel)
# - lx-0.1.0.tar.gz (source)
```

### Sharing Options

#### 1. Direct File Sharing

Share the wheel file with others:

```bash
# Send them: dist/lx-0.1.0-py3-none-any.whl

# They install with:
pipx install lx-0.1.0-py3-none-any.whl
```

#### 2. Publish to PyPI

```bash
# Install twine
pip install twine

# Upload to PyPI (requires account at pypi.org)
twine upload dist/*

# Users can then install with:
pipx install lx
```

#### 3. GitHub Release

1. Push code to GitHub
2. Create a release (tag: `v0.1.0`)
3. Upload `dist/*` files as release assets

Users install with:
```bash
pipx install git+https://github.com/username/lx.git
```

### Before Publishing

Update `pyproject.toml` with your information:

```toml
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

[project.urls]
Homepage = "https://github.com/yourusername/lx"
Repository = "https://github.com/yourusername/lx"
```

---

## Troubleshooting

### "lx: command not found"

**Solution 1**: Ensure Python bin directory is in PATH

```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Solution 2**: Reinstall with pipx

```bash
pipx install lx --force
```

**Solution 3**: Check installation location

```bash
which lx
# Should show: /home/user/.local/bin/lx or similar
```

### Installation Fails

**Error: "pip is not installed"**

```bash
# Fedora/RHEL
sudo dnf install python3-pip

# Ubuntu/Debian
sudo apt install python3-pip

# macOS
brew install python3
```

**Error: "Python version too old"**

lx requires Python 3.10+. Check your version:

```bash
python3 --version

# Upgrade if needed (example for Fedora)
sudo dnf install python3.10
```

**Error: "Can not perform a '--user' install"**

You're in a virtualenv. Either:

```bash
# Option 1: Deactivate virtualenv first
deactivate
./scripts/install.sh

# Option 2: Install in virtualenv
pip install -e .
```

### Colors Don't Work

Ensure your terminal supports 256 colors:

```bash
echo $TERM
# Should show something like "xterm-256color"

# If not, set it:
export TERM=xterm-256color
```

### Scrolling Issues

If navigation goes off-screen:
- This was fixed in v0.1.0
- Make sure you have the latest version
- Try: `pipx upgrade lx`

### Shell Integration Not Working

1. Make sure you added the function to the correct file
2. Reload your shell: `source ~/.bashrc` or `source ~/.zshrc`
3. Test: `type lx` should show the function
4. Check for syntax errors in your shell config

---

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/jorbraken/lx.git
cd lx

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or use make
make dev-install
```

### Project Structure

```
lx/
├── lx/                    # Main package
│   ├── __init__.py
│   ├── __main__.py       # Entry point
│   ├── app.py            # Main application
│   ├── tree_widget.py    # Tree rendering
│   ├── file_node.py      # File/directory nodes
│   ├── file_utils.py     # Utility functions
│   └── styles.tcss       # Textual CSS styles
├── scripts/              # Installation scripts
│   ├── install.sh
│   └── uninstall.sh
├── dist/                 # Built packages
├── pyproject.toml        # Package configuration
├── README.md             # This file
├── CHANGELOG.md          # Version history
├── DEV_README.md         # Development guide
└── LICENSE               # MIT License
```

### Running from Source

```bash
# Run directly
python3 -m lx

# Or with debug mode
TEXTUAL=debug python3 -m lx
```

### Building

```bash
# Clean and build
make clean
make build

# Or use the build script
./build.sh
```

### Testing

```bash
# Run tests (if available)
make test

# Type checking
make type-check

# Linting
make lint

# Format code
make format
```

### Making Changes

1. Create a branch: `git checkout -b feature-name`
2. Make your changes
3. Test thoroughly: `python3 -m lx`
4. Update CHANGELOG.md
5. Commit and push
6. Create a pull request

### Dependencies

- **textual** (>= 0.40.0) - TUI framework
- **pathspec** (>= 0.11.0) - GitIgnore pattern matching

### Version Bumping

Update version in `pyproject.toml`:

```toml
[project]
version = "0.2.0"  # MAJOR.MINOR.PATCH
```

Then rebuild:

```bash
./build.sh
```

---

## Uninstallation

### Using the Uninstall Script

```bash
./scripts/uninstall.sh
```

This removes:
- The lx package
- Shell integration from your config files
- Creates backups before removing

### Manual Uninstall

```bash
# Remove package
pipx uninstall lx
# or
pip uninstall lx

# Manually remove shell function from ~/.bashrc or ~/.zshrc
# (Search for "# lx directory navigator" and remove that section)
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

See `DEV_README.md` for detailed development guidelines.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

## License

MIT License

Copyright (c) 2024 lx Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Credits

Built with:
- [Textual](https://textual.textualize.io/) - Modern TUI framework
- [pathspec](https://github.com/cpburnz/python-pathspec) - GitIgnore pattern matching

---

## Links

- **Repository**: https://github.com/yourusername/lx
- **Issues**: https://github.com/yourusername/lx/issues
- **PyPI**: https://pypi.org/project/lx/ (when published)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Development**: [DEV_README.md](DEV_README.md)

---

**Made with ❤️ for developers and sysadmins who love the terminal**
