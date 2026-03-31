#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

from hpone_web.auth import get_credentials

def main() -> int:
    base_dir = Path(__file__).resolve().parent
    manage_py = base_dir / "manage.py"
    host = os.environ.get("HPONE_WEB_HOST", "0.0.0.0")
    port = os.environ.get("HPONE_WEB_PORT", "8000")
    if not os.environ.get("HPONE_WEB_USER"):
        os.environ["HPONE_WEB_USER"] = "admin"
    if not os.environ.get("HPONE_WEB_PASSWORD"):
        creds = get_credentials()
        os.environ["HPONE_WEB_PASSWORD"] = creds.password
    creds = get_credentials()
    print("HPone Web credentials", flush=True)
    print(f"  Username: {creds.username}", flush=True)
    print(f"  Password: {creds.password}", flush=True)
    print("Keep this safe; it is generated at startup.", flush=True)
    cmd = [sys.executable, str(manage_py), "runserver", f"{host}:{port}"]
    return subprocess.call(cmd)

if __name__ == "__main__":
    raise SystemExit(main())
