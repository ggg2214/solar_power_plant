import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from root backend directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "E-SolarSpot Backend API"
    VERSION: str = "1.0.0"

    API_KEY: str = os.getenv("API_KEY", "")
    VWORLD_API_KEY: str = os.getenv("VWORLD_API_KEY", "F2F85A24-CCED-459C-81FD-1C7AE96F6911" if False else "")
    VWORLD_DOMAIN: str = os.getenv("VWORLD_DOMAIN", "http://www.vworld.kr")
    VWORLD_GEOCODER_URL: str = "https://api.vworld.kr/req/address"
    VWORLD_DATA_URL: str = "https://api.vworld.kr/req/data"
    KMA_API_KEY: str = os.getenv("KMA_API_KEY", "")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")

    # API Endpoints 1~10
    API_1_URL: str = os.getenv("API_1_URL", "https://api.koreaconnect.kr/01/1/2603101713597416530PDP/ENVIRO/B551184/SrQtyService/getSrQtyPredcInfo")
    API_2_URL: str = os.getenv("API_2_URL", "https://api.koreaconnect.kr/01/1/2603101713597416530PDP/CONST/B551184/SolarGhiService/getSolarGhiHrInfo")
    API_3_URL: str = os.getenv("API_3_URL", "https://api.koreaconnect.kr/01/1/2603101713597416530PDP/ENVIRO/B552115/PvAmountByLocHr/getPvAmountByLocHr")
    API_4_URL: str = os.getenv("API_4_URL", "https://api.koreaconnect.kr/01/1/2603101728019668512VW/DEMRES/ned/wfs/getBuildingUseWFS")
    API_5_URL: str = os.getenv("API_5_URL", "https://api.koreaconnect.kr/01/1/2603101728019668512VW/DEMRES/ned/wfs/getGisAggrBuildingWFS")
    API_6_URL: str = os.getenv("API_6_URL", "https://api.koreaconnect.kr/01/1/2603101434213625838HYP/DEMRES/in0005000371")
    API_7_URL: str = os.getenv("API_7_URL", "https://apis.data.go.kr/1360000/AsosDalyInfoService")
    API_8_URL: str = os.getenv("API_8_URL", "https://apis.data.go.kr/1360000/AsosHourlyInfoService")
    API_9_URL: str = os.getenv("API_9_URL", "https://api.koreaconnect.kr/01/1/2603101713597416530PDP/CONST/B552115/SmpWithForecastDemand/getSmpWithForecastDemand")
    API_10_URL: str = os.getenv("API_10_URL", "https://api.koreaconnect.kr/01/1/2603101713597416530PDP/CONST/B552115/PvAmountByPwrGen/getPvAmountByPwrGen")

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

settings = Settings()
