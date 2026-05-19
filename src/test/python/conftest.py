import sys
from pathlib import Path

_MAIN_PYTHON = Path(__file__).resolve().parents[2] / "main" / "python"
if str(_MAIN_PYTHON) not in sys.path:
    sys.path.insert(0, str(_MAIN_PYTHON))
