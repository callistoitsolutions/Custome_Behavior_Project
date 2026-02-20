import pandas as pd
from analytics.schema_mapper import map_columns

file_path = "data/raw/Indian_Customer_Digital_Marketing_Dataset_5000_With_Cost_ROI.xlsx"

df = pd.read_excel(file_path)

mapped_df = map_columns(df)

print("📌 Columns AFTER mapping:")
for col in mapped_df.columns:
    print("-", col)

print("\n📌 Sample mapped data:")
print(mapped_df.head())
