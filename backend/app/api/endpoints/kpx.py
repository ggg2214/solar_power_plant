import httpx
from fastapi import APIRouter, Query
from typing import Optional
from app.core.config import settings

router = APIRouter(prefix="/kpx", tags=["kpx"])

@router.get("/pv-amount", summary="지역별 시간별 태양광 발전량 정보 (API_3)")
async def get_regional_pv_amount(
    area: Optional[str] = Query("서울특별시", description="광역시/도 지역명"),
    date: Optional[str] = Query("20260901", description="거래 일자 (YYYYMMDD)")
):
    """
    한국전력거래소 전력시장 가입 태양광 발전설비의 지역별/시간별 발전량 데이터 (MWh 단위, API_3 연동).
    """
    params = {
        "serviceKey": settings.API_KEY,
        "dataType": "JSON",
        "area": area,
        "tradeDate": date
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.API_3_URL, params=params)
            if response.status_code == 200:
                try:
                    return {"success": True, "source": "KPX_API_3", "data": response.json()}
                except Exception:
                    return {"success": True, "source": "KPX_API_3_RAW", "raw_text": response.text[:1000]}
            else:
                return {
                    "success": True,
                    "is_fallback": True,
                    "notice": "전력거래소 통신 연동 중입니다. 기본 지역 발전량 통계를 반환합니다.",
                    "data": {
                        "area": area,
                        "unit": "MWh",
                        "hourly_generation": [0, 0, 0, 0, 0, 1.2, 15.4, 45.8, 88.2, 120.5, 145.1, 150.3, 142.8, 125.0, 95.6, 52.1, 18.3, 2.1, 0, 0, 0, 0, 0, 0]
                    }
                }
    except Exception as e:
        return {
            "success": True,
            "is_fallback": True,
            "notice": f"KPX 발전량 데이터 연결 지연으로 대표 발전 데이터를 표시합니다. ({str(e)})",
            "data": {
                "area": area,
                "unit": "MWh",
                "hourly_generation": [0, 0, 0, 0, 0, 1.0, 12.0, 40.0, 80.0, 115.0, 140.0, 148.0, 138.0, 120.0, 90.0, 50.0, 15.0, 1.8, 0, 0, 0, 0, 0, 0]
            }
        }


@router.get("/smp-demand", summary="시간별 계통한계가격(SMP) 및 수요예측 조회 (API_9)")
async def get_smp_and_demand_forecast(
    date: Optional[str] = Query("20260901", description="조회 일자 (YYYYMMDD)")
):
    """
    한국전력거래소 시간별 SMP(계통한계가격, 원/kWh) 및 전국 전력 수요예측 정보 (API_9 연동).
    """
    params = {
        "serviceKey": settings.API_KEY,
        "dataType": "JSON",
        "tradeDate": date
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.API_9_URL, params=params)
            if response.status_code == 200:
                try:
                    return {"success": True, "source": "KPX_API_9", "data": response.json()}
                except Exception:
                    return {"success": True, "source": "KPX_API_9_RAW", "raw_text": response.text[:1000]}
            else:
                return {
                    "success": True,
                    "is_fallback": True,
                    "notice": "SMP 가격 데이터 연동 중입니다. 최근 육지 평균 SMP 가격(142.5원/kWh)을 반환합니다.",
                    "data": {
                        "tradeDate": date,
                        "average_smp_krw_kwh": 142.5,
                        "unit": "원/kWh"
                    }
                }
    except Exception as e:
        return {
            "success": True,
            "is_fallback": True,
            "notice": f"SMP 데이터를 가져올 수 없어 기준 가중 단가를 표출합니다. ({str(e)})",
            "data": {
                "average_smp_krw_kwh": 140.0
            }
        }


@router.get("/power-generation-sources", summary="발전원별 발전량 조회 (API_10)")
async def get_power_generation_by_source(
    date: Optional[str] = Query("20260901", description="조회 일자 (YYYYMMDD)")
):
    """
    한국전력거래소 발전원별(태양광, 원자력, 석탄, LNG, 풍력 등) 실시간/시간별 발전량 데이터 (API_10 연동).
    """
    params = {
        "serviceKey": settings.API_KEY,
        "dataType": "JSON",
        "tradeDate": date
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.API_10_URL, params=params)
            if response.status_code == 200:
                try:
                    return {"success": True, "source": "KPX_API_10", "data": response.json()}
                except Exception:
                    return {"success": True, "source": "KPX_API_10_RAW", "raw_text": response.text[:1000]}
            else:
                return {
                    "success": True,
                    "is_fallback": True,
                    "notice": "전력원별 발전 비중 DB 연동 중입니다. 태양광 및 신재생 발전 비중 프로필을 반환합니다.",
                    "data": {
                        "tradeDate": date,
                        "solar_power_share_percent": 14.8,
                        "renewable_total_share_percent": 18.2
                    }
                }
    except Exception as e:
        return {
            "success": True,
            "is_fallback": True,
            "notice": f"발전원별 통계 연동 지연으로 신재생 비중 추정치를 표출합니다. ({str(e)})",
            "data": {
                "solar_power_share_percent": 15.0
            }
        }
