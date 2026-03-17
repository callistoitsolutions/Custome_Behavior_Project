import pandas as pd


def clean_data(df):

    # ------------------------------------------------
    # Remove duplicates
    # ------------------------------------------------
    df = df.drop_duplicates()

    # ------------------------------------------------
    # Date handling
    # ------------------------------------------------
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ------------------------------------------------
    # Numeric columns
    # ------------------------------------------------
    numeric_columns = [
        "page_views",
        "session_duration_min",
        "clicks",
        "campaign_cost_inr",
        "revenue",
        "cost",
        "roi"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ------------------------------------------------
    # Converted column (Yes/No → 1/0)
    # ------------------------------------------------
    if "converted" in df.columns:
        df["converted"] = df["converted"].replace({
            "Yes": 1,
            "No": 0,
            "yes": 1,
            "no": 0
        })
        df["converted"] = pd.to_numeric(df["converted"], errors="coerce").fillna(0)

    # ------------------------------------------------
    # Ensure cost column exists
    # ------------------------------------------------
    if "cost" not in df.columns and "campaign_cost_inr" in df.columns:
        df["cost"] = df["campaign_cost_inr"]

    # ------------------------------------------------
    # Fill missing text fields
    # ------------------------------------------------
    text_columns = [
        "sector",
        "city",
        "traffic_source",
        "device_type",
        "action_type",
        "campaign"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df
