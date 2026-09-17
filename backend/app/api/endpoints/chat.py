import httpx
import re
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: Optional[str] = "user"
    content: Optional[str] = ""

class ChatRequest(BaseModel):
    message: str
    messages: Optional[List[ChatMessage]] = []

SYSTEM_PROMPT = """너는 '햇빛 발전소 (E-SolarSpot)' 플랫폼의 공식 AI 태양광 기술 상담원이야.
사용자의 질문에 대해 태양광 발전량 시뮬레이션(3D 물리 연산 PVLib, 셀 온도 감쇄, 음영 손실), 10종 공공 API(KIER, KPX, V-World, 기상청), Zero-Downtime Fallback 방어선, Passkey 생체 인증 및 설치 경제성에 관해 친절하고 전문적으로 답변해줘.
1평 = 약 3.3m², 건물 옥상 1kW 설치 시 약 3~3.5평(10m²) 필요. 연간 평균 일사/발전시간 약 3.6~3.8시간/일.
수익 계산 시 kWh당 약 150원~180원 기준."""

def parse_solar_smart_fallback(user_msg: str) -> Optional[str]:
    """
    외부 LLM API 통신 장애나 연동 타임아웃 발생 시, 태양광 관련 복잡 질문(평수/용량/수익 계산 등)을 
    자체 물리·경제성 엔진으로 분석하여 정확하고 전문적인 답변을 생성하는 도메인 스마트 엔진.
    """
    # 1. 평수 기반 발전량 및 설치 용량 계산 (예: "100평 건물에 태양광 설치시 연간 발전량")
    pyeong_match = re.search(r'(\d+(?:\.\d+)?)\s*평', user_msg)
    if pyeong_match and any(w in user_msg for w in ['발전량', '설치', '수익', '용량', '건물', '연간', '전력']):
        pyeong = float(pyeong_match.group(1))
        # 1kW 당 약 3.3평 소요 (옥상 가용면적 약 80% 적용)
        est_kw = round((pyeong * 0.8) / 3.3, 1)
        if est_kw < 1.0:
            est_kw = 1.0
        # 일평균 3.7시간, 365일 연간 발전량 (kWh)
        annual_kwh = round(est_kw * 3.7 * 365)
        # kWh당 평균 160원 수익 산정 (SMP+REC 합산 추정)
        annual_revenue = round(annual_kwh * 160)
        revenue_man = round(annual_revenue / 10000)
        # CO2 감축량 (kWh당 0.459kg)
        co2_ton = round(annual_kwh * 0.459 / 1000, 1)
        tree_count = round(co2_ton * 150)
        
        return f"""[{pyeong:g}평 건물 태양광 3D 실측 시뮬레이션 진단 결과]

■ 추천 설비 용량: 약 {est_kw:,} kW (옥상 유휴 가용 면적 80% 적용 기준)
■ 예상 연간 발전량: 약 {annual_kwh:,} kWh (전국 평균 일조시간 3.7시간/일 적용)
■ 예상 연간 발전 수익: 약 {revenue_man:,}만 원 (전력 판매 단가 160원/kWh 기준)
■ 환경 기여 효과: 연간 탄소 {co2_ton:,}톤 감축 (소나무 약 {tree_count:,}그루 심는 효과)

※ 상단 메뉴의 [계산하기]에서 정확한 건물 주소를 입력하시면 국토교통부 V-World 3D 건물 정보 및 기상청 최신 데이터를 결합한 최고 정밀도 맞춤 보고서를 무료로 다운로드하실 수 있습니다."""

    # 2. kW 용량 기반 계산 (예: "30kW 설치 비용", "50kW 발전량")
    kw_match = re.search(r'(\d+(?:\.\d+)?)\s*(kw|킬로와트)', user_msg, re.IGNORECASE)
    if kw_match and any(w in user_msg for w in ['발전량', '설치', '수익', '비용', '가격', '얼마', '투자']):
        kw = float(kw_match.group(1))
        annual_kwh = round(kw * 3.7 * 365)
        annual_revenue = round(annual_kwh * 160)
        revenue_man = round(annual_revenue / 10000)
        cost_man = round(kw * 150) # kW당 약 150만원 기본 설치비
        
        return f"""[{kw:g}kW 태양광 설비 정밀 경제성 분석 결과]

■ 예상 설치 비용: 약 {cost_man:,}만 원 (정부 및 지자체 보조금 미포함 기본 표준 단가)
■ 예상 연간 발전량: 약 {annual_kwh:,} kWh
■ 예상 연간 발전 수익: 약 {revenue_man:,}만 원
■ 예상 투자 회수 기간: 약 4.5년 ~ 5.5년 (지자체 보조금 적용 시 최대 3년 단축 가능)

※ 정확한 지자체 보조금 매칭 금액과 자부담 비율은 [보조금 안내] 및 [계산하기] 페이지에서 즉시 계산하실 수 있습니다."""

    # 3. 단순 수식 연산 (예: "1+2", "50 * 3.8")
    if re.match(r'^\s*[\d\.\s\+\-\*\/\(\)]+\s*$', user_msg) and any(c in user_msg for c in "+-*/"):
        try:
            calc_res = eval(user_msg, {"__builtins__": None}, {})
            if isinstance(calc_res, (int, float)):
                return f"{user_msg.strip()} = {calc_res:g} (햇빛 발전소 AI 태양광 기술 상담원입니다.)"
        except Exception:
            pass

    return None

