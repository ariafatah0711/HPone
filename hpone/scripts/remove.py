"""
Remove honeypot script for HPone.

Functions to remove an imported honeypot.
"""

import shutil
from pathlib import Path
from core.constants import OUTPUT_DOCKER_DIR
from core.utils import PREFIX_OK, PREFIX_ERROR


def remove_honeypot(honeypot_id: str) -> bool:
    """
    Remove an imported honeypot.

    Args:
        honeypot_id: The honeypot ID to remove

    Returns:
        True on success, False on failure
    """
    try:
        honeypot_dir = OUTPUT_DOCKER_DIR / honeypot_id

        if not honeypot_dir.exists():
            print(f"{PREFIX_ERROR} Tool {honeypot_id} not found in {OUTPUT_DOCKER_DIR}")
            return False

        # Remove honeypot directory
        shutil.rmtree(honeypot_dir)
        print(f"{PREFIX_OK}: Removed honeypot {honeypot_id}")
        return True

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to remove honeypot {honeypot_id}: {exc}")
        return False
