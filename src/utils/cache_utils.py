"""Small cache-control helpers shared by analysis modules."""

from pathlib import Path


def should_use_cache(cache_path: Path, *, force: bool = False) -> bool:
    """Return whether an existing cache may be reused."""
    return cache_path.exists() and not force
