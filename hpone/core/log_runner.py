#!/usr/bin/env python3
"""
Ephemeral log runner for HPone.

This module provides functions to run commands with live logging that gets
cleared and replaced with a summary after completion.
"""

import os
import sys
import time
import subprocess
import threading
import queue
from datetime import datetime
from typing import Optional, Callable, Any
from pathlib import Path

# ANSI escape codes for terminal control
CLEAR_SCREEN = "\033[2J\033[H"  # Clear screen and move cursor to top
CLEAR_LINE = "\033[2K"  # Clear current line
MOVE_UP = "\033[1A"  # Move cursor up one line
MOVE_DOWN = "\033[1B"  # Move cursor down one line

# Color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"


def get_timestamp() -> str:
    """Get current timestamp in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


def clear_screen() -> None:
    """Clear the terminal screen cross-platform."""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/Mac
        os.system('clear')


def clear_lines(count: int) -> None:
    """Clear specified number of lines from current position."""
    for _ in range(count):
        print(CLEAR_LINE + MOVE_UP, end='')
    print(CLEAR_LINE, end='')


def run_with_ephemeral_logs(
    command: list[str],
    honeypot_name: str,
    cwd: Optional[Path] = None,
    timeout: Optional[int] = None,
    on_log_line: Optional[Callable[[str], None]] = None,
    action: Optional[str] = None
) -> tuple[bool, float]:
    """
    Run a command with ephemeral logging display.

    Args:
        command: List of command arguments
        honeypot_name: Name of the honeypot for display
        cwd: Working directory for the command
        timeout: Command timeout in seconds (None = no timeout)
        on_log_line: Optional callback for each log line

    Returns:
        Tuple of (success: bool, duration: float)
    """
    start_time = time.time()
    log_lines: list[str] = []
    is_build_command = "up" in command and "-d" in command

    def should_show_line(line: str) -> bool:
        """Filter out verbose build output but keep important information."""
        if not is_build_command:
            return True

        line_lower = line.lower()

        # Always show these important messages
        important_keywords = ['error', 'failed', 'fatal', 'exception', 'warn', 'warning',
                             'done', 'finished', 'complete', 'started', 'created', 'pull complete']
        if any(keyword in line_lower for keyword in important_keywords):
            return True

        # Show main pull events but not progress details
        if 'pulling' in line_lower and not any(skip in line_lower for skip in
            ['fs layer', 'waiting', 'downloading', 'extracting', 'verifying']):
            return True

        # Skip all verbose output patterns
        skip_patterns = [
            # Build patterns
            '#', 'transferring', 'load build definition', 'load metadata',
            'building with', 'load .dockerignore', 'internal',
            # Pull patterns
            'pulling fs layer', 'waiting', 'downloading [', 'extracting [',
            'verifying checksum', 'download complete',
            # SHA256 and hash patterns
            'sha256:', 'resolve docker.io', 'kb / ', 'mb / ', 'gb / ',
            # Database and progress patterns
            '(reading database', 'files and directories currently installed',
            # Cargo/Rust download patterns
            'downloaded ', 'kb/s', 'mb/s', ' added, ', ' removed; done'
        ]
        if any(pattern in line_lower for pattern in skip_patterns):
            return False

        # Show everything else by default
        return True

    def log_line(line: str) -> None:
        """Add a timestamped log line."""
        if should_show_line(line):
            timestamp = get_timestamp()
            formatted_line = f"[{timestamp}] [INFO] {line}"
            log_lines.append(formatted_line)
            print(formatted_line)

            if on_log_line:
                on_log_line(line)

    def clear_logs() -> None:
        """Clear all displayed log lines."""
        if log_lines:
            clear_lines(len(log_lines))

    try:
        # Start the process
        action_verb = "Stopping" if action == "down" else "Starting"
        log_line(f"{action_verb} {honeypot_name} containers ...")

        process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Read output in real-time
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break

            if line:
                line = line.strip()
                if line:  # Skip empty lines
                    log_line(line)

        # Wait for process to complete
        return_code = process.wait(timeout=timeout)
        duration = time.time() - start_time

        # Clear all logs
        clear_logs()

        # Display result
        if return_code == 0:
            if action == "down":
                status = f"{COLOR_YELLOW}[DOWN]{COLOR_RESET}"
            else:
                status = f"{COLOR_GREEN}[UP]{COLOR_RESET}"
            result = f"{COLOR_GREEN}OK{COLOR_RESET}"
        else:
            status = f"{COLOR_RED}[FAIL]{COLOR_RESET}"
            result = f"{COLOR_RED}ERR{COLOR_RESET}"

        print(f"{status} {honeypot_name} {result} ({duration:.1f}s)")
        return return_code == 0, duration

    except subprocess.TimeoutExpired:
        process.kill()
        duration = time.time() - start_time
        clear_logs()
        print(f"{COLOR_RED}[FAIL]{COLOR_RESET} {honeypot_name} {COLOR_RED}TIMEOUT{COLOR_RESET} ({duration:.1f}s)")
        return False, duration

    except Exception as e:
        duration = time.time() - start_time
        clear_logs()
        print(f"{COLOR_RED}[FAIL]{COLOR_RESET} {honeypot_name} {COLOR_RED}ERROR{COLOR_RESET} ({duration:.1f}s)")
        print(f"Error: {e}")
        return False, duration


def run_docker_compose_action(
    action: str,
    honeypot_name: str,
    honeypot_dir: Path,
    timeout: Optional[int] = None
) -> tuple[bool, float]:
    """
    Run docker compose action with ephemeral logging.

    Args:
        action: Docker compose action (up, down, etc.)
        honeypot_name: Name of the honeypot
        honeypot_dir: Directory containing docker-compose.yml
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success: bool, duration: float)
    """
    if not (honeypot_dir / "docker-compose.yml").exists():
        raise FileNotFoundError(f"docker-compose.yml not found in {honeypot_dir}")

    # Build command
    cmd = ["docker", "compose", action]
    if action == "up":
        cmd.append("-d")

    return run_with_ephemeral_logs(cmd, honeypot_name, cwd=honeypot_dir, timeout=timeout, action=action)


def run_docker_compose_action_with_args(
    action: str,
    honeypot_name: str,
    honeypot_dir: Path,
    extra_args: Optional[list[str]] = None,
    timeout: Optional[int] = None
) -> tuple[bool, float]:
    """
    Run docker compose action with extra arguments and ephemeral logging.

    Args:
        action: Docker compose action (up, down, etc.)
        honeypot_name: Name of the honeypot
        honeypot_dir: Directory containing docker-compose.yml
        extra_args: Additional arguments for docker compose command
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success: bool, duration: float)
    """
    if not (honeypot_dir / "docker-compose.yml").exists():
        raise FileNotFoundError(f"docker-compose.yml not found in {honeypot_dir}")

    # Build command
    cmd = ["docker", "compose", action]
    if action == "up":
        cmd.append("-d")
    if extra_args:
        cmd.extend(extra_args)

    return run_with_ephemeral_logs(cmd, honeypot_name, cwd=honeypot_dir, timeout=timeout, action=action)


# Example usage and testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test ephemeral log runner")
    parser.add_argument("command", nargs="+", help="Command to run")
    parser.add_argument("--honeypot", default="test", help="Tool name for display")
    parser.add_argument("--cwd", type=Path, help="Working directory")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")

    args = parser.parse_args()

    success, duration = run_with_ephemeral_logs(
        args.command,
        args.honeypot,
        cwd=args.cwd,
        timeout=args.timeout
    )

    sys.exit(0 if success else 1)
