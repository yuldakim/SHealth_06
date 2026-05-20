import sys
from pathlib import Path

import pytest

_MAIN_PYTHON = Path(__file__).resolve().parents[2] / "main" / "python"
if str(_MAIN_PYTHON) not in sys.path:
    sys.path.insert(0, str(_MAIN_PYTHON))


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture
def shealth_dat(repo_root: Path) -> Path:
    path = repo_root / "shealth.dat"
    if not path.is_file():
        pytest.skip("shealth.dat not found at project root")
    return path
