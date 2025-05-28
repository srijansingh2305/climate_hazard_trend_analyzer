import httpx
import pandas as pd
import numpy as np
from datetime import datetime
import logging

from scipy.stats import linregress
import pymannkendall as mk

from climate_hazard_detection import (
    detect_heatwaves,
    detect_flood_events,
    detect_drought,
)

logger = logging.getLogger(__name__)


async def fetch_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "precipitation_sum"],
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            df = pd.DataFrame({
                "date": data["daily"]["time"],
                "temp_max": data["daily"]["temperature_2m_max"],
                "precipitation": data["daily"]["precipitation_sum"]
            })
            df["date"] = pd.to_datetime(df["date"])
            return df
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from Open-Meteo: {e}")
        raise HTTPException(status_code=502, detail=f"Weather data fetch failed for {start_date}–{end_date}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data.")



def analyze_trend_summary(trends, hazard_name, threshold, year_range):
    years = [t["year"] for t in trends]
    freq = [t["frequency"] for t in trends]

    slope, intercept, r_value, p_value, std_err = linregress(years, freq)
    trend_label = "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat"
    linreg_summary = (
        f" Linear regression shows a {trend_label} trend "
        f"(slope={slope:.2f}, R²={r_value**2:.2f}, p={p_value:.3f})."
    )

    mk_result = mk.original_test(freq)
    mk_summary = (
        f" Mann-Kendall trend test shows a '{mk_result.trend}' trend "
        f"(p={mk_result.p:.3f}, tau={mk_result.Tau:.2f})."
    )

    return linreg_summary + mk_summary


async def analyze_heatwaves(bounds, year_range, threshold):
    lat = (bounds[0] + bounds[2]) / 2
    lon = (bounds[1] + bounds[3]) / 2

    trends = []

    for year in range(year_range["start"], year_range["end"] + 1):
        df = await fetch_weather(lat, lon, f"{year}-01-01", f"{year}-12-31")
        if df is None or df.empty:
            continue
        heatwave_periods, _ = detect_heatwaves(df, threshold=threshold)
        trends.append({"year": year, "frequency": len(heatwave_periods)})

    logger.info(f"Heatwave trends: {trends}")

    if not trends:
        summary = "No data available for the selected years and location."
        return [], summary

    frequencies = [t["frequency"] for t in trends]
    first_half = frequencies[:len(frequencies) // 2]
    second_half = frequencies[len(frequencies) // 2:]

    avg_first = np.mean(first_half)
    avg_second = np.mean(second_half)

    increase = avg_second - avg_first
    if avg_first == 0:
        percent = 100 if avg_second > 0 else 0
    else:
        percent = (increase / avg_first) * 100

    direction = "increased" if percent >= 0 else "decreased"
    summary = (
        f"Heatwaves (temp > {threshold}°C) have {direction} by "
        f"{abs(int(percent))}% on average in this region between "
        f"{year_range['start']} and {year_range['end']}."
    )

    summary += analyze_trend_summary(trends, "heatwaves", threshold, year_range)

    return trends, summary


async def analyze_rainfall(bounds, year_range, threshold):
    lat = (bounds[0] + bounds[2]) / 2
    lon = (bounds[1] + bounds[3]) / 2
    trends = []

    for year in range(year_range["start"], year_range["end"] + 1):
        df = await fetch_weather(lat, lon, f"{year}-01-01", f"{year}-12-31")
        heavy_rain_days = df[df["precipitation"] > threshold]
        trends.append({"year": year, "frequency": len(heavy_rain_days)})

    increase = trends[-1]["frequency"] - trends[0]["frequency"]
    if trends[0]["frequency"] == 0:
        percent = 100 if trends[-1]["frequency"] > 0 else 0
    else:
        percent = (increase / trends[0]["frequency"]) * 100

    direction = "increased" if percent >= 0 else "decreased"
    summary = (
        f"Heavy rainfall days (>{threshold}mm) have {direction} by "
        f"{abs(int(percent))}% since {year_range['start']}."
    )

    summary += analyze_trend_summary(trends, "rainfall", threshold, year_range)
    return trends, summary


async def analyze_flood(bounds, year_range, threshold):
    lat = (bounds[0] + bounds[2]) / 2
    lon = (bounds[1] + bounds[3]) / 2
    trends = []

    for year in range(year_range["start"], year_range["end"] + 1):
        df = await fetch_weather(lat, lon, f"{year}-01-01", f"{year}-12-31")
        flood_periods = detect_flood_events(df, threshold=threshold)
        trends.append({"year": year, "frequency": len(flood_periods)})

    increase = trends[-1]["frequency"] - trends[0]["frequency"]
    if trends[0]["frequency"] == 0:
        percent = 100 if trends[-1]["frequency"] > 0 else 0
    else:
        percent = (increase / trends[0]["frequency"]) * 100

    direction = "increased" if percent >= 0 else "decreased"
    summary = (
        f"Flood-risk days (rain > {threshold}mm) have {direction} by "
        f"{abs(int(percent))}% since {year_range['start']}."
    )

    summary += analyze_trend_summary(trends, "flood", threshold, year_range)
    return trends, summary


async def analyze_drought(bounds, year_range, threshold=50):
    lat = (bounds[0] + bounds[2]) / 2
    lon = (bounds[1] + bounds[3]) / 2

    start_date = f"{year_range['start']}-01-01"
    end_date = f"{year_range['end']}-12-31"
    df = await fetch_weather(lat, lon, start_date, end_date)

    drought_periods = detect_drought(df, deficit_threshold=threshold, window_months=3)

    trends = []
    for year in range(year_range["start"], year_range["end"] + 1):
        count = sum(
            1 for start, end in drought_periods
            if (start.year == year) or (end.year == year) or
               (start.year < year < end.year)
        )
        trends.append({"year": year, "frequency": count})

    increase = trends[-1]["frequency"] - trends[0]["frequency"]
    if trends[0]["frequency"] == 0:
        percent = 100 if trends[-1]["frequency"] > 0 else 0
    else:
        percent = (increase / trends[0]["frequency"]) * 100

    direction = "increased" if percent >= 0 else "decreased"
    summary = (
        f"Drought periods (3-month rolling precipitation < {threshold}mm) "
        f"have {direction} by {abs(int(percent))}% since {year_range['start']}."
    )

    summary += analyze_trend_summary(trends, "drought", threshold, year_range)
    return trends, summary


async def get_heatwave_threshold(bounds, year_range, percentile=95):
    lat = (bounds[0] + bounds[2]) / 2
    lon = (bounds[1] + bounds[3]) / 2
    start_date = f"{year_range['start']}-01-01"
    end_date = f"{year_range['end']}-12-31"

    df = await fetch_weather(lat, lon, start_date, end_date)
    threshold = np.percentile(df["temp_max"], percentile)

    return {"percentile": percentile, "threshold": round(float(threshold), 2)}