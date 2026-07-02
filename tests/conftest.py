"""Pytest configuration shared by the test suite."""

from __future__ import annotations

import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parent.parent / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
