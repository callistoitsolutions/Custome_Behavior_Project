import pandas as pd

# =====================================================
# CANONICAL SCHEMA (Database Columns)
# =====================================================

CANONICAL_SCHEMA = {

    "date": [
        "date"
    ],

    "sector": [
        "sector",
        "industry"
    ],

    "city": [
        "city",
        "location"
    ],

    "traffic_source": [
        "traffic_source",
        "traffic source",
        "channel",
        "platform"
    ],

    "device_type": [
        "device_type",
        "device type",
        "device"
    ],

    "page_views": [
        "page_views",
        "page views",
        "views"
    ],

    "session_duration_min": [
        "session_duration_min",
        "session duration",
        "session_time"
    ],

    "clicks": [
        "clicks"
    ],

    "action_type": [
        "action_type",
        "action",
        "event_type"
    ],

    "converted": [
        "converted",
        "conversion",
        "is_converted"
    ],

    "campaign": [
        "campaign",
        "campaign_name",
        "campaign name"
    ],

    "campaign_cost_inr": [
        "campaign_cost_inr",
        "campaign cost",
        "spend",
        "ad_spend"
    ],

    "revenue": [
        "revenue",
        "conversion_value_inr",
        "sales"
    ],

    "cost": [
        "cost",
        "expense"
    ],

    "roi": [
        "roi"
    ]
}


# =====================================================
# COLUMN NORMALIZATION
# =====================================================

def normalize_columns(df):

    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df


# =====================================================
# SCHEMA MAPPING
# =====================================================

def map_columns(df):

    # Normalize column names
    df = normalize_columns(df)

    column_mapping = {}

    for canonical, variants in CANONICAL_SCHEMA.items():
        for variant in variants:

            variant = variant.replace(" ", "_").lower()

            if variant in df.columns:
                column_mapping[variant] = canonical

    df = df.rename(columns=column_mapping)

    return df
