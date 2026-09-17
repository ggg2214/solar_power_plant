import math
from datetime import datetime, timezone
from typing import Dict, Any, List

try:
    import pvlib
    import pandas as pd
    import numpy as np
    PVLIB_AVAILABLE = True
except ImportError:
    PVLIB_AVAILABLE = False

class SolarSimulationEngine:
    """
    Solar simulation engine supporting pvlib-python calculation and mathematical fallbacks.
    Calculates plane of array (POA) irradiance, cell temperature loss, shadow loss, and total kWh.
    """

    @staticmethod
    def calculate_sun_position(lat: float, lon: float, date_time: datetime) -> Dict[str, float]:
        """
        Calculate solar zenith and azimuth angles for a given coordinate and datetime.
        """
        if PVLIB_AVAILABLE:
            times = pd.date_range(start=date_time, periods=1, freq='1h', tz='Asia/Seoul')
            solpos = pvlib.solarposition.get_solarposition(times, lat, lon)
            zenith = float(solpos['zenith'].iloc[0])
            azimuth = float(solpos['azimuth'].iloc[0])
            elevation = float(solpos['elevation'].iloc[0])
            return {"zenith": round(zenith, 2), "azimuth": round(azimuth, 2), "elevation": round(elevation, 2)}
        else:
            # Mathematical approximation for solar position
            day_of_year = date_time.timetuple().tm_yday
            hour = date_time.hour + date_time.minute / 60.0
            
            # Declination angle
            declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
            
            # Solar hour angle
            lstm = 135.0  # KST Meridian
            tc = 4 * (lon - lstm)
            local_solar_time = hour + (tc / 60.0)
            hra = 15 * (local_solar_time - 12)
            
            lat_rad = math.radians(lat)
            dec_rad = math.radians(declination)
            hra_rad = math.radians(hra)
            
            elevation_rad = math.asin(
                math.sin(lat_rad) * math.sin(dec_rad) +
                math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hra_rad)
            )
            elevation = math.degrees(elevation_rad)
            zenith = 90.0 - elevation
            
            if elevation > 0:
                cos_azimuth = (math.sin(dec_rad) * math.cos(lat_rad) - math.cos(dec_rad) * math.sin(lat_rad) * math.cos(hra_rad)) / math.cos(elevation_rad)
                cos_azimuth = max(-1.0, min(1.0, cos_azimuth))
                azimuth = math.degrees(math.acos(cos_azimuth))
                if hra > 0:
                    azimuth = 360.0 - azimuth
            else:
                azimuth = 180.0

            return {"zenith": round(max(0, zenith), 2), "azimuth": round(azimuth, 2), "elevation": round(max(0, elevation), 2)}

    @classmethod
    def estimate_daily_annual_generation(
        cls,
        lat: float,
        lon: float,
        capacity_kw: float,
        panel_tilt: float = 30.0,
        panel_azimuth: float = 180.0,
        module_efficiency: float = 0.20,
        inverter_efficiency: float = 0.96,
        shadow_loss_percent: float = 5.0,
        ambient_temp_avg: float = 15.0
    ) -> Dict[str, Any]:
        """
        Simulates annual power output (kWh), monthly breakdown, ROI and CO2 reduction.
        """
        # Average peak sun hours for Korea: ~3.5 to 3.8 hours/day depending on tilt/azimuth
        tilt_rad = math.radians(panel_tilt)
        azimuth_diff_rad = math.radians(abs(panel_azimuth - 180.0))
        
        # Tilt factor (optimal tilt angle in Korea is around 30-35 deg facing South)
        tilt_factor = math.cos(tilt_rad - math.radians(lat - 37.5)) * math.cos(azimuth_diff_rad * 0.5)
        tilt_factor = max(0.7, min(1.15, tilt_factor))
        
        base_peak_hours = 3.65 * tilt_factor
        
        # Cell temperature derating: ~ -0.38% / deg C over standard test condition (25 deg C)
        noct = 45.0
        avg_cell_temp = ambient_temp_avg + ((noct - 20) / 800) * 800
        temp_loss_coef = -0.0038
        temp_derate = 1.0 + temp_loss_coef * (avg_cell_temp - 25.0)
        temp_derate = max(0.85, min(1.0, temp_derate))
        
        # Total efficiency factor
        effective_shadow_loss = max(0.0, min(80.0, shadow_loss_percent)) / 100.0
        system_derate = (1.0 - effective_shadow_loss) * temp_derate * (inverter_efficiency) * 0.95  # 5% cabling/soiling loss
        
        daily_kwh = capacity_kw * base_peak_hours * system_derate
        annual_kwh = daily_kwh * 365.0

        # Monthly breakdown (seasonal weighting: Spring/Autumn higher, Summer monsoon slightly lower, Winter lower)
        monthly_weights = [0.075, 0.082, 0.095, 0.098, 0.102, 0.088, 0.078, 0.082, 0.089, 0.091, 0.072, 0.048]
        monthly_kwh = [round(annual_kwh * w, 1) for w in monthly_weights]

        # Financial estimate (SMP ~ 130 KRW/kWh, REC ~ 70 KRW/kWh -> Total ~ 200 KRW/kWh)
        estimated_tariff_per_kwh = 200 # KRW
        annual_revenue_krw = annual_kwh * estimated_tariff_per_kwh
        estimated_capex_krw = capacity_kw * 1_400_000 # 1.4 million KRW per kW
        simple_payback_years = round(estimated_capex_krw / annual_revenue_krw, 1) if annual_revenue_krw > 0 else 0

        # Environmental impact (0.478 kg CO2 per kWh)
        co2_reduction_kg = round(annual_kwh * 0.478, 1)
        tree_equivalent = round(co2_reduction_kg / 6.6, 0) # 1 tree absorbs ~6.6 kg CO2/year

        return {
            "capacity_kw": capacity_kw,
            "panel_tilt": panel_tilt,
            "panel_azimuth": panel_azimuth,
            "daily_kwh": round(daily_kwh, 2),
            "annual_kwh": round(annual_kwh, 1),
            "monthly_kwh": monthly_kwh,
            "shadow_loss_percent": shadow_loss_percent,
            "system_efficiency_percent": round(system_derate * 100, 1),
            "financial": {
                "estimated_capex_krw": int(estimated_capex_krw),
                "annual_revenue_krw": int(annual_revenue_krw),
                "simple_payback_years": simple_payback_years
            },
            "environmental": {
                "co2_reduction_kg": co2_reduction_kg,
                "tree_equivalent_count": int(tree_equivalent)
            }
        }
