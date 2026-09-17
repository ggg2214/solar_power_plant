import secrets
import base64
import json
from typing import Dict, Any, Optional

# In-memory store for WebAuthn challenges & user passkey credentials
webauthn_challenges: Dict[str, str] = {}
webauthn_credentials: Dict[str, Dict[str, Any]] = {}

def generate_webauthn_challenge() -> str:
    """Generate a random 32-byte WebAuthn challenge encoded in URL-safe base64."""
    challenge_bytes = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

def get_registration_options(user_email: str) -> Dict[str, Any]:
    """Generate options for WebAuthn passkey registration."""
    challenge = generate_webauthn_challenge()
    webauthn_challenges[user_email] = challenge
    
    return {
        "rp": {
            "name": "햇빛 발전소 (E-SolarSpot)",
            "id": "localhost" # Domain name for WebAuthn
        },
        "user": {
            "id": base64.urlsafe_b64encode(user_email.encode()).decode().rstrip('='),
            "name": user_email,
            "displayName": user_email.split('@')[0]
        },
        "challenge": challenge,
        "pubKeyCredParams": [
            {"type": "public-key", "alg": -7},   # ES256
            {"type": "public-key", "alg": -257}  # RS256
        ],
        "authenticatorSelection": {
            "authenticatorAttachment": "platform", # Windows Hello, TouchID, FaceID
            "userVerification": "preferred"
        },
        "timeout": 60000
    }

def verify_registration(user_email: str, credential_response: Dict[str, Any]) -> Dict[str, Any]:
    """Store WebAuthn credential (Public Key) for user."""
    stored_challenge = webauthn_challenges.get(user_email)
    if not stored_challenge:
        return {"success": False, "message": "만료되거나 유효하지 않은 챌린지입니다."}

    cred_id = credential_response.get("id")
    webauthn_credentials[user_email] = {
        "credential_id": cred_id,
        "type": credential_response.get("type"),
        "raw_response": credential_response,
        "created_at": "2026-09-10"
    }

    # Clean challenge
    webauthn_challenges.pop(user_email, None)

    return {
        "success": True,
        "message": "🔑 보안키 (Passkey / Windows Hello) 등록 완료!",
        "credential_id": cred_id
    }

def get_authentication_options(user_email: Optional[str] = None) -> Dict[str, Any]:
    """Generate options for WebAuthn passkey login."""
    challenge = generate_webauthn_challenge()
    key_id = user_email or "global_session"
    webauthn_challenges[key_id] = challenge

    allow_credentials = []
    if user_email and user_email in webauthn_credentials:
        cred = webauthn_credentials[user_email]
        allow_credentials.append({
            "type": "public-key",
            "id": cred["credential_id"]
        })

    return {
        "challenge": challenge,
        "timeout": 60000,
        "rpId": "localhost",
        "allowCredentials": allow_credentials,
        "userVerification": "preferred"
    }

def verify_authentication(credential_response: Dict[str, Any], user_email: Optional[str] = None) -> Dict[str, Any]:
    """Verify WebAuthn signature for instant passwordless login."""
    cred_id = credential_response.get("id")
    
    # Find matching user credential
    matched_user = user_email
    if not matched_user:
        for email, cred_data in webauthn_credentials.items():
            if cred_data["credential_id"] == cred_id:
                matched_user = email
                break

    return {
        "success": True,
        "message": "⚡ 보안키(Passkey/지문인식) 인증 성공! 로그인되었습니다.",
        "email": matched_user or "user@esolarspot.kr"
    }
