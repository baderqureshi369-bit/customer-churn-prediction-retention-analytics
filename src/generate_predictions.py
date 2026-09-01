"""
================================================================================
TELCO CUSTOMER CHURN PREDICTION - PHASE 4: PREDICTION & POWER BI DATASET
================================================================================
Script: src/generate_predictions.py
Description:
    Loads the cleaned customer churn dataset and the approved Logistic Regression
    pipeline (models/selected_churn_model.joblib), extracts the 19 primary model
    features (strictly excluding customerID, Churn, Tenure_Group, Monthly_Charge_Range),
    generates calibrated churn probability predictions and classifications for all
    7,043 customers, constructs business-aligned risk tiers, retention priorities,
    deterministic retention actions, and high-risk flags. Exports the 32-column
    analytical dataset, Power BI dimension sort tables, complete data dictionary,
    detailed prediction summary report, and automated 22-point validation report.
================================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib


def generate_retention_action(row):
    """
    Deterministic rule-based recommendation generator based on customer
    risk tier and observable account/service characteristics.
    """
    priority = row['Retention_Priority']
    if priority in ['Priority 1 - Critical', 'Priority 2 - High']:
        actions = []
        if row['Contract'] == 'Month-to-month':
            actions.append("Offer contract upgrade incentive")
        if row['PaymentMethod'] == 'Electronic check':
            actions.append("Promote automatic payment enrollment")
        if row['OnlineSecurity'] == 'No':
            actions.append("Offer security service retention package")
        if row['TechSupport'] == 'No':
            actions.append("Offer technical support retention package")
        
        if not actions:
            actions.append("Engage proactive account review and customized retention offer")
        return "; ".join(actions)
    elif priority == 'Priority 3 - Medium':
        return "Monitor engagement and provide targeted retention offer"
    else:  # Priority 4 - Low
        return "Maintain relationship and monitor satisfaction"


def main():
    print("=" * 80)
    print("STARTING PHASE 4: CHURN PREDICTION GENERATION & POWER BI DATASET PREPARATION")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 0. Setup Directories and File Paths
    # -------------------------------------------------------------------------
    raw_path = os.path.join("data", "raw", "original_dataset.csv")
    cleaned_path = os.path.join("data", "processed", "cleaned_customer_churn.csv")
    model_path = os.path.join("models", "selected_churn_model.joblib")

    powerbi_dir = os.path.join("data", "powerbi")
    pred_output_dir = os.path.join("outputs", "predictions")

    os.makedirs(powerbi_dir, exist_ok=True)
    os.makedirs(pred_output_dir, exist_ok=True)

    analytics_csv_path = os.path.join(powerbi_dir, "customer_churn_analytics.csv")
    data_dict_csv_path = os.path.join(powerbi_dir, "customer_churn_data_dictionary.csv")
    risk_sort_csv_path = os.path.join(powerbi_dir, "risk_category_sort.csv")
    retention_sort_csv_path = os.path.join(powerbi_dir, "retention_priority_sort.csv")
    summary_report_path = os.path.join(pred_output_dir, "phase4_prediction_summary.txt")
    val_report_path = os.path.join(pred_output_dir, "phase4_validation_report.txt")

    # Record timestamps for immutable files
    raw_mtime_before = os.path.getmtime(raw_path) if os.path.exists(raw_path) else None
    cleaned_mtime_before = os.path.getmtime(cleaned_path) if os.path.exists(cleaned_path) else None
    model_mtime_before = os.path.getmtime(model_path) if os.path.exists(model_path) else None

    # -------------------------------------------------------------------------
    # 1. Load Data and Model
    # -------------------------------------------------------------------------
    print("\n--- 1. LOADING DATA AND PRE-TRAINED MODEL ---")
    if not os.path.exists(cleaned_path):
        raise FileNotFoundError(f"Cleaned dataset missing: {cleaned_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Selected model file missing: {model_path}")

    df_cleaned = pd.read_csv(cleaned_path)
    print(f"Cleaned dataset loaded successfully: {df_cleaned.shape[0]} rows, {df_cleaned.shape[1]} columns.")

    model_pipeline = joblib.load(model_path)
    print(f"Model pipeline loaded successfully from: {model_path}")
    print(f"Pipeline components: {model_pipeline.named_steps}")

    # Initial data validations
    assert len(df_cleaned) == 7043, f"Expected 7,043 rows, found {len(df_cleaned)}"
    assert df_cleaned['customerID'].nunique() == 7043, "customerID is not 100% unique!"
    assert df_cleaned.isnull().sum().sum() == 0, "Cleaned dataset contains null values!"

    original_columns = list(df_cleaned.columns)
    assert len(original_columns) == 23, f"Expected 23 original columns, found {len(original_columns)}"

    # -------------------------------------------------------------------------
    # 2. Extract Primary Model Features (19 Features)
    # -------------------------------------------------------------------------
    print("\n--- 2. EXTRACTING PRIMARY MODEL FEATURES ---")
    numerical_features = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges']
    categorical_features = [
        'gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
        'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
        'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
        'PaperlessBilling', 'PaymentMethod'
    ]
    primary_features = numerical_features + categorical_features
    print(f"Total primary features extracted: {len(primary_features)}")

    # Strictly verify exclusions
    excluded_features = ['customerID', 'Churn', 'Tenure_Group', 'Monthly_Charge_Range']
    for feat in excluded_features:
        assert feat not in primary_features, f"Critical error: {feat} is present in model features!"

    X_input = df_cleaned[primary_features].copy()
    print(f"Model input feature matrix shape: {X_input.shape}")

    # -------------------------------------------------------------------------
    # 3. Generate Predictions & Probabilities
    # -------------------------------------------------------------------------
    print("\n--- 3. GENERATING MODEL PREDICTIONS ---")
    # Predict probabilities for Class 1 (Churn = Yes)
    probs = model_pipeline.predict_proba(X_input)[:, 1]
    
    # Predict binary classifications using default 0.50 threshold
    raw_preds = model_pipeline.predict(X_input)
    predicted_churn = np.where(raw_preds == 1, 'Yes', 'No')

    print(f"Probabilities generated: min={probs.min():.4f}, max={probs.max():.4f}, mean={probs.mean():.4f}, median={np.median(probs):.4f}")
    print(f"Predicted Churn (Default threshold): Yes={np.sum(predicted_churn == 'Yes')} ({np.mean(predicted_churn == 'Yes')*100:.2f}%), No={np.sum(predicted_churn == 'No')}")

    # -------------------------------------------------------------------------
    # 4. Construct Analytical & Business Fields
    # -------------------------------------------------------------------------
    print("\n--- 4. CONSTRUCTING ANALYTICAL & BUSINESS FIELDS ---")
    df_analytics = df_cleaned.copy()

    # 1. Predicted_Churn_Probability (exact float between 0 and 1)
    df_analytics['Predicted_Churn_Probability'] = probs

    # 2. Churn_Risk_Percentage (Probability * 100 rounded to 2 decimal places)
    df_analytics['Churn_Risk_Percentage'] = np.round(probs * 100, 2)

    # 3. Predicted_Churn ('Yes' / 'No')
    df_analytics['Predicted_Churn'] = predicted_churn

    # 4. Prediction_Correct ('Yes' / 'No')
    df_analytics['Prediction_Correct'] = np.where(df_analytics['Predicted_Churn'] == df_analytics['Churn'], 'Yes', 'No')

    # 5. Churn_Risk_Category ('Low Risk', 'Medium Risk', 'High Risk')
    risk_conditions = [
        df_analytics['Predicted_Churn_Probability'] < 0.30,
        (df_analytics['Predicted_Churn_Probability'] >= 0.30) & (df_analytics['Predicted_Churn_Probability'] < 0.60),
        df_analytics['Predicted_Churn_Probability'] >= 0.60
    ]
    risk_categories = ['Low Risk', 'Medium Risk', 'High Risk']
    df_analytics['Churn_Risk_Category'] = np.select(risk_conditions, risk_categories, default='Unknown')

    # 6. Churn_Risk_Score (Integer 0 to 100)
    df_analytics['Churn_Risk_Score'] = np.round(probs * 100).astype(int)

    # 7. Retention_Priority
    priority_conditions = [
        df_analytics['Predicted_Churn_Probability'] >= 0.80,
        (df_analytics['Predicted_Churn_Probability'] >= 0.60) & (df_analytics['Predicted_Churn_Probability'] < 0.80),
        (df_analytics['Predicted_Churn_Probability'] >= 0.30) & (df_analytics['Predicted_Churn_Probability'] < 0.60),
        df_analytics['Predicted_Churn_Probability'] < 0.30
    ]
    priority_labels = [
        'Priority 1 - Critical',
        'Priority 2 - High',
        'Priority 3 - Medium',
        'Priority 4 - Low'
    ]
    df_analytics['Retention_Priority'] = np.select(priority_conditions, priority_labels, default='Unknown')

    # 8. Retention_Action (Deterministic recommendations)
    df_analytics['Retention_Action'] = df_analytics.apply(generate_retention_action, axis=1)

    # 9. High_Risk_Flag ('Yes' / 'No')
    df_analytics['High_Risk_Flag'] = np.where(df_analytics['Predicted_Churn_Probability'] >= 0.60, 'Yes', 'No')

    new_columns = [
        'Predicted_Churn_Probability',
        'Churn_Risk_Percentage',
        'Predicted_Churn',
        'Prediction_Correct',
        'Churn_Risk_Category',
        'Churn_Risk_Score',
        'Retention_Priority',
        'Retention_Action',
        'High_Risk_Flag'
    ]
    assert len(new_columns) == 9, "Expected exactly 9 new columns"
    assert df_analytics.shape == (7043, 32), f"Expected shape (7043, 32), got {df_analytics.shape}"

    # -------------------------------------------------------------------------
    # 5. Export Analytical Dataset
    # -------------------------------------------------------------------------
    print("\n--- 5. EXPORTING ANALYTICAL DATASET ---")
    df_analytics.to_csv(analytics_csv_path, index=False)
    print(f"Analytical dataset successfully saved to: {analytics_csv_path}")
    print(f"Rows: {df_analytics.shape[0]}, Columns: {df_analytics.shape[1]}")

    # -------------------------------------------------------------------------
    # 6. Create Power BI Sort Tables
    # -------------------------------------------------------------------------
    print("\n--- 6. CREATING POWER BI SORT TABLES ---")
    df_risk_sort = pd.DataFrame({
        'Risk_Category': ['Low Risk', 'Medium Risk', 'High Risk'],
        'Sort_Order': [1, 2, 3]
    })
    df_risk_sort.to_csv(risk_sort_csv_path, index=False)
    print(f"Risk Category sort table saved to: {risk_sort_csv_path}")

    df_priority_sort = pd.DataFrame({
        'Retention_Priority': [
            'Priority 1 - Critical',
            'Priority 2 - High',
            'Priority 3 - Medium',
            'Priority 4 - Low'
        ],
        'Sort_Order': [1, 2, 3, 4]
    })
    df_priority_sort.to_csv(retention_sort_csv_path, index=False)
    print(f"Retention Priority sort table saved to: {retention_sort_csv_path}")

    # -------------------------------------------------------------------------
    # 7. Create Data Dictionary
    # -------------------------------------------------------------------------
    print("\n--- 7. CREATING COMPREHENSIVE DATA DICTIONARY ---")
    data_dict = [
        # Original 23 Columns
        {"Column_Name": "customerID", "Data_Type": "String", "Category": "Customer Identifier", "Description": "Unique alphanumeric identifier assigned to each telecommunications customer."},
        {"Column_Name": "gender", "Data_Type": "String", "Category": "Demographics", "Description": "Customer gender classification (Female, Male)."},
        {"Column_Name": "SeniorCitizen", "Data_Type": "Integer", "Category": "Demographics", "Description": "Binary indicator indicating if the customer is a senior citizen (1 = Yes, 0 = No)."},
        {"Column_Name": "Partner", "Data_Type": "String", "Category": "Demographics", "Description": "Indicates whether the customer has a domestic partner or spouse (Yes, No)."},
        {"Column_Name": "Dependents", "Data_Type": "String", "Category": "Demographics", "Description": "Indicates whether the customer lives with dependents or children (Yes, No)."},
        {"Column_Name": "tenure", "Data_Type": "Integer", "Category": "Account Information", "Description": "Total number of months the customer has stayed with the company."},
        {"Column_Name": "PhoneService", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates whether the customer subscribes to landline phone service (Yes, No)."},
        {"Column_Name": "MultipleLines", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates if the customer has multiple phone lines (Yes, No, No phone service)."},
        {"Column_Name": "InternetService", "Data_Type": "String", "Category": "Service Information", "Description": "Customer internet service provider technology (DSL, Fiber optic, No)."},
        {"Column_Name": "OnlineSecurity", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates whether the customer subscribes to online security addon (Yes, No, No internet service)."},
        {"Column_Name": "OnlineBackup", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates whether the customer subscribes to cloud backup addon (Yes, No, No internet service)."},
        {"Column_Name": "DeviceProtection", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates whether the customer subscribes to device protection warranty (Yes, No, No internet service)."},
        {"Column_Name": "TechSupport", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates whether the customer subscribes to premium technical support (Yes, No, No internet service)."},
        {"Column_Name": "StreamingTV", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates whether the customer streams television via internet service (Yes, No, No internet service)."},
        {"Column_Name": "StreamingMovies", "Data_Type": "String", "Category": "Service Information", "Description": "Indicates whether the customer streams movies via internet service (Yes, No, No internet service)."},
        {"Column_Name": "Contract", "Data_Type": "String", "Category": "Account Information", "Description": "Contract agreement duration terms (Month-to-month, One year, Two year)."},
        {"Column_Name": "PaperlessBilling", "Data_Type": "String", "Category": "Billing Information", "Description": "Indicates whether customer opted for electronic paperless billing (Yes, No)."},
        {"Column_Name": "PaymentMethod", "Data_Type": "String", "Category": "Billing Information", "Description": "Customer payment disbursement channel (Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic))."},
        {"Column_Name": "MonthlyCharges", "Data_Type": "Float", "Category": "Billing Information", "Description": "The recurring amount billed to the customer each month (in USD)."},
        {"Column_Name": "TotalCharges", "Data_Type": "Float", "Category": "Billing Information", "Description": "The cumulative total charges incurred over the customer tenure (in USD)."},
        {"Column_Name": "Churn", "Data_Type": "String", "Category": "Actual Outcome", "Description": "Actual historical status indicating whether customer churned in last month (Yes, No)."},
        {"Column_Name": "Tenure_Group", "Data_Type": "String", "Category": "Analytical Feature", "Description": "Binned tenure cohort segmentation (0–12 Months, 13–24 Months, 25–48 Months, 49–72 Months)."},
        {"Column_Name": "Monthly_Charge_Range", "Data_Type": "String", "Category": "Analytical Feature", "Description": "Binned monthly charges tier segmentation ($0–$35, $35–$70, $70–$90, $90+)."},
        # 9 New Prediction Columns
        {"Column_Name": "Predicted_Churn_Probability", "Data_Type": "Float", "Category": "Machine Learning Prediction", "Description": "Model-estimated posterior probability of customer churn (continuous float between 0.0000 and 1.0000)."},
        {"Column_Name": "Churn_Risk_Percentage", "Data_Type": "Float", "Category": "Machine Learning Prediction", "Description": "Predicted churn probability expressed as a percentage rounded to 2 decimal places (0.00% to 100.00%)."},
        {"Column_Name": "Predicted_Churn", "Data_Type": "String", "Category": "Machine Learning Prediction", "Description": "Model classification outcome using default 0.50 decision threshold (Yes, No)."},
        {"Column_Name": "Prediction_Correct", "Data_Type": "String", "Category": "Machine Learning Prediction", "Description": "Audit validation flag indicating if model prediction matches actual historical outcome (Yes, No)."},
        {"Column_Name": "Churn_Risk_Category", "Data_Type": "String", "Category": "Risk Segmentation", "Description": "Three-tier probability risk categorization (Low Risk: <0.30, Medium Risk: 0.30-0.59, High Risk: >=0.60)."},
        {"Column_Name": "Churn_Risk_Score", "Data_Type": "Integer", "Category": "Risk Segmentation", "Description": "Calibrated integer risk score scaled from 0 to 100 based on predicted probability."},
        {"Column_Name": "Retention_Priority", "Data_Type": "String", "Category": "Risk Segmentation", "Description": "Four-tier operational prioritization index (Priority 1 - Critical: >=0.80, Priority 2 - High: 0.60-0.79, Priority 3 - Medium: 0.30-0.59, Priority 4 - Low: <0.30)."},
        {"Column_Name": "Retention_Action", "Data_Type": "String", "Category": "Retention Action", "Description": "Rule-based prescriptive retention recommendations mapped to customer risk tier and service configuration."},
        {"Column_Name": "High_Risk_Flag", "Data_Type": "String", "Category": "Risk Segmentation", "Description": "Operational executive filter flag identifying customers with >= 0.60 churn probability (Yes, No)."}
    ]
    df_data_dict = pd.DataFrame(data_dict)
    df_data_dict.to_csv(data_dict_csv_path, index=False)
    print(f"Data dictionary saved to: {data_dict_csv_path} ({len(df_data_dict)} documented columns)")

    # -------------------------------------------------------------------------
    # 8. Generate Phase 4 Statistical Summary
    # -------------------------------------------------------------------------
    print("\n--- 8. GENERATING PREDICTION SUMMARY REPORT ---")
    total_cust = len(df_analytics)
    actual_churn_cnt = int(np.sum(df_analytics['Churn'] == 'Yes'))
    actual_retained_cnt = int(np.sum(df_analytics['Churn'] == 'No'))
    actual_churn_rate = (actual_churn_cnt / total_cust) * 100

    pred_churn_cnt = int(np.sum(df_analytics['Predicted_Churn'] == 'Yes'))
    pred_retained_cnt = int(np.sum(df_analytics['Predicted_Churn'] == 'No'))
    pred_churn_rate = (pred_churn_cnt / total_cust) * 100

    # Risk Categories
    risk_counts = df_analytics['Churn_Risk_Category'].value_counts()
    low_risk_cnt = int(risk_counts.get('Low Risk', 0))
    med_risk_cnt = int(risk_counts.get('Medium Risk', 0))
    high_risk_cnt = int(risk_counts.get('High Risk', 0))

    # Retention Priorities
    prio_counts = df_analytics['Retention_Priority'].value_counts()
    p1_cnt = int(prio_counts.get('Priority 1 - Critical', 0))
    p2_cnt = int(prio_counts.get('Priority 2 - High', 0))
    p3_cnt = int(prio_counts.get('Priority 3 - Medium', 0))
    p4_cnt = int(prio_counts.get('Priority 4 - Low', 0))

    # High Risk Flag
    high_risk_flag_cnt = int(np.sum(df_analytics['High_Risk_Flag'] == 'Yes'))

    # Probability Stats
    prob_mean = float(df_analytics['Predicted_Churn_Probability'].mean())
    prob_median = float(df_analytics['Predicted_Churn_Probability'].median())
    prob_min = float(df_analytics['Predicted_Churn_Probability'].min())
    prob_max = float(df_analytics['Predicted_Churn_Probability'].max())
    prob_std = float(df_analytics['Predicted_Churn_Probability'].std())

    # Top 10 Highest-Risk Customers
    top10_df = df_analytics.sort_values(
        by=['Predicted_Churn_Probability', 'TotalCharges'],
        ascending=[False, False]
    ).head(10)[[
        'customerID', 'Churn', 'Predicted_Churn_Probability',
        'Churn_Risk_Percentage', 'Churn_Risk_Category',
        'Retention_Priority', 'Retention_Action'
    ]]

    # Format Top 10 table
    top10_lines = []
    top10_lines.append(f"{'#':<3} | {'CustomerID':<11} | {'Actual':<6} | {'Prob':<8} | {'Risk %':<7} | {'Category':<11} | {'Priority':<21} | {'Retention Action'}")
    top10_lines.append("-" * 120)
    for idx, (_, row) in enumerate(top10_df.iterrows(), 1):
        top10_lines.append(
            f"{idx:<3} | {row['customerID']:<11} | {row['Churn']:<6} | {row['Predicted_Churn_Probability']:.4f}   | {row['Churn_Risk_Percentage']:>5.2f}% | {row['Churn_Risk_Category']:<11} | {row['Retention_Priority']:<21} | {row['Retention_Action']}"
        )
    top10_formatted_text = "\n".join(top10_lines)

    summary_text = f"""================================================================================
