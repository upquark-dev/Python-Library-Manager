"""Pytest configuration.

Ensures the repository root is importable so tests can ``import core.*``
regardless of the directory pytest is invoked from.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
