import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest


@pytest.fixture(autouse=True)
def quiet_pygame():
    """Import pygame lazily only when a test needs it (keeps core headless)."""
    yield