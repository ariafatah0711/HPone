"""
Remove tool script for HPone.

Functions to remove an imported tool.
"""

import shutil
from pathlib import Path
from core.constants import OUTPUT_DOCKER_DIR


def remove_tool(tool_id: str) -> bool:
    """
    Remove an imported tool.
    
    Args:
        tool_id: The tool ID to remove
        
    Returns:
        True on success, False on failure
    """
    try:
        tool_dir = OUTPUT_DOCKER_DIR / tool_id
        
        if not tool_dir.exists():
            print(f"[ERROR] Tool {tool_id} not found in {OUTPUT_DOCKER_DIR}")
            return False
            
        # Remove tool directory
        shutil.rmtree(tool_dir)
        print(f"OK: Removed tool {tool_id}")
        return True
        
    except Exception as exc:
        print(f"[ERROR] Failed to remove tool {tool_id}: {exc}")
        return False
