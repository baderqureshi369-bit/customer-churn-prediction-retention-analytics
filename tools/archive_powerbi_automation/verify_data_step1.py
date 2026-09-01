import pandas as pd
import numpy as np

analytics_path = r"c:\Users\bader\Desktop\CCPRA Project\data\powerbi\customer_churn_analytics.csv"
risk_sort_path = r"c:\Users\bader\Desktop\CCPRA Project\data\powerbi\risk_category_sort.csv"
ret_sort_path = r"c:\Users\bader\Desktop\CCPRA Project\data\powerbi\retention_priority_sort.csv"
dict_path = r"c:\Users\bader\Desktop\CCPRA Project\data\powerbi\customer_churn_data_dictionary.csv"

print("=" * 70)
print("STEP 1: INSPECTION OF PHASE 4 POWER BI DATASETS")
print("=" * 70)

df = pd.read_csv(analytics_path)
print(f"Main Dataset Shape: {df.shape} (Expected: 7043 rows, 32 columns)")
assert df.shape == (7043, 32), f"Unexpected shape {df.shape}"

print("\n--- 32 COLUMNS AND TYPES ---")
for idx, (col, dtype) in enumerate(zip(df.columns, df.dtypes), 1):
    null_count = df[col].isnull().sum()
    unique_count = df[col].nunique()
    sample_val = df[col].iloc[0]
    print(f"{idx:2d}. {col:30s} | dtype: {str(dtype):10s} | nulls: {null_count:4d} | uniques: {unique_count:5d} | sample: {sample_val}")

print("\n--- NULL VALUE CHECK ---")
total_nulls = df.isnull().sum().sum()
print(f"Total null values across all columns: {total_nulls}")
assert total_nulls == 0, f"Found {total_nulls} null values!"

print("\n--- TARGET & PREDICTION METRICS CHECK ---")
print("Actual Churn:")
print(df['Churn'].value_counts())

print("\nPredicted Churn (0.5 threshold):")
print(df['Predicted_Churn'].value_counts())

print("\nHigh Risk Flag:")
print(df['High_Risk_Flag'].value_counts())

print("\nChurn Risk Category:")
print(df['Churn_Risk_Category'].value_counts())

print("\nRetention Priority:")
print(df['Retention_Priority'].value_counts())

print("\nProbability Summary:")
prob = df['Predicted_Churn_Probability']
print(f"Mean:   {prob.mean():.6f} (Expected ~0.2659)")
print(f"Median: {prob.median():.6f} (Expected ~0.1887)")
print(f"Min:    {prob.min():.6f} (Expected ~0.0016)")
print(f"Max:    {prob.max():.6f} (Expected ~0.8555)")
print(f"Std:    {prob.std():.6f} (Expected ~0.2446)")

print("\n--- DIMENSION SORT TABLES CHECK ---")
df_risk = pd.read_csv(risk_sort_path)
print("Risk Category Sort Table:")
print(df_risk)

df_ret = pd.read_csv(ret_sort_path)
print("\nRetention Priority Sort Table:")
print(df_ret)

# Check relationship integrity
risk_diff = set(df['Churn_Risk_Category']) - set(df_risk['Risk_Category'])
print(f"\nUnmatched Churn_Risk_Category in main vs sort table: {risk_diff}")
assert len(risk_diff) == 0

ret_diff = set(df['Retention_Priority']) - set(df_ret['Retention_Priority'])
print(f"Unmatched Retention_Priority in main vs sort table: {ret_diff}")
assert len(ret_diff) == 0

print("\nStep 1 Inspection Completed Successfully! All validations passed perfectly.")
