"""
Up command implementation for HPone.

This module handles starting honeypots with auto-import functionality,
update capabilities, and interactive import prompts for missing honeypots.
"""

import sys
from typing import List

try:
    import questionary
except ImportError:
    print("Error: questionary library not installed. Run: pip install questionary", file=sys.stderr)
    sys.exit(1)

from core import (
    up_honeypot,
    is_honeypot_enabled,
    find_honeypot_yaml_path
)

from .list import (
    list_all_enabled_honeypot_ids,
    list_enabled_honeypot_ids,
    list_imported_honeypot_ids
)

from .import_cmd import (
    import_honeypot
)

from core.utils import PREFIX_OK, PREFIX_ERROR, PREFIX_WARN

# Import configuration
try:
    from config import ALWAYS_IMPORT
except ImportError:
    ALWAYS_IMPORT = True


def up_all_honeypots(update: bool = False) -> int:
    """
    Start all enabled honeypots with optional auto-import and update functionality.

    Args:
        update: Whether to update imported honeypots before starting

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # For --all, handle ALWAYS_IMPORT differently
        if ALWAYS_IMPORT:
            # Auto-import all enabled honeypots first
            honeypot_ids = list_all_enabled_honeypot_ids()
            if not honeypot_ids:
                print("No enabled honeypots.")
                return 0

            print(f"Auto-importing {len(honeypot_ids)} enabled honeypots...")
            for t in honeypot_ids:
                try:
                    dest = import_honeypot(t, force=True)
                    # print(f"{PREFIX_OK}: Auto-imported '{t}'")
                except Exception as exc:
                    print(f"{PREFIX_ERROR} Failed to auto-import '{t}': {exc}", file=sys.stderr)
                    continue

            print(f"Starting {len(honeypot_ids)} honeypots...")
            for t in honeypot_ids:
                try:
                    up_honeypot(t, force=False)
                except Exception as exc:
                    print(f"{PREFIX_ERROR} Failed to start '{t}': {exc}", file=sys.stderr)
                    continue
        else:
            # Original logic for ALWAYS_IMPORT=false
            # If --update, update all imported honeypots first
            if update:
                imported_ids = list_imported_honeypot_ids()
                if imported_ids:
                    print(f"Updating {len(imported_ids)} imported honeypots before up...")
                    for t in imported_ids:
                        try:
                            dest = import_honeypot(t, force=True)
                            print(f"{PREFIX_OK}: Template '{t}' updated at: {dest}")
                        except Exception as exc:
                            print(f"{PREFIX_WARN} Failed to update '{t}': {exc}")
                else:
                    print("No imported honeypots to update.")

            honeypot_ids = list_enabled_honeypot_ids()
            if not honeypot_ids:
                print("No enabled and imported honeypots.")
            for t in honeypot_ids:
                up_honeypot(t, force=False)

        return 0

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to start all honeypots: {exc}", file=sys.stderr)
        return 1


def up_single_honeypot(honeypot_id: str, force: bool = False, update: bool = False) -> int:
    """
    Start a single honeypot with optional auto-import, force, and update functionality.

    Args:
        honeypot_id: The ID of the honeypot to start
        force: Whether to force the operation
        update: Whether to update the honeypot before starting

    Returns:
        Exit code (0 for success, 1 for error, 2 for missing honeypot)
    """
    try:
        # Auto-import if ALWAYS_IMPORT=true
        if ALWAYS_IMPORT:
            try:
                # First check if honeypot exists
                from core.constants import HONEYPOT_MANIFEST_DIR
                try:
                    find_honeypot_yaml_path(honeypot_id)
                except FileNotFoundError:
                    print(f"{PREFIX_ERROR} Honeypot '{honeypot_id}' not found in '{HONEYPOT_MANIFEST_DIR}'.", file=sys.stderr)
                    return 1

                # Then check if honeypot is enabled
                if not is_honeypot_enabled(honeypot_id):
                    if not force:
                        print(f"{PREFIX_ERROR} Honeypot '{honeypot_id}' is not enabled. Use --force to override.", file=sys.stderr)
                        return 1
                    print(f"{PREFIX_WARN} Honeypot '{honeypot_id}' is not enabled, but continuing with --force")

                # Auto-import the honeypot
                dest = import_honeypot(honeypot_id, force=True)
                # print(f"{PREFIX_OK}: Auto-imported '{honeypot_id}'")

                # Start the honeypot
                up_honeypot(honeypot_id, force=force)
                return 0

            except Exception as exc:
                print(f"{PREFIX_ERROR} Failed to auto-import and start '{honeypot_id}': {exc}", file=sys.stderr)
                return 1

        # Original logic for ALWAYS_IMPORT=false
        # If --update for a single honeypot, update first only if already imported
        if update:
            try:
                from core.constants import OUTPUT_DOCKER_DIR
                if (OUTPUT_DOCKER_DIR / honeypot_id).exists():
                    dest = import_honeypot(honeypot_id, force=True)
                    print(f"{PREFIX_OK}: Updated '{honeypot_id}'")
                else:
                    print(f"Skip update: honeypot '{honeypot_id}' is not imported.")
            except Exception as exc:
                print(f"{PREFIX_ERROR} Failed to update '{honeypot_id}': {exc}", file=sys.stderr)
                return 1

        try:
            up_honeypot(honeypot_id, force=force)
        except FileNotFoundError:
            # Verify the honeypot exists in honeypots/ before offering import
            try:
                from core.constants import HONEYPOT_MANIFEST_DIR
                find_honeypot_yaml_path(honeypot_id)
            except FileNotFoundError:
                print(f"{PREFIX_ERROR} Honeypot '{honeypot_id}' not found in '{HONEYPOT_MANIFEST_DIR}'.", file=sys.stderr)
                return 1

            confirm_import = questionary.confirm(
                f"Honeypot '{honeypot_id}' is not imported. Import now?"
            ).unsafe_ask()
            if confirm_import:
                try:
                    dest = import_honeypot(honeypot_id, force=False)
                    print(f"{PREFIX_OK}: Imported '{honeypot_id}'")
                    up_honeypot(honeypot_id, force=force)
                except Exception as exc:
                    print(f"{PREFIX_ERROR} Failed to start '{honeypot_id}': {exc}", file=sys.stderr)
                    return 1
            else:
                print("Cancelled.")
                return 0

        return 0

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to start '{honeypot_id}': {exc}", file=sys.stderr)
        return 1


def up_main(args) -> int:
    """
    Main function for the up command.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for error, 2 for invalid arguments)
    """
    try:
        if getattr(args, "all", False):
            return up_all_honeypots(
                update=getattr(args, "update", False)
            )
        else:
            if not args.honeypot:
                print("You must specify a honeypot or use --all", file=sys.stderr)
                return 2

            return up_single_honeypot(
                args.honeypot,
                force=getattr(args, "force", False),
                update=getattr(args, "update", False)
            )

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to start: {exc}", file=sys.stderr)
        return 1
