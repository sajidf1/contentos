"""Per-visitor, short-lived Google Drive OAuth and Google Docs creation.

No shared Drive account, persistent tokens, or refresh tokens.
Requires Streamlit server-side secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
GOOGLE_REDIRECT_URI, GOOGLE_OAUTH_STATE_SECRET.
"""
from html import escape
from urllib.parse import urlencode
import secrets

import requests
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"
SCOPE = "https://www.googleapis.com/auth/drive.file"


def configured(config):
    return all(config(k) for k in (
        "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI", "GOOGLE_OAUTH_STATE_SECRET"
    ))


def signer(config):
    return URLSafeTimedSerializer(config("GOOGLE_OAUTH_STATE_SECRET"), salt="content-studio-google-drive")


def authorization_url(config):
    state = signer(config).dumps({"nonce": secrets.token_urlsafe(24), "redirect": config("GOOGLE_REDIRECT_URI")})
    params = {
        "client_id": config("GOOGLE_CLIENT_ID"),
        "redirect_uri": config("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "online",
        "include_granted_scopes": "false",
        "state": state,
    }
    return AUTH_URL + "?" + urlencode(params)


def exchange_callback(config, code, state):
    try:
        payload = signer(config).loads(state, max_age=600)
    except (BadSignature, SignatureExpired) as exc:
        raise ValueError("Invalid or expired Google authorization response. Please reconnect.") from exc
    if payload.get("redirect") != config("GOOGLE_REDIRECT_URI"):
        raise ValueError("Google redirect configuration changed. Please reconnect.")
    response = requests.post(TOKEN_URL, data={
        "code": code,
        "client_id": config("GOOGLE_CLIENT_ID"),
        "client_secret": config("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": config("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code",
    }, timeout=20)
    response.raise_for_status()
    result = response.json()
    if "access_token" not in result:
        raise ValueError("Google did not return an access token.")
    if SCOPE not in result.get("scope", SCOPE).split():
        raise ValueError("Google did not grant the requested Drive file permission.")
    return result["access_token"], min(int(result.get("expires_in", 3600)), 3600)


def _html(markdown_text):
    """Conservative HTML conversion for Drive's native Google Docs import."""
    import markdown
    return '<html><head><meta charset="utf-8"></head><body>' + markdown.markdown(
        markdown_text, extensions=["extra", "sane_lists"], output_format="html"
    ) + '</body></html>'


def create_google_doc(access_token, title, markdown_text):
    """Import a new native Google Doc into the authorized visitor's Drive."""
    if not markdown_text.strip():
        raise ValueError("Generate a draft before creating a Google Doc.")
    safe_title = (title or "Content Studio draft").strip()[:150]
    metadata = {"name": safe_title, "mimeType": "application/vnd.google-apps.document"}
    import json
    boundary = "contentstudio" + secrets.token_hex(12)
    body = (
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
        + json.dumps(metadata) + "\r\n"
        + f"--{boundary}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n"
        + _html(markdown_text) + "\r\n"
        + f"--{boundary}--\r\n"
    ).encode("utf-8")
    response = requests.post(
        UPLOAD_URL,
        params={"uploadType": "multipart", "fields": "id,name,webViewLink"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": f"multipart/related; boundary={boundary}",
        },
        data=body,
        timeout=35,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("id"):
        raise ValueError("Google Drive did not return a document ID.")
    return result.get("webViewLink") or "https://docs.google.com/document/d/" + result["id"] + "/edit"
