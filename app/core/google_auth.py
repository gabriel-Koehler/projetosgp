"""Fluxo Google OAuth para a sessão de professor."""

import base64
import hashlib
import secrets
import time
from urllib.parse import urlencode

import httpx
from starlette.requests import Request

from app.core.config import Settings

SESSION_FLOW = "google_oauth"
FLOW_SECONDS = 600


def authorization_url(request: Request, settings: Settings) -> str:
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(48)
    request.session[SESSION_FLOW] = {
        "state": state,
        "verifier": verifier,
        "expires": time.time() + FLOW_SECONDS,
    }
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    query = urlencode({
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


def consume_verifier(request: Request, state: str | None) -> str | None:
    flow = request.session.get(SESSION_FLOW)
    if not flow or not state or not secrets.compare_digest(state.encode(), flow["state"].encode()):
        return None
    request.session.pop(SESSION_FLOW)
    return flow["verifier"] if time.time() < flow["expires"] else None


def fetch_profile(settings: Settings, code: str, verifier: str) -> tuple[str, str] | None:
    with httpx.Client(timeout=5) as client:
        token = client.post("https://oauth2.googleapis.com/token", data={
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": verifier,
        }).raise_for_status().json()["access_token"]
        profile = client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {token}"},
        ).raise_for_status().json()

    subject = profile.get("sub")
    email = profile.get("email")
    if not isinstance(subject, str) or not subject or len(subject) > 255:
        return None
    if profile.get("email_verified") is not True or not isinstance(email, str) or not email:
        return None
    name = profile.get("name")
    if not isinstance(name, str) or not name.strip():
        name = email
    return subject, name.strip()[:100]
