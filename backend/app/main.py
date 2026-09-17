from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.api.endpoints import solar, kpx, simulation, vworld, weather, auth, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="도심형 소규모 분산에너지(태양광) 입지 분석 및 발전량 시뮬레이터 '햇빛 발전소 (E-SolarSpot)' 백엔드 API"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Endpoints (API 1 ~ API 10 & Auth & AI Chat)
app.include_router(auth.router, prefix="/api")       # SHA-256 회원가입 & 로그인
app.include_router(solar.router, prefix="/api")      # API 1, API 2
app.include_router(kpx.router, prefix="/api")        # API 3, API 9, API 10
app.include_router(vworld.router, prefix="/api")     # API 4, API 5, API 6
app.include_router(weather.router, prefix="/api")    # API 7, API 8
app.include_router(simulation.router, prefix="/api") # 3D Shadow & Physics Calculator
app.include_router(chat.router, prefix="/api")       # AI Chatbot API

@app.get("/health", summary="Root Health Check")
def root_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_count": 10,
        "auth_security": "SHA-256 + Salt One-Way Hashing",
        "docs": "/docs"
    }

# Mount Static Dashboard UI
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
