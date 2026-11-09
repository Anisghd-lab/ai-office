"""OAuth 2.0 PKCE and CSRF State Manager."""

import base64
import hashlib
import os
import secrets
import time
from typing import Dict, Optional, Tuple
from app.social.base import SocialPlatform


def generate_pkce_pair() -> Tuple[str, str]:
    """Generate RFC 7636 PKCE code_verifier and code_challenge."""
    # 32 random bytes -> 43 base64url characters
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
    # SHA-256 digest of verifier
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge


class OAuthStateManager:
    """Tracks OAuth states to guarantee CSRF protection and PKCE challenge binding."""

    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        # In-memory session state storage: state -> {platform, code_verifier, timestamp}
        self._pending_states: Dict[str, dict] = {}

    def create_authorization_session(
        self,
        platform: SocialPlatform,
        code_verifier: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        """Generate a cryptographically secure state token and store session."""
        state = secrets.token_urlsafe(32)
        self._pending_states[state] = {
            "platform": platform,
            "code_verifier": code_verifier,
            "created_at": time.time(),
        }
        return state, code_verifier

    def validate_callback_state(self, state: str, expected_platform: SocialPlatform) -> str:
        """Validate state token and return the bound code_verifier for PKCE exchange."""
        now = time.time()
        # Clean expired states
        self._pending_states = {
            s: v for s, v in self._pending_states.items() if now - v["created_at"] < self.ttl_seconds
        }

        if state not in self._pending_states:
            raise ValueError("Invalid, unknown, or expired OAuth state token (CSRF check failed).")

        session = self._pending_states.pop(state)
        if session["platform"] != expected_platform:
            raise ValueError(f"OAuth state platform mismatch: expected {expected_platform.value}, got {session['platform'].value}.")

        return session.get("code_verifier") or ""


oauth_state_manager = OAuthStateManager()
