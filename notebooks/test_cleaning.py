import pandas as pd
from analytics.schema_mapper import map_columns
from analytics.data_cleaning import clean_data

file_path = "data/raw/Indian_Customer_Digital_Marketing_Dataset_5000_With_Cost_ROI.xlsx"

df = pd.read_excel(file_path)

df = map_columns(df)
cleaned_df = clean_data(df)

print("📌 Columns AFTER cleaning:")
for col in cleaned_df.columns:
    print("-", col)

print("\n📌 Data types:")
print(cleaned_df.dtypes)

print("\n📌 Sample cleaned data:")
print(cleaned_df.head())
