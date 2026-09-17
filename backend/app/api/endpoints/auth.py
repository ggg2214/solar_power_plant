from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
from app.core.auth import register_user_sha256, login_user_sha256
from app.core.webauthn import (
    get_registration_options,
    verify_registration,
    get_authentication_options,
    verify_authentication
)

router = APIRouter(prefix="/auth", tags=["auth"])

class UserSignupRequest(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일 주소")
    password: str = Field(..., min_length=6, description="비밀번호 (최소 6자 이상)")

class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일 주소")
    password: str = Field(..., description="비밀번호")

@router.post("/signup", summary="회원가입 (SHA-256 + Salt 단방향 암호화 적용)")
def signup(req: UserSignupRequest):
    result = register_user_sha256(req.email, req.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/login", summary="로그인 (SHA-256 해시 대조 인증)")
def login(req: UserLoginRequest):
    result = login_user_sha256(req.email, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result

# WebAuthn / Passkey Security Key Endpoints
@router.get("/webauthn/register-options", summary="보안키(Passkey) 등록 옵션 요청")
def passkey_register_options(email: str = Query("user@esolarspot.kr")):
    return get_registration_options(email)

@router.post("/webauthn/register-verify", summary="보안키(Passkey) 등록 결과 저장")
def passkey_register_verify(payload: Dict[str, Any] = Body(...), email: str = Query("user@esolarspot.kr")):
    res = verify_registration(email, payload)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@router.get("/webauthn/login-options", summary="보안키(Passkey) 로그인 옵션 요청")
def passkey_login_options(email: Optional[str] = Query(None)):
    return get_authentication_options(email)

@router.post("/webauthn/login-verify", summary="보안키(Passkey/지문/Windows Hello) 로그인 검증")
def passkey_login_verify(payload: Dict[str, Any] = Body(...), email: Optional[str] = Query(None)):
    return verify_authentication(payload, email)
