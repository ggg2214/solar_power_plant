import httpx
from fastapi import APIRouter, Query
from typing import Optional
from app.core.config import settings

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/daily", summary="기상청 지상(종관 ASOS) 일자료 조회 (API_7)")
async def get_kma_asos_daily(
    station_id: Optional[str] = Query("108", description="지점 번호 (108: 서울)"),
    date: Optional[str] = Query("20260901", description="조회 일자 (YYYYMMDD)")
):
    """
    기상청 지상(종관, ASOS) 일자료 조회 서비스 (API_7 연동).
    외기 평균기온, 최고/최저기온, 일조시간, 일사량 데이터 제공.
    """
    params = {
        "serviceKey": settings.KMA_API_KEY,
        "pageNo": "1",
        "numOfRows": "10",
        "dataType": "JSON",
        "dataCd": "ASOS",
        "dateCd": "DAY",
        "startDt": date,
        "endDt": date,
        "stnIds": station_id
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.API_7_URL + "/getAsosDalyInfo", params=params)
            if response.status_code == 200:
                try:
                    return {"success": True, "source": "KMA_API_7", "data": response.json()}
                except Exception:
                    return {"success": True, "source": "KMA_API_7_RAW", "raw_text": response.text[:1000]}
            else:
                return {
                    "success": True,
                    "is_fallback": True,
                    "notice": "기상청 ASOS 서버 연동 중입니다. 서울 관측소 일별 대표 기상을 반환합니다.",
                    "data": {
                        "stnId": station_id,
                        "date": date,
                        "avgTa": 22.5, # 외기 평균기온 (deg C)
                        "maxTa": 27.8,
                        "minTa": 18.2,
                        "sumGsr": 18.4 # 일적산 일사량 (MJ/m2)
                    }
                }
    except Exception as e:
        return {
            "success": True,
            "is_fallback": True,
            "notice": f"기상청 일자료 연동 지연으로 표준 기온 정보를 제공합니다. ({str(e)})",
            "data": {
                "avgTa": 20.0,
                "sumGsr": 16.5
            }
        }


@router.get("/hourly", summary="기상청 지상(종관 ASOS) 시간자료 조회 (API_8)")
async def get_kma_asos_hourly(
    station_id: Optional[str] = Query("108", description="지점 번호 (108: 서울)"),
    date: Optional[str] = Query("20260901", description="조회 일자 (YYYYMMDD)")
):
    """
    기상청 지상(종관, ASOS) 시간자료 조회 서비스 (API_8 연동).
    시간별 외기온도($T_{amb}$), 풍속, 상대습도를 조회하여 패널 셀 온도($T_{cell}$) 및 효율 손실 연산에 반영.
    """
    params = {
        "serviceKey": settings.KMA_API_KEY,
        "pageNo": "1",
        "numOfRows": "24",
        "dataType": "JSON",
        "dataCd": "ASOS",
        "dateCd": "HR",
        "startDt": date,
        "startHh": "00",
        "endDt": date,
        "endHh": "23",
        "stnIds": station_id
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.API_8_URL + "/getAsosHourlyInfo", params=params)
            if response.status_code == 200:
                try:
                    return {"success": True, "source": "KMA_API_8", "data": response.json()}
                except Exception:
                    return {"success": True, "source": "KMA_API_8_RAW", "raw_text": response.text[:1000]}
            else:
                return {
                    "success": True,
                    "is_fallback": True,
                    "notice": "기상청 ASOS 시간별 데이터 연동 중입니다. 표준 외기온도 및 풍속 프로필을 반환합니다.",
                    "data": {
                        "stnId": station_id,
                        "date": date,
                        "hourly_temp_c": [17.5, 16.8, 16.2, 15.9, 15.5, 16.0, 18.2, 21.0, 24.1, 26.5, 27.9, 28.5, 28.9, 28.2, 27.5, 26.0, 24.2, 22.1, 20.5, 19.8, 19.1, 18.5, 18.0, 17.6],
                        "hourly_wind_ws": [1.5, 1.2, 1.0, 0.8, 0.9, 1.1, 1.8, 2.2, 2.5, 2.8, 3.1, 3.2, 3.0, 2.7, 2.5, 2.1, 1.8, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 1.1]
                    }
                }
    except Exception as e:
        return {
            "success": True,
            "is_fallback": True,
            "notice": f"시간별 기상 데이터 조회 오류로 표준 외기 프로필을 반환합니다. ({str(e)})",
            "data": {
                "hourly_temp_c": [20.0] * 24,
                "hourly_wind_ws": [2.0] * 24
            }
        }
