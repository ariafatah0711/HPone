#!/usr/bin/env python3
"""
HPone Launcher Script - Simple Version

Script ini bisa dijalankan dari lokasi manapun untuk menjalankan HPone.
"""

import os
import sys
import subprocess
from pathlib import Path

# =============================================================================
# KONFIGURASI PATH PROJECT - UBAH SESUAI LOKASI PROJECT ANDA
# =============================================================================

# Path ke project HPone (absolute path atau relative path)
PROJECT_PATH = Path(__file__).resolve().parent / "hpone"

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function untuk menjalankan HPone"""
    try:
        # Check if project path exists
        if not PROJECT_PATH.exists():
            print(f"Error: Project path tidak ditemukan: {PROJECT_PATH}")
            print("Ubah PROJECT_PATH di file ini sesuai lokasi project Anda")
            return 1
        
        # Change directory ke project
        os.chdir(PROJECT_PATH)
        
        # Jalankan app.py dengan semua argument
        args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
        
        # Jalankan app.py
        result = subprocess.run([sys.executable, "app.py"] + args)
        return result.returncode
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
