import pandas as pd

def clean_data(df):
    # Remove duplicates
    df = df.drop_duplicates()

    # Date handling
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Numeric conversions
    numeric_columns = [
        "page_views",
        "session_duration_min",
        "clicks",
        "conversion_value_inr",
        "campaign_cost_inr",
        "roi"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Converted flag → integer
    if "converted" in df.columns:
        df["converted"] = df["converted"].map({"Yes": 1, "No": 0}).fillna(0)

    # Standardized revenue & cost columns (for analytics)
    df["revenue"] = df.get("conversion_value_inr", 0)
    df["cost"] = df.get("campaign_cost_inr", 0)

    # Fill remaining missing values
    df = df.fillna("Unknown")

    return df
