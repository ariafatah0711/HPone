#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    hpone_root = base_dir.parent
    if str(hpone_root) not in sys.path:
        sys.path.insert(0, str(hpone_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hpone_web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. Install with: pip install django"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
