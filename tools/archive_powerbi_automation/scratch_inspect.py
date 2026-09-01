import os
import sys
import pandas as pd
import numpy as np

raw_path = r"c:\Users\bader\Desktop\CCPRA Project\data\raw\original_dataset.csv"

if not os.path.exists(raw_path):
    print(f"Error: File not found at {raw_path}")
    sys.exit(1)

df = pd.read_csv(raw_path)

print("="*60)
print("DATASET PROFILING REPORT")
print("="*60)
print(f"File name: original_dataset.csv")
print(f"Number of rows: {df.shape[0]}")
print(f"Number of columns: {df.shape[1]}")
print(f"Column names: {list(df.columns)}")
print("\n--- Data Types ---")
print(df.dtypes)

print("\n--- Missing Values Per Column ---")
missing = df.isnull().sum()
print(missing)

# Check for whitespace strings or empty strings in object columns
print("\n--- Whitespace / Blank String Count in Object Columns ---")
for col in df.select_dtypes(include='object').columns:
    blank_cnt = (df[col].astype(str).str.strip() == '').sum()
    if blank_cnt > 0:
        print(f"{col}: {blank_cnt} blank/empty string rows")

print(f"\nDuplicate rows: {df.duplicated().sum()}")

if 'customerID' in df.columns:
    print(f"Unique Customer IDs: {df['customerID'].nunique()} (Total rows: {len(df)})")
elif 'CustomerID' in df.columns:
    print(f"Unique Customer IDs: {df['CustomerID'].nunique()} (Total rows: {len(df)})")
else:
    print("Customer ID column check:", [c for c in df.columns if 'id' in c.lower()])

print("\n--- Unique Values for Categorical Columns ---")
for col in df.select_dtypes(include='object').columns:
    if col.lower() not in ['customerid', 'customer_id']:
        print(f"{col} ({df[col].nunique()} unique): {df[col].unique().tolist()[:10]}")

print("\n--- Summary Statistics for Numeric Columns ---")
print(df.describe().to_string())

# Target distribution
target_cols = [c for c in df.columns if 'churn' in c.lower()]
print(f"\n--- Target Distribution ({target_cols}) ---")
for c in target_cols:
    print(df[c].value_counts(dropna=False))
    print(df[c].value_counts(normalize=True, dropna=False) * 100)
