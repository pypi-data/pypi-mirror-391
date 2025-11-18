"""
Documentation URL configuration for MBASIC UIs.

Provides centralized configuration for documentation URLs, supporting both
local development and production deployment.

Environment Variables:
    MBASIC_DOCS_URL: Override the documentation base URL
                     Default: https://avwohl.github.io/mbasic/help/
                     For local development: http://localhost:8000/help/
"""

import os
from pathlib import Path


# Default production documentation URL (GitHub Pages)
DEFAULT_DOCS_URL = "https://avwohl.github.io/mbasic/help/"

# Default production site URL (GitHub Pages site root)
DEFAULT_SITE_URL = "https://avwohl.github.io/mbasic/"

# Get documentation URL from environment or use default
DOCS_BASE_URL = os.environ.get('MBASIC_DOCS_URL', DEFAULT_DOCS_URL)

# Derive site base URL from docs URL (remove /help/ suffix)
# For local development: http://localhost:8000/help/ -> http://localhost:8000/
# For production: https://avwohl.github.io/mbasic/help/ -> https://avwohl.github.io/mbasic/
SITE_BASE_URL = DOCS_BASE_URL.rstrip('/').rsplit('/help', 1)[0] + '/'
if SITE_BASE_URL.endswith('//'):
    SITE_BASE_URL = SITE_BASE_URL[:-1]  # Fix double slash


def get_site_url(path: str = None) -> str:
    """
    Get the site URL for a non-help page (library, project status, etc.).

    Args:
        path: Site path (e.g., "library/", "PROJECT_STATUS/")

    Returns:
        Full URL to the site page
    """
    base = SITE_BASE_URL.rstrip('/')

    if path:
        # Ensure path has proper format
        path = path.lstrip('/')
        if not path.endswith('/') and '.' not in path:
            path += '/'
        return f"{base}/{path}"
    else:
        return f"{base}/"


def get_docs_url(topic: str = None, ui_type: str = "cli") -> str:
    """
    Get the documentation URL for a specific help topic.

    Args:
        topic: Specific help topic (e.g., "common/statements/print")
        ui_type: UI type for UI-specific help ("tk", "curses", "web", "cli")

    Returns:
        Full URL to the documentation page
    """
    base = DOCS_BASE_URL.rstrip('/')

    if topic:
        # Ensure topic has proper path format
        topic = topic.lstrip('/')
        if not topic.endswith('/') and '.' not in topic:
            topic += '/'
        return f"{base}/{topic}"
    else:
        # Default to UI-specific index
        return f"{base}/ui/{ui_type}/"


def get_local_docs_path() -> Path:
    """
    Get the path to local documentation files.

    Returns:
        Path to docs/help directory (relative to project root)

    Note: Local docs are used by UIs that render markdown directly (curses, tk).
    Web-based UIs should use get_docs_url() instead.
    """
    # Get path to this module (src/docs_config.py)
    src_dir = Path(__file__).parent

    # Project root is parent of src
    project_root = src_dir.parent

    # docs/help is the help documentation root
    return project_root / "docs" / "help"


def is_using_remote_docs() -> bool:
    """
    Check if documentation is configured to use remote URL.

    Returns:
        True if using remote (web-based) documentation, False if localhost
    """
    return not DOCS_BASE_URL.startswith('http://localhost')


# For backwards compatibility and convenience
HELP_BASE_URL = DOCS_BASE_URL
