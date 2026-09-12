import shutil
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def tmp_fixture(tmp_path):
    """Copy a named fixture directory into a fresh tmp_path and return it."""

    def _copy(name: str) -> Path:
        src = FIXTURES / name
        dest = tmp_path / name
        shutil.copytree(src, dest)
        return dest

    return _copy
