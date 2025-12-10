from pathlib import Path
import json
import logging
from typing import Any

# test/__init__.py
# Lightweight helpers for tests (fixtures live in conftest.py when pytest is available)


# Directory of this test package
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"

# Avoid "No handler found" warnings when tests configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())


def load_fixture(name: str) -> Any:
    """
    Load and return JSON fixture from test/data/<name>.
    Example: load_fixture("sample_claim.json")
    """
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# If pytest is present, expose a couple of small fixtures for convenience.
# These are optional — test suites can import load_fixture directly.
try:
    import pytest  # type: ignore

    @pytest.fixture(scope="session")
    def data_dir() -> Path:
        """Return path to test data directory."""
        return DATA_DIR

    @pytest.fixture
    def load_json():
        """Return a callable that loads JSON fixtures by filename."""
        return load_fixture
except Exception:
    # pytest not available outside of test runs — ignore silently
    pass


__all__ = ["BASE_DIR", "DATA_DIR", "load_fixture"]