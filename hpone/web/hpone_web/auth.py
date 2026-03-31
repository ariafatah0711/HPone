from __future__ import annotations

from dataclasses import dataclass
import os
import secrets

@dataclass(frozen=True)
class Credentials:
    username: str
    password: str

_USERNAME = os.environ.get("HPONE_WEB_USER", "admin")
_PASSWORD = os.environ.get("HPONE_WEB_PASSWORD") or secrets.token_urlsafe(12)
_CREDS = Credentials(username=_USERNAME, password=_PASSWORD)

def get_credentials() -> Credentials:
    return _CREDS

def verify(username: str, password: str) -> bool:
    return username == _CREDS.username and password == _CREDS.password
