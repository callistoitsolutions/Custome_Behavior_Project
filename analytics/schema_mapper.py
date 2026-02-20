# This schema is BASED on your Excel structure
CANONICAL_SCHEMA = {
    "date": ["date"],
    "sector": ["sector"],
    "campaign": ["campaign_name", "campaign"],
    "platform": ["platform", "channel"],
    "cost": ["spend", "cost", "ad_spend"],
    "revenue": ["revenue", "sales"],
    "conversions": ["conversions", "orders", "leads"],
    "users": ["customers", "users", "visitors"],
    "roi": ["roi"]
}

def map_columns(df):
    df.columns = df.columns.str.lower().str.strip()
    column_mapping = {}

    for canonical, variants in CANONICAL_SCHEMA.items():
        for col in df.columns:
            if col in variants:
                column_mapping[col] = canonical

    return df.rename(columns=column_mapping)
