"""Entry point for lx command."""

import sys
import os
import tempfile
from pathlib import Path
from .app import LxApp


def main():
    """Main entry point for lx command."""
    # Parse command line arguments
    path = None
    if len(sys.argv) > 1:
        path_str = sys.argv[1]
        path = Path(path_str).expanduser().resolve()
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            sys.exit(1)
        if not path.is_dir():
            print(f"Error: Path is not a directory: {path}")
            sys.exit(1)
    else:
        path = Path.cwd()

    # Create temp file path for exit directory
    # Use shell PID from environment if available, otherwise use our PID
    shell_pid = os.environ.get("LX_SHELL_PID", str(os.getpid()))
    temp_dir = tempfile.gettempdir()
    exit_file = Path(temp_dir) / f"lx_exit_{shell_pid}"

    # Create and run the app
    try:
        app = LxApp(path=path)
        app.run()

        # If exit_path is set, write it to temp file for shell wrapper
        if app.exit_path:
            exit_file.write_text(str(app.exit_path))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
