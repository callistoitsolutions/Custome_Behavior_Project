import os
import pandas as pd

from analytics.schema_mapper import map_columns
from analytics.data_cleaning import clean_data
from database.db_config import engine

RAW_DATA_PATH = "data/raw"

SQL_COLUMNS = [
    "customer_id",
    "date",
    "sector",
    "city",
    "traffic_source",
    "device_type",
    "page_views",
    "session_duration_min",
    "clicks",
    "action_type",
    "converted",
    "campaign",
    "campaign_cost_inr",
    "revenue",
    "cost",
    "roi"
]

def ingest_excel_files():
    for file in os.listdir(RAW_DATA_PATH):

        if not file.endswith(".xlsx"):
            continue

        file_path = os.path.join(RAW_DATA_PATH, file)
        print(f"📥 Processing: {file}")

        # SAFE EXCEL LOAD
        df = pd.read_excel(
            file_path,
            engine="openpyxl",
            dtype=str
        )

        # Step 1: map columns
        df = map_columns(df)

        # Step 2: clean & cast data
        df = clean_data(df)

        # Step 6: align schema
        df = df[SQL_COLUMNS]

        # ✅ CHUNKED INSERT (FIX)
        df.to_sql(
            name="analytics_data",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=200
        )

        print(f"✅ Inserted rows: {len(df)}")

    print("\n🎉 All Excel files ingested successfully")

if __name__ == "__main__":
    ingest_excel_files()
