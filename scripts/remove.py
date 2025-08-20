"""
Remove Tool Script untuk HPone

Fungsi untuk remove tool yang sudah diimport.
"""

import shutil
from pathlib import Path
from core.constants import OUTPUT_DOCKER_DIR


def remove_tool(tool_id: str) -> bool:
    """
    Remove tool yang sudah diimport.
    
    Args:
        tool_id: ID tool yang akan dihapus
        
    Returns:
        True jika berhasil, False jika gagal
    """
    try:
        tool_dir = OUTPUT_DOCKER_DIR / tool_id
        
        if not tool_dir.exists():
            print(f"❌ Tool {tool_id} tidak ditemukan di {OUTPUT_DOCKER_DIR}")
            return False
            
        # Hapus direktori tool
        shutil.rmtree(tool_dir)
        print(f"✅ Tool {tool_id} berhasil dihapus")
        return True
        
    except Exception as exc:
        print(f"❌ Gagal hapus tool {tool_id}: {exc}")
        return False
