# src/duplifinder/output.py

"""Re-exports for backward compatibility; use submodules for new code."""

from .duplicate_renderer import render_duplicates
from .search_renderer import render_search, render_search_json

__all__ = ["render_duplicates", "render_search", "render_search_json"]