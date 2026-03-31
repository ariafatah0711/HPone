#!/usr/bin/env python3
"""
Run HPone Web (Django UI).
"""

import sys
import subprocess
from pathlib import Path

from core.constants import PROJECT_ROOT
from core.utils import PREFIX_ERROR

def web_main() -> int:
    web_app = PROJECT_ROOT / "hpone" / "web" / "app.py"
    if not web_app.exists():
        print(f"{PREFIX_ERROR} HPone Web app not found: {web_app}")
        return 1

    cmd = [sys.executable, str(web_app)]
    return subprocess.call(cmd)