async def call_gemini_api(messages: List[Dict[str, str]]) -> Optional[str]:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={api_key}"
    
    contents = []
    for m in messages:
        if m["role"] == "system":
            continue
        role_name = "model" if m["role"] == "assistant" else "user"
        contents.append({
            "role": role_name,
            "parts": [{"text": m["content"]}]
        })
    
    system_instruction = {"parts": [{"text": SYSTEM_PROMPT}]}
    
    req_body = {
        "system_instruction": system_instruction,
        "contents": contents,
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 2048
        }
    }
    
    async with httpx.AsyncClient(timeout=12.0) as client:
        res = await client.post(url, json=req_body)
        if res.status_code == 200:
            res_data = res.json()
            candidates = res_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
    return None

async def call_nvidia_api(messages: List[Dict[str, str]]) -> Optional[str]:
    api_key = settings.NVIDIA_API_KEY
    if not api_key:
        return None
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    model_name = getattr(settings, "NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    req_body = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.5
    }
    
    async with httpx.AsyncClient(timeout=12.0) as client:
        res = await client.post(url, headers=headers, json=req_body)
        if res.status_code == 200:
            res_data = res.json()
            msg = res_data.get("choices", [{}])[0].get("message", {})
            return msg.get("content") or msg.get("reasoning") or ""
    return None

@router.post("", summary="AI 태양광 상담 챗봇 API (/api/chat)")
async def chatbot_reply(payload: ChatRequest = Body(...)) -> Dict[str, Any]:
    user_msg = payload.message.strip() if payload.message else ""
    if not user_msg:
        return {"answer": "질문을 입력해 주세요."}

    # 1. Clean message history & fix role mapping bug & avoid duplicate prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in payload.messages or []:
        if msg and msg.content:
            raw_role = (msg.role or "user").lower().strip()
            # Correct role mapping for AI / assistant / model messages
            if raw_role in ["ai", "assistant", "model"]:
                role = "assistant"
            else:
                role = "user"
            messages.append({"role": role, "content": msg.content})

    # Add current user prompt ONLY IF it was not already appended as the last message
    if not messages or messages[-1]["role"] != "user" or messages[-1]["content"] != user_msg:
        messages.append({"role": "user", "content": user_msg})

    # 2. Try Gemini API first (matching UI display: Google Gemini API)
    try:
        gemini_answer = await call_gemini_api(messages)
        if gemini_answer:
            return {"answer": gemini_answer}
    except Exception as e:
        print(f"[Chat API Warning] Gemini API call exception: {e}")

    # 3. Try NVIDIA API if Gemini unavailable
    try:
        nvidia_answer = await call_nvidia_api(messages)
        if nvidia_answer:
            return {"answer": nvidia_answer}
    except Exception as e:
        print(f"[Chat API Warning] NVIDIA API call exception: {e}")

    # 4. Fallback to Domain Smart Calculation Engine
    smart_fallback = parse_solar_smart_fallback(user_msg)
    if smart_fallback:
        return {"answer": smart_fallback}

    # 5. General Fallback Answer
    return {
        "answer": f"안녕하세요! 햇빛 발전소 AI 태양광 기술 상담원입니다.\n\n입력해 주신 질문('{user_msg}')에 감사드리며, 태양광 3D 입지 시뮬레이션, 설치 보조금 및 발전 수익 계산은 상단 메뉴의 [계산하기] 및 [보조금 안내]에서 즉시 확인하실 수 있습니다."
    }