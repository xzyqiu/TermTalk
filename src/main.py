"""Small wrapper for CLI entrypoint.

This module keeps a simple entrypoint and delegates the actual CLI to
``src.cli.main`` so the CLI code has a stable import location.
"""

from src.cli.main import main


if __name__ == "__main__":
    main()
