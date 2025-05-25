import pandas as pd
import numpy as np

def detect_heatwaves(df, temp_col="temp_max", threshold=33.8, min_days=3):
    df = df.sort_values("date").reset_index(drop=True)
    df["heatwave_day"] = df[temp_col] > threshold

    # Find consecutive sequences of heatwave days
    df["group"] = (df["heatwave_day"] != df["heatwave_day"].shift()).cumsum()
    groups = df.groupby("group")

    heatwave_periods = []
    for _, group in groups:
        if group["heatwave_day"].iloc[0] and len(group) >= min_days:
            start_date = group["date"].iloc[0]
            end_date = group["date"].iloc[-1]
            heatwave_periods.append((start_date, end_date))

    # Optional: return all heatwave days (not just consecutive sequences)
    heatwave_days = df[df["heatwave_day"]]

    return heatwave_periods, heatwave_days

def detect_flood_events(df, rain_col="precipitation", threshold=50, min_duration=1):
    df = df.sort_values("date").reset_index(drop=True)
    df["heavy_rain_day"] = df[rain_col] > threshold

    df["group"] = (df["heavy_rain_day"] != df["heavy_rain_day"].shift()).cumsum()
    flood_periods = []
    for _, group in df.groupby("group"):
        if group["heavy_rain_day"].iloc[0] and len(group) >= min_duration:
            start_date = group["date"].iloc[0]
            end_date = group["date"].iloc[-1]
            flood_periods.append((start_date, end_date))

    return flood_periods


def detect_drought(df, rain_col="precipitation", deficit_threshold=50, window_months=3):
    df = df.sort_values("date").reset_index(drop=True)

    # If daily data, convert to monthly sums:
    df['month'] = df['date'].dt.to_period('M')
    monthly_rain = df.groupby('month')[rain_col].sum().reset_index()
    monthly_rain['month'] = monthly_rain['month'].dt.to_timestamp()

    monthly_rain['rolling_sum'] = monthly_rain[rain_col].rolling(window=window_months).sum()

    droughts = monthly_rain[monthly_rain['rolling_sum'] < deficit_threshold]

    # Identify consecutive drought months
    droughts['group'] = (droughts['month'].diff() != pd.offsets.MonthBegin(1)).cumsum()
    drought_periods = []
    for _, group in droughts.groupby('group'):
        start_date = group['month'].iloc[0]
        end_date = group['month'].iloc[-1]
        drought_periods.append((start_date, end_date))

    return drought_periods

def calculate_percentile_threshold(df, temp_col="temp_max", percentile=95):
    threshold = np.percentile(df[temp_col], percentile)
    return threshold

