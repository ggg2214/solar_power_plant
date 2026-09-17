import hashlib
import os
import secrets
from typing import Tuple, Dict, Any

def generate_salt() -> str:
    """Generate a cryptographically secure 16-byte random salt (Hex string)."""
    return secrets.token_hex(16)

def hash_password_sha256(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Hashes user password using SHA-256 with a unique Salt (One-Way Hashing).
    Returns tuple: (hashed_password, salt)
    
    Even system administrators or database owners CANNOT reverse this hash back to plain password.
    """
    if not salt:
        salt = generate_salt()
        
    # Combine password with salt to prevent Rainbow Table attacks
    salted_password = (password + salt).encode('utf-8')
    password_hash = hashlib.sha256(salted_password).hexdigest()
    
    return password_hash, salt

def verify_password_sha256(plain_password: str, stored_hash: str, stored_salt: str) -> bool:
    """
    Verifies login attempt by hashing input password with stored salt.
    """
    computed_hash, _ = hash_password_sha256(plain_password, stored_salt)
    return secrets.compare_digest(computed_hash, stored_hash)

# In-memory user database simulation
in_memory_user_db: Dict[str, Dict[str, Any]] = {}

def register_user_sha256(email: str, plain_password: str) -> Dict[str, Any]:
    """Register user with SHA-256 salted password hashing."""
    if email in in_memory_user_db:
        return {"success": False, "message": "이미 가입된 이메일 계정입니다."}
        
    pwd_hash, salt = hash_password_sha256(plain_password)
    
    in_memory_user_db[email] = {
        "email": email,
        "password_hash": pwd_hash, # SHA-256 Hash stored
        "salt": salt,              # Unique Salt stored
        "created_at": "2026-09-10"
    }
    
    return {
        "success": True,
        "message": "회원가입 완료 (비밀번호 SHA-256 단방향 암호화 적용)",
        "email": email,
        "stored_data_preview": {
            "password_hash": pwd_hash[:20] + "...",
            "admin_viewable_plain_password": None # Impossible to view
        }
    }

def login_user_sha256(email: str, plain_password: str) -> Dict[str, Any]:
    """Authenticate user with SHA-256 salted hash verification."""
    user = in_memory_user_db.get(email)
    if not user:
        return {"success": False, "message": "존재하지 않는 계정입니다."}
        
    is_valid = verify_password_sha256(plain_password, user["password_hash"], user["salt"])
    if is_valid:
        return {"success": True, "message": "로그인 성공!", "email": email}
    else:
        return {"success": False, "message": "비밀번호가 일치하지 않습니다."}
