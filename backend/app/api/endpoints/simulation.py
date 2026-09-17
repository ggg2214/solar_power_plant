from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.pvlib_engine import SolarSimulationEngine

router = APIRouter(prefix="/simulation", tags=["simulation"])

class SimulationRequest(BaseModel):
    latitude: float = Field(37.5665, description="설치 위치 위도")
    longitude: float = Field(126.9780, description="설치 위치 경도")
    capacity_kw: float = Field(10.0, description="태양광 설치 용량 (kW)")
    panel_tilt: float = Field(30.0, description="패널 경사각 (도)")
    panel_azimuth: float = Field(180.0, description="패널 방위각 (도, 정남향=180)")
    shadow_loss_percent: float = Field(5.0, description="3D 그림자 손실률 (%)")
    module_efficiency: float = Field(0.20, description="모듈 변환 효율 (0.20 = 20%)")
    inverter_efficiency: float = Field(0.96, description="인버터 변환 효율 (0.96 = 96%)")

@router.post("/calculate", summary="태양광 발전량 및 경제성(ROI) 시뮬레이션")
async def calculate_solar_power(req: SimulationRequest) -> Dict[str, Any]:
    """
    태양 천정각/방위각 계산, 3D 음영 차폐 손실률, 셀 온도 감쇄 및 인버터 손실을 반영하여
    연간 발전량(kWh), 월별 예상 발전량, 경제성(회수기간, CAPEX/OPEX), CO2 절감 효과를 도출합니다.
    """
    res = SolarSimulationEngine.estimate_daily_annual_generation(
        lat=req.latitude,
        lon=req.longitude,
        capacity_kw=req.capacity_kw,
        panel_tilt=req.panel_tilt,
        panel_azimuth=req.panel_azimuth,
        module_efficiency=req.module_efficiency,
        inverter_efficiency=req.inverter_efficiency,
        shadow_loss_percent=req.shadow_loss_percent
    )
    
    sun_pos = SolarSimulationEngine.calculate_sun_position(req.latitude, req.longitude, datetime.now())

    return {
        "status": "success",
        "input_parameters": req.model_dump(),
        "sun_position_now": sun_pos,
        "results": res
    }
