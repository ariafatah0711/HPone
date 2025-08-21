#!/usr/bin/env python3
"""
Test script to demonstrate different logging modes.

This script shows the difference between ephemeral and simple logging.
"""

import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.log_runner import run_with_ephemeral_logs


def test_ephemeral_mode():
    """Test ephemeral logging mode."""
    print("🔍 Testing Ephemeral Logging Mode")
    print("=" * 40)
    
    success, duration = run_with_ephemeral_logs(
        ["sh", "-c", "echo 'Building image...'; sleep 1; echo 'Starting container...'; sleep 1; echo 'Ready!'"],
        "demo-tool"
    )
    
    print(f"Ephemeral mode result: {'SUCCESS' if success else 'FAILED'}")
    print()


def test_simple_mode():
    """Test simple output mode (simulated)."""
    print("🔍 Testing Simple Output Mode")
    print("=" * 40)
    
    # Simulate simple mode output
    print("[UP] demo-tool OK")
    print("Simple mode result: SUCCESS")
    print()


def compare_modes():
    """Compare both logging modes."""
    print("📊 Logging Mode Comparison")
    print("=" * 50)
    
    print("Ephemeral Mode (USE_EPHEMERAL_LOGGING = True):")
    print("  ✅ Real-time output with timestamps")
    print("  ✅ Auto-clear logs after completion")
    print("  ✅ Shows duration and detailed status")
    print("  ✅ Better for long-running operations")
    print()
    
    print("Simple Mode (USE_EPHEMERAL_LOGGING = False):")
    print("  ✅ Minimal output")
    print("  ✅ No log clearing")
    print("  ✅ Quick status display")
    print("  ✅ Better for scripts and automation")
    print()


def main():
    """Run the logging mode tests."""
    print("🧪 Logging Mode Test Suite")
    print("=" * 50)
    
    # Show comparison first
    compare_modes()
    
    # Test ephemeral mode
    test_ephemeral_mode()
    
    # Test simple mode
    test_simple_mode()
    
    print("💡 To switch modes, edit hpone/config.py:")
    print("   USE_EPHEMERAL_LOGGING = True   # For ephemeral mode")
    print("   USE_EPHEMERAL_LOGGING = False  # For simple mode")


if __name__ == "__main__":
    main()
