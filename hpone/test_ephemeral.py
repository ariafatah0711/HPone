#!/usr/bin/env python3
"""
Test script for ephemeral logging functionality.

This script demonstrates how the ephemeral logging works with various commands.
"""

import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.log_runner import run_with_ephemeral_logs, run_docker_compose_action


def test_simple_command():
    """Test with a simple command that produces output."""
    print("Testing simple command...")
    success, duration = run_with_ephemeral_logs(
        ["echo", "Hello World"],
        "echo-test"
    )
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")


def test_long_running_command():
    """Test with a command that runs for a few seconds."""
    print("Testing long-running command...")
    success, duration = run_with_ephemeral_logs(
        ["sleep", "3"],
        "sleep-test"
    )
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")


def test_command_with_output():
    """Test with a command that produces multiple lines of output."""
    print("Testing command with output...")
    success, duration = run_with_ephemeral_logs(
        ["sh", "-c", "echo 'Line 1'; sleep 1; echo 'Line 2'; sleep 1; echo 'Line 3'"],
        "output-test"
    )
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")


def test_failing_command():
    """Test with a command that fails."""
    print("Testing failing command...")
    success, duration = run_with_ephemeral_logs(
        ["false"],
        "fail-test"
    )
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")


def test_timeout_command():
    """Test with a command that times out."""
    print("Testing timeout command...")
    success, duration = run_with_ephemeral_logs(
        ["sleep", "10"],
        "timeout-test",
        timeout=2
    )
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")


def main():
    """Run all tests."""
    print("🧪 Testing Ephemeral Logging Functionality")
    print("=" * 50)
    
    tests = [
        test_simple_command,
        test_long_running_command,
        test_command_with_output,
        test_failing_command,
        test_timeout_command,
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n📋 Test {i}/{len(tests)}")
        print("-" * 30)
        test()
        time.sleep(1)  # Brief pause between tests
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