TELCO CUSTOMER CHURN PREDICTION - PHASE 4 PREDICTION SUMMARY REPORT
================================================================================

1. DATASET VOLUME & OVERVIEW
--------------------------------------------------------------------------------
A. Total Customers:                    {total_cust:,}
B. Actual Churned Customers (Yes):     {actual_churn_cnt:,} ({actual_churn_rate:.2f}%)
C. Actual Retained Customers (No):     {actual_retained_cnt:,} ({100 - actual_churn_rate:.2f}%)
D. Actual Churn Rate:                  {actual_churn_rate:.2f}%
E. Predicted Churned Customers (0.50): {pred_churn_cnt:,} ({pred_churn_rate:.2f}%)
   Predicted Retained Customers:       {pred_retained_cnt:,} ({100 - pred_churn_rate:.2f}%)

2. CHURN RISK CATEGORY DISTRIBUTION
--------------------------------------------------------------------------------
F. Risk Segmentation Breakdown:
   - Low Risk    (Prob < 0.30):        {low_risk_cnt:>5,} ({low_risk_cnt/total_cust*100:>5.2f}%)
   - Medium Risk (0.30 <= Prob < 0.60): {med_risk_cnt:>5,} ({med_risk_cnt/total_cust*100:>5.2f}%)
   - High Risk   (Prob >= 0.60):       {high_risk_cnt:>5,} ({high_risk_cnt/total_cust*100:>5.2f}%)
   Total:                              {total_cust:>5,} (100.00%)

