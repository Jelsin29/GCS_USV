"""
Shared fixtures for GCS UI tests (pytest-qt).

Run from the project root so relative asset paths resolve correctly:
    cd /home/jelsin/projecto/GCS_USV
    source ~/venv-ardupilot/bin/activate
    pytest tests/ -v
"""

import os
import sys
import pytest

# Make sure imports resolve from the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Change to project root so relative paths (fonts, icons, map.html) resolve
os.chdir(PROJECT_ROOT)


@pytest.fixture(scope="session")
def main_window(qapp):
    """
    Create a single MainWindow for the test session.
    Firebase is skipped — the app continues without it (same as when offline).
    """
    from MainWindow import MainWindow

    win = MainWindow(firebase=None)
    win.show()
    yield win
    win.close()
