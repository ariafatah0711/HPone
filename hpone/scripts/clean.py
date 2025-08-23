"""
Clean command implementation for HPone.

This module handles cleaning operations including stopping containers,
removing data, images, volumes, and docker directories for honeypots.
"""

import sys
import time
from typing import List

try:
    import questionary
except ImportError:
    print("Error: questionary library not installed. Run: pip install questionary", file=sys.stderr)
    sys.exit(1)

from core import (
    down_honeypot,
    cleanup_global_images,
    cleanup_global_volumes
)

from .list import (
    list_imported_honeypot_ids
)

from .remove import (
    remove_honeypot
)

from .file_ops import (
    remove_honeypot_data
)

from core.utils import PREFIX_OK, PREFIX_ERROR, PREFIX_WARN


def clean_all_honeypots(remove_data: bool = False, remove_images: bool = False, remove_volumes: bool = False) -> int:
    """
    Clean all imported honeypots with optional data, images, and volumes removal.

    Args:
        remove_data: Whether to remove data directories
        remove_images: Whether to remove Docker images
        remove_volumes: Whether to remove Docker volumes

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        imported_ids = list_imported_honeypot_ids()

        # Sequential confirmation prompts for different removal types
        remove_data_all = False
        remove_images_all = False
        remove_volumes_all = False

        # First ask about data removal if --data flag is present
        if remove_data:
            remove_data_all = questionary.confirm(
                "This will remove mounted data under data/<honeypot> for ALL honeypots. Continue?"
            ).unsafe_ask()
            if not remove_data_all:
                print("Data removal cancelled.")

        # Second ask about image removal if --image flag is present
        if remove_images:
            remove_images_all = questionary.confirm(
                "This will remove Docker images for ALL honeypots. Continue?"
            ).unsafe_ask()
            if not remove_images_all:
                print("Image removal cancelled.")

        # Third ask about volume removal if --volume flag is present
        if remove_volumes:
            remove_volumes_all = questionary.confirm(
                "This will remove Docker volumes for ALL honeypots. Continue?"
            ).unsafe_ask()
            if not remove_volumes_all:
                print("Volume removal cancelled.")

        if not imported_ids:
            # Handle data removal
            if remove_data_all:
                try:
                    # Remove all data directories under DATA_DIR even if nothing is imported
                    from core.constants import DATA_DIR
                    # Iterate over immediate subdirectories in DATA_DIR
                    if DATA_DIR.exists():
                        print("No imported honeypots. Removing data directories under data/...")
                        for d in sorted([p for p in DATA_DIR.iterdir() if p.is_dir()]):
                            try:
                                remove_honeypot_data(d.name)
                            except Exception as exc_data:
                                print(f"{PREFIX_WARN} Failed to remove data for '{d.name}': {exc_data}")
                    else:
                        print("No data directory found.")
                except Exception as exc:
                    print(f"{PREFIX_ERROR} Failed to remove data: {exc}", file=sys.stderr)
                    return 1

            # Handle global image removal when no imported honeypots
            if remove_images_all:
                try:
                    print("No imported honeypots.")
                    cleanup_global_images()
                except Exception as exc:
                    print(f"{PREFIX_WARN} Failed to remove global images: {exc}")

            # Handle global volume removal when no imported honeypots
            if remove_volumes_all:
                try:
                    cleanup_global_volumes()
                except Exception as exc:
                    print(f"{PREFIX_WARN} Failed to remove volumes: {exc}")

            # Only return if at least one operation was performed or no operations were requested
            if remove_data_all or remove_images_all or remove_volumes_all:
                return 0
            else:
                print("No imported honeypots.")
                return 0

        print(f"Cleaning {len(imported_ids)} imported honeypots (down + remove{' + data' if remove_data_all else ''}{' + images' if remove_images_all else ''}{' + volumes' if remove_volumes_all else ''})...")
        for t in imported_ids:
            try:
                # Down first
                down_honeypot(
                    t,
                    remove_volumes=remove_volumes_all,
                    remove_images=remove_images_all,
                )

                # Wait a moment for containers to fully stop before removing data
                if remove_data_all:
                    time.sleep(1)  # Brief pause to ensure containers are fully stopped

                # Remove data if confirmed - do this before removing docker directory
                if remove_data_all:
                    try:
                        success = remove_honeypot_data(t)  # This prints its own success message
                        if not success:
                            print(f"{PREFIX_WARN} Data removal for '{t}' was skipped (folder may not exist)")
                    except Exception as exc_data:
                        print(f"{PREFIX_WARN} Failed to remove data for '{t}': {exc_data}")

                # Show image/volume removal status (docker compose down with flags doesn't show explicit confirmation)
                if remove_images_all:
                    print(f"{PREFIX_OK}: Removed images for {t}")

                if remove_volumes_all:
                    print(f"{PREFIX_OK}: Removed volumes for {t}")

                # Then remove docker directory
                remove_honeypot(t)  # This prints its own success message
            except Exception as exc:
                print(f"{PREFIX_ERROR} Failed to clean '{t}': {exc}", file=sys.stderr)
                continue

        return 0

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to clean all honeypots: {exc}", file=sys.stderr)
        return 1


def clean_single_honeypot(honeypot_id: str, remove_data: bool = False, remove_images: bool = False, remove_volumes: bool = False) -> int:
    """
    Clean a single honeypot with optional data, images, and volumes removal.

    Args:
        honeypot_id: The ID of the honeypot to clean
        remove_data: Whether to remove data directories
        remove_images: Whether to remove Docker images
        remove_volumes: Whether to remove Docker volumes

    Returns:
        Exit code (0 for success, 1 for error, 2 for missing honeypot)
    """
    try:
        # Sequential confirmation prompts for single honeypot
        remove_data_single = False
        remove_images_single = False
        remove_volumes_single = False

        # Ask about data removal if --data flag is present
        if remove_data:
            remove_data_single = questionary.confirm(
                f"This will remove mounted data for honeypot '{honeypot_id}'. Continue?"
            ).unsafe_ask()
            if not remove_data_single:
                print("Data removal cancelled.")

        # Ask about image removal if --image flag is present
        if remove_images:
            remove_images_single = questionary.confirm(
                f"This will remove Docker images for honeypot '{honeypot_id}'. Continue?"
            ).unsafe_ask()
            if not remove_images_single:
                print("Image removal cancelled.")

        # Ask about volume removal if --volume flag is present
        if remove_volumes:
            remove_volumes_single = questionary.confirm(
                f"This will remove Docker volumes for honeypot '{honeypot_id}'. Continue?"
            ).unsafe_ask()
            if not remove_volumes_single:
                print("Volume removal cancelled.")

        # Down first
        down_honeypot(
            honeypot_id,
            remove_volumes=remove_volumes_single,
            remove_images=remove_images_single,
        )

        # Wait a moment for containers to fully stop before removing data
        if remove_data_single:
            time.sleep(1)  # Brief pause to ensure containers are fully stopped

        # Optionally remove data for single honeypot - do this before removing docker directory
        if remove_data_single:
            try:
                success = remove_honeypot_data(honeypot_id)  # This prints its own success message
                if not success:
                    print(f"{PREFIX_WARN} Data removal for '{honeypot_id}' was skipped (folder may not exist)")
            except Exception as exc_data:
                print(f"{PREFIX_WARN} Failed to remove data for '{honeypot_id}': {exc_data}")

        # Show image/volume removal status (docker compose down with flags doesn't show explicit confirmation)
        if remove_images_single:
            print(f"{PREFIX_OK}: Removed images for {honeypot_id}")

        if remove_volumes_single:
            print(f"{PREFIX_OK}: Removed volumes for {honeypot_id}")

        # Then remove docker directory
        remove_honeypot(honeypot_id)  # This prints its own success message

        return 0

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to clean '{honeypot_id}': {exc}", file=sys.stderr)
        return 1


def clean_main(args) -> int:
    """
    Main function for the clean command.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for error, 2 for invalid arguments)
    """
    try:
        if getattr(args, "all", False):
            return clean_all_honeypots(
                remove_data=getattr(args, "data", False),
                remove_images=getattr(args, "image", False),
                remove_volumes=getattr(args, "volume", False)
            )
        else:
            if not args.honeypot:
                print("You must specify a honeypot or use --all", file=sys.stderr)
                return 2

            return clean_single_honeypot(
                args.honeypot,
                remove_data=getattr(args, "data", False),
                remove_images=getattr(args, "image", False),
                remove_volumes=getattr(args, "volume", False)
            )

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to clean: {exc}", file=sys.stderr)
        return 1
