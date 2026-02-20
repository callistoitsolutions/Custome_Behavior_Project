import pandas as pd

# Path to your Excel file
file_path = "data/raw/Indian_Customer_Digital_Marketing_Dataset_5000_With_Cost_ROI.xlsx"

# Read Excel
df = pd.read_excel(file_path)

# Basic checks
print("✅ Excel loaded successfully\n")
print("Shape (rows, columns):", df.shape)

print("\n📌 Column names:")
for col in df.columns:
    print("-", col)

print("\n📌 Sample data:")
print(df.head(5))
