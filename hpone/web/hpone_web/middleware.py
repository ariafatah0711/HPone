from __future__ import annotations

from urllib.parse import urlencode
from django.core import signing
from django.shortcuts import redirect

from .auth import get_credentials

COOKIE_NAME = "hpone_auth"


def _is_login_path(path: str) -> bool:
    return path.startswith("/login") or path.startswith("/static/")


def _sign_user(username: str) -> str:
    return signing.dumps({"u": username})


def _unsign_user(value: str) -> str | None:
    try:
        data = signing.loads(value)
        return data.get("u")
    except signing.BadSignature:
        return None

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _is_login_path(request.path):
            return self.get_response(request)

        cookie = request.COOKIES.get(COOKIE_NAME)
        username = _unsign_user(cookie) if cookie else None
        creds = get_credentials()
        if username == creds.username:
            return self.get_response(request)

        query = urlencode({"next": request.get_full_path()})
        return redirect(f"/login/?{query}")


def set_auth_cookie(response, username: str) -> None:
    response.set_cookie(
        COOKIE_NAME,
        _sign_user(username),
        httponly=True,
        samesite="Lax",
    )