3. RETENTION OPERATIONAL PRIORITY DISTRIBUTION
--------------------------------------------------------------------------------
G. Operational Priority Breakdown:
   - Priority 1 - Critical (Prob >= 0.80):        {p1_cnt:>5,} ({p1_cnt/total_cust*100:>5.2f}%)
   - Priority 2 - High     (0.60 <= Prob < 0.80): {p2_cnt:>5,} ({p2_cnt/total_cust*100:>5.2f}%)
   - Priority 3 - Medium   (0.30 <= Prob < 0.60): {p3_cnt:>5,} ({p3_cnt/total_cust*100:>5.2f}%)
   - Priority 4 - Low      (Prob < 0.30):         {p4_cnt:>5,} ({p4_cnt/total_cust*100:>5.2f}%)
   Total:                                         {total_cust:>5,} (100.00%)

H. High Risk Flag Summary:
   - High_Risk_Flag = 'Yes' (Prob >= 0.60): {high_risk_flag_cnt:,} ({high_risk_flag_cnt/total_cust*100:.2f}%)
   - High_Risk_Flag = 'No'  (Prob < 0.60):  {total_cust - high_risk_flag_cnt:,} ({(total_cust - high_risk_flag_cnt)/total_cust*100:.2f}%)

4. PREDICTED CHURN PROBABILITY DISTRIBUTION STATISTICS
--------------------------------------------------------------------------------
I. Average Predicted Churn Probability: {prob_mean:.4f} ({prob_mean*100:.2f}%)
J. Median Predicted Churn Probability:  {prob_median:.4f} ({prob_median*100:.2f}%)
K. Minimum Predicted Churn Probability: {prob_min:.4f} ({prob_min*100:.2f}%)
L. Maximum Predicted Churn Probability: {prob_max:.4f} ({prob_max*100:.2f}%)
   Standard Deviation of Probability:   {prob_std:.4f}

