#!/usr/bin/env python3
"""
HPone Launcher Script - Locked Version

Program ini ngejalanin HPone tanpa bisa ditekan enter/ketik apapun,
dan Ctrl+C ditangani dengan rapi.
"""

import os
import sys
import subprocess
import signal
import termios
import tty
from pathlib import Path

PREFIX_INFO = f"\033[32mINFO\033[0m"
PREFIX_ERROR = f"\033[31m[ERROR]\033[0m"
PREFIX_WARN = f"\033[33m[WARN]\033[0m"

PROJECT_PATH = Path(__file__).resolve().parent / "hpone"

def disable_input():
    """Matikan input terminal sementara (disable enter/keyboard)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return old_settings

def flush_stdin():
    try:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass

def restore_input(old_settings):
    """Balikin input terminal seperti semula."""
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():
    if not PROJECT_PATH.exists():
        print(f"{PREFIX_ERROR} Project path tidak ditemukan: {PROJECT_PATH}")
        return 1

    os.chdir(PROJECT_PATH)
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]

    # Tangani Ctrl+C dengan rapi
    def handle_sigint(sig, frame):
        print(f"{PREFIX_INFO} Dihentikan oleh user (Ctrl+C)")
        sys.exit(130)

    signal.signal(signal.SIGINT, handle_sigint)

    # Disable input user
    old_settings = disable_input()
    try:
        # Jalanin app.py
        result = subprocess.run([sys.executable, "app.py"] + args)
        return result.returncode
    finally:
        # Restore input terminal
        flush_stdin()
        restore_input(old_settings)

if __name__ == "__main__":
    sys.exit(main())