5. TOP 10 HIGHEST-RISK CUSTOMERS
--------------------------------------------------------------------------------
{top10_formatted_text}

================================================================================
END OF SUMMARY REPORT
================================================================================
"""

    with open(summary_report_path, "w") as f:
        f.write(summary_text)
    print(f"Prediction summary report saved to: {summary_report_path}")

    # -------------------------------------------------------------------------
    # 9. Perform 22 Comprehensive Validation Checks
    # -------------------------------------------------------------------------
    print("\n--- 9. RUNNING 22 COMPREHENSIVE VALIDATION CHECKS ---")
    raw_mtime_after = os.path.getmtime(raw_path) if os.path.exists(raw_path) else None
    cleaned_mtime_after = os.path.getmtime(cleaned_path) if os.path.exists(cleaned_path) else None
    model_mtime_after = os.path.getmtime(model_path) if os.path.exists(model_path) else None

    # Verification checks
    v1_raw_unmod = (raw_mtime_before == raw_mtime_after)
    v2_cleaned_unmod = (cleaned_mtime_before == cleaned_mtime_after)
    v3_model_unmod = (model_mtime_before == model_mtime_after)
    v4_input_rows = (len(df_cleaned) == 7043)
    v5_output_rows = (len(df_analytics) == 7043)
    v6_unique_id = (df_analytics['customerID'].nunique() == 7043)
    v7_col_count = (len(df_analytics.columns) == 32)
    v8_orig_preserved = all(col in df_analytics.columns for col in original_columns) and list(df_analytics.columns[:23]) == original_columns
    v9_new_cols_exist = all(col in df_analytics.columns for col in new_columns)
    v10_no_null_prob = (df_analytics['Predicted_Churn_Probability'].isnull().sum() == 0)
    v11_prob_range = ((df_analytics['Predicted_Churn_Probability'] >= 0.0).all() and (df_analytics['Predicted_Churn_Probability'] <= 1.0).all())
    
    # Check v12: Churn_Risk_Percentage equals probability * 100 rounded
    v12_pct_calc = np.allclose(df_analytics['Churn_Risk_Percentage'], np.round(df_analytics['Predicted_Churn_Probability'] * 100, 2), atol=1e-5)
    
    # Check v13: Churn_Risk_Score integer 0 to 100
    v13_score_int = (
        pd.api.types.is_integer_dtype(df_analytics['Churn_Risk_Score']) and
        (df_analytics['Churn_Risk_Score'] >= 0).all() and
        (df_analytics['Churn_Risk_Score'] <= 100).all()
    )
    
    # Check v14: Churn_Risk_Category values
    v14_risk_cats = (set(df_analytics['Churn_Risk_Category'].unique()) == {'Low Risk', 'Medium Risk', 'High Risk'})
    
    # Check v15: Retention_Priority values
    v15_ret_prios = (set(df_analytics['Retention_Priority'].unique()) == {
        'Priority 1 - Critical', 'Priority 2 - High', 'Priority 3 - Medium', 'Priority 4 - Low'
    })
    
    # Check v16: High_Risk_Flag values
    v16_hr_flag = (set(df_analytics['High_Risk_Flag'].unique()) == {'Yes', 'No'})
    
    # Check v17: Predicted_Churn values
    v17_pred_churn = (set(df_analytics['Predicted_Churn'].unique()) == {'Yes', 'No'})
    
    # Check v18: Prediction_Correct values
    v18_pred_correct = (set(df_analytics['Prediction_Correct'].unique()) == {'Yes', 'No'})
    
    # Check v19: Model inputs exclude sensitive/leakage features
    v19_excluded = all(feat not in primary_features for feat in ['customerID', 'Churn', 'Tenure_Group', 'Monthly_Charge_Range'])
    
    # Check v20: CSV opens successfully and no malformed rows
    df_read_check = pd.read_csv(analytics_csv_path)
    v20_csv_valid = (df_read_check.shape == (7043, 32) and df_read_check.isnull().sum().sum() == 0)
    
    # Check v21: Data dictionary contains all 32 columns
    df_dict_check = pd.read_csv(data_dict_csv_path)
    v21_dict_valid = (len(df_dict_check) == 32 and set(df_dict_check['Column_Name']) == set(df_analytics.columns))
    
    # Check v22: Deterministic reproducibility
    re_probs = model_pipeline.predict_proba(df_cleaned[primary_features])[:, 1]
    v22_reproducible = np.allclose(probs, re_probs, atol=1e-9)

    validations = [
        ("1. Raw dataset remains unmodified", v1_raw_unmod, "mtime verified untouched"),
        ("2. Cleaned dataset remains unmodified", v2_cleaned_unmod, "mtime verified untouched"),
        ("3. Selected model file was not modified", v3_model_unmod, "mtime verified untouched"),
        ("4. Input dataset contains 7,043 rows", v4_input_rows, f"{len(df_cleaned)} rows"),
        ("5. Output dataset contains exactly 7,043 rows", v5_output_rows, f"{len(df_analytics)} rows"),
        ("6. customerID remains 100% unique", v6_unique_id, f"{df_analytics['customerID'].nunique()} unique IDs"),
        ("7. Output dataset contains exactly 32 columns", v7_col_count, f"{len(df_analytics.columns)} columns"),
        ("8. All 23 original cleaned dataset columns are preserved", v8_orig_preserved, "All 23 columns present in exact initial order"),
        ("9. All 9 new prediction columns exist", v9_new_cols_exist, f"9 columns created: {', '.join(new_columns)}"),
        ("10. Predicted_Churn_Probability contains no null values", v10_no_null_prob, "0 null values"),
        ("11. Predicted_Churn_Probability values are between 0 and 1", v11_prob_range, f"Range [{prob_min:.4f}, {prob_max:.4f}]"),
        ("12. Churn_Risk_Percentage equals probability * 100 (rounded 2 decimals)", v12_pct_calc, "100% calculation consistency"),
        ("13. Churn_Risk_Score is an integer between 0 and 100", v13_score_int, f"Integer type, range [{df_analytics['Churn_Risk_Score'].min()}, {df_analytics['Churn_Risk_Score'].max()}]"),
        ("14. Churn_Risk_Category contains only Low Risk, Medium Risk, High Risk", v14_risk_cats, f"Categories: {sorted(list(df_analytics['Churn_Risk_Category'].unique()))}"),
        ("15. Retention_Priority contains only the 4 approved values", v15_ret_prios, f"Priorities: {sorted(list(df_analytics['Retention_Priority'].unique()))}"),
        ("16. High_Risk_Flag contains only Yes and No", v16_hr_flag, f"Values: {sorted(list(df_analytics['High_Risk_Flag'].unique()))}"),
        ("17. Predicted_Churn contains only Yes and No", v17_pred_churn, f"Values: {sorted(list(df_analytics['Predicted_Churn'].unique()))}"),
        ("18. Prediction_Correct contains only Yes and No", v18_pred_correct, f"Values: {sorted(list(df_analytics['Prediction_Correct'].unique()))}"),
        ("19. No model input includes customerID, Churn, Tenure_Group, or Monthly_Charge_Range", v19_excluded, "Strictly excluded from X_input"),
        ("20. Output CSV opens successfully with no malformed rows", v20_csv_valid, f"Re-read shape: {df_read_check.shape}, 0 nulls"),
        ("21. Data dictionary contains all 32 columns", v21_dict_valid, f"{len(df_dict_check)}/32 columns documented"),
        ("22. Prediction output is reproducible when rerun", v22_reproducible, "Deterministic 100% match across runs")
    ]

    all_passed = all(status for _, status, _ in validations)

    val_report_lines = []
    val_report_lines.append("=" * 80)
    val_report_lines.append("TELCO CUSTOMER CHURN PREDICTION - PHASE 4 VALIDATION AUDIT REPORT")
    val_report_lines.append("=" * 80)
    val_report_lines.append("")
    val_report_lines.append(f"Overall Status: {'ALL 22 CHECKS PASSED (100% COMPLIANT)' if all_passed else 'VALIDATION FAILURES DETECTED'}")
    val_report_lines.append("-" * 80)
    val_report_lines.append("")

    for desc, status, detail in validations:
        status_str = "PASSED" if status else "FAILED"
        val_report_lines.append(f"[{status_str}] {desc}")
        val_report_lines.append(f"         Detail: {detail}")
        val_report_lines.append("")

    val_report_lines.append("=" * 80)
    val_report_lines.append("END OF VALIDATION REPORT")
    val_report_lines.append("=" * 80)

    val_report_text = "\n".join(val_report_lines)

    with open(val_report_path, "w") as f:
        f.write(val_report_text)
    print(f"Validation report saved to: {val_report_path}")

    print("\n" + "=" * 80)
    print(f"PHASE 4 EXECUTION COMPLETE - STATUS: {'SUCCESS (22/22 PASSED)' if all_passed else 'FAILURE'}")
    print("=" * 80)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
