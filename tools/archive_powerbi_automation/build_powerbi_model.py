"""
CCPRA Power BI Model Builder
Generates TMSL JSON for the complete data model and deploys it to the running PBI Desktop instance.
"""

import json
import os
import subprocess
import sys

# Configuration
PROJECT_ROOT = r"C:\Users\bader\Desktop\CCPRA Project"
POWERBI_DATA = os.path.join(PROJECT_ROOT, "data", "powerbi")
CSV_MAIN = os.path.join(POWERBI_DATA, "customer_churn_analytics.csv")
CSV_RISK = os.path.join(POWERBI_DATA, "risk_category_sort.csv")
CSV_RET = os.path.join(POWERBI_DATA, "retention_priority_sort.csv")
DATABASE_ID = "3b747c39-23bb-417d-96e0-e976777f0047"
COMPAT_LEVEL = 1606


def build_m_expression(csv_path, columns_types):
    """Build a Power Query M expression for importing a CSV file."""
    escaped = csv_path.replace("\\", "\\\\")

    type_lines = []
    for col_name, col_type in columns_types:
        if col_type == "text":
            type_lines.append(f'        {{"{col_name}", type text}}')
        elif col_type == "int64":
            type_lines.append(f'        {{"{col_name}", Int64.Type}}')
        elif col_type == "double":
            type_lines.append(f'        {{"{col_name}", type number}}')

    types_str = ",\n".join(type_lines)

    return (
        f'let\n'
        f'    Source = Csv.Document(File.Contents("{escaped}"), '
        f'[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),\n'
        f'    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
        f'    Types = Table.TransformColumnTypes(Headers, {{\n'
        f'{types_str}\n'
        f'    }})\n'
        f'in\n'
        f'    Types'
    )


def build_tmsl():
    """Build the complete TMSL model definition."""

    # ========================================================================
    # MAIN TABLE: customer_churn_analytics
    # ========================================================================
    main_col_defs = [
        ("customerID", "string", "text", None, None),
        ("gender", "string", "text", None, None),
        ("SeniorCitizen", "int64", "int64", None, None),
        ("Partner", "string", "text", None, None),
        ("Dependents", "string", "text", None, None),
        ("tenure", "int64", "int64", None, None),
        ("PhoneService", "string", "text", None, None),
        ("MultipleLines", "string", "text", None, None),
        ("InternetService", "string", "text", None, None),
        ("OnlineSecurity", "string", "text", None, None),
        ("OnlineBackup", "string", "text", None, None),
        ("DeviceProtection", "string", "text", None, None),
        ("TechSupport", "string", "text", None, None),
        ("StreamingTV", "string", "text", None, None),
        ("StreamingMovies", "string", "text", None, None),
        ("Contract", "string", "text", None, None),
        ("PaperlessBilling", "string", "text", None, None),
        ("PaymentMethod", "string", "text", None, None),
        ("MonthlyCharges", "double", "double", "$#,##0.00", None),
        ("TotalCharges", "double", "double", "$#,##0.00", None),
        ("Churn", "string", "text", None, None),
        ("Tenure_Group", "string", "text", None, None),
        ("Monthly_Charge_Range", "string", "text", None, None),
        ("Predicted_Churn_Probability", "double", "double", "0.0000", None),
        ("Churn_Risk_Percentage", "double", "double", "0.00", None),
        ("Predicted_Churn", "string", "text", None, None),
        ("Prediction_Correct", "string", "text", None, None),
        ("Churn_Risk_Category", "string", "text", None, "Risk_Sort_Order"),
        ("Churn_Risk_Score", "int64", "int64", None, None),
        ("Retention_Priority", "string", "text", None, "Retention_Sort_Order"),
        ("Retention_Action", "string", "text", None, None),
        ("High_Risk_Flag", "string", "text", None, None),
    ]

    # Build TMSL columns
    main_columns = []
    for name, data_type, m_type, fmt, sort_by in main_col_defs:
        col = {
            "name": name,
            "dataType": data_type,
            "sourceColumn": name,
        }
        if fmt:
            col["formatString"] = fmt
        if sort_by:
            col["sortByColumn"] = sort_by
        main_columns.append(col)

    # Add hidden calculated columns for sorting
    main_columns.append({
        "type": "calculated",
        "name": "Risk_Sort_Order",
        "dataType": "int64",
        "expression": "RELATED(risk_category_sort[Sort_Order])",
        "isHidden": True,
    })
    main_columns.append({
        "type": "calculated",
        "name": "Retention_Sort_Order",
        "dataType": "int64",
        "expression": "RELATED(retention_priority_sort[Sort_Order])",
        "isHidden": True,
    })

    # Build M expression for main table
    main_m_cols = [(name, m_type) for name, _, m_type, _, _ in main_col_defs]
    main_m_expr = build_m_expression(CSV_MAIN, main_m_cols)

    # ========================================================================
    # DAX MEASURES
    # ========================================================================
    measures = [
        # Core KPIs
        ("Total Customers", "COUNTROWS(customer_churn_analytics)", "#,##0"),
        ("Actual Churned Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Churn] = "Yes")', "#,##0"),
        ("Actual Retained Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Churn] = "No")', "#,##0"),
        ("Actual Churn Rate", "DIVIDE([Actual Churned Customers], [Total Customers], 0)", "0.00%"),
        ("Predicted Churn Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Predicted_Churn] = "Yes")', "#,##0"),
        ("Predicted Retained Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Predicted_Churn] = "No")', "#,##0"),
        ("Predicted Churn Rate", "DIVIDE([Predicted Churn Customers], [Total Customers], 0)", "0.00%"),

        # Risk KPIs
        ("High Risk Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[High_Risk_Flag] = "Yes")', "#,##0"),
        ("High Risk Rate", "DIVIDE([High Risk Customers], [Total Customers], 0)", "0.00%"),

        # Priority KPIs
        ("Critical Priority Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Retention_Priority] = "Priority 1 - Critical")', "#,##0"),
        ("High Priority Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Retention_Priority] = "Priority 2 - High")', "#,##0"),
        ("Medium Priority Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Retention_Priority] = "Priority 3 - Medium")', "#,##0"),
        ("Low Priority Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Retention_Priority] = "Priority 4 - Low")', "#,##0"),

        # Probability statistics
        ("Average Churn Probability", "AVERAGE(customer_churn_analytics[Predicted_Churn_Probability])", "0.00%"),
        ("Median Churn Probability", "MEDIAN(customer_churn_analytics[Predicted_Churn_Probability])", "0.00%"),
        ("Max Churn Probability", "MAX(customer_churn_analytics[Predicted_Churn_Probability])", "0.00%"),
        ("Min Churn Probability", "MIN(customer_churn_analytics[Predicted_Churn_Probability])", "0.00%"),

        # Financial metrics
        ("Average Monthly Charges", "AVERAGE(customer_churn_analytics[MonthlyCharges])", "$#,##0.00"),
        ("Average Tenure", "AVERAGE(customer_churn_analytics[tenure])", "#,##0.0"),
        ("Average Total Charges", "AVERAGE(customer_churn_analytics[TotalCharges])", "$#,##0.00"),
        ("Total Monthly Revenue", "SUM(customer_churn_analytics[MonthlyCharges])", "$#,##0.00"),
        ("At-Risk Revenue", 'CALCULATE(SUM(customer_churn_analytics[MonthlyCharges]), customer_churn_analytics[High_Risk_Flag] = "Yes")', "$#,##0.00"),
        ("Churned Customer Revenue", 'CALCULATE(SUM(customer_churn_analytics[MonthlyCharges]), customer_churn_analytics[Churn] = "Yes")', "$#,##0.00"),

        # Model performance
        ("Correct Predictions", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Prediction_Correct] = "Yes")', "#,##0"),
        ("Incorrect Predictions", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Prediction_Correct] = "No")', "#,##0"),
        ("Prediction Accuracy", "DIVIDE([Correct Predictions], [Total Customers], 0)", "0.00%"),

        # Additional measures
        ("Churn Probability Average %", "AVERAGE(customer_churn_analytics[Churn_Risk_Percentage])", "0.00"),
        ("Average Risk Score", "AVERAGE(customer_churn_analytics[Churn_Risk_Score])", "0.0"),

        # Confusion matrix components
        ("True Positives", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Churn] = "Yes", customer_churn_analytics[Predicted_Churn] = "Yes")', "#,##0"),
        ("True Negatives", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Churn] = "No", customer_churn_analytics[Predicted_Churn] = "No")', "#,##0"),
        ("False Positives", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Churn] = "No", customer_churn_analytics[Predicted_Churn] = "Yes")', "#,##0"),
        ("False Negatives", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[Churn] = "Yes", customer_churn_analytics[Predicted_Churn] = "No")', "#,##0"),

        # Customer segment counts
        ("Senior Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[SeniorCitizen] = 1)', "#,##0"),
        ("Non-Senior Customers", 'CALCULATE(COUNTROWS(customer_churn_analytics), customer_churn_analytics[SeniorCitizen] = 0)', "#,##0"),
    ]

    measures_json = []
    for name, expr, fmt in measures:
        m = {"name": name, "expression": expr}
        if fmt:
            m["formatString"] = fmt
        measures_json.append(m)

    # ========================================================================
    # DIMENSION TABLE: risk_category_sort
    # ========================================================================
    risk_m_expr = build_m_expression(CSV_RISK, [("Risk_Category", "text"), ("Sort_Order", "int64")])
    risk_columns = [
        {"name": "Risk_Category", "dataType": "string", "sourceColumn": "Risk_Category", "sortByColumn": "Sort_Order"},
        {"name": "Sort_Order", "dataType": "int64", "sourceColumn": "Sort_Order", "isHidden": True},
    ]

    # ========================================================================
    # DIMENSION TABLE: retention_priority_sort
    # ========================================================================
    ret_m_expr = build_m_expression(CSV_RET, [("Retention_Priority", "text"), ("Sort_Order", "int64")])
    ret_columns = [
        {"name": "Retention_Priority", "dataType": "string", "sourceColumn": "Retention_Priority", "sortByColumn": "Sort_Order"},
        {"name": "Sort_Order", "dataType": "int64", "sourceColumn": "Sort_Order", "isHidden": True},
    ]

    # ========================================================================
    # CALCULATED TABLE: Model_Performance
    # ========================================================================
    model_perf_expr = (
        'DATATABLE(\n'
        '    "Model", STRING,\n'
        '    "Accuracy", DOUBLE,\n'
        '    "Precision_Score", DOUBLE,\n'
        '    "Recall", DOUBLE,\n'
        '    "F1_Score", DOUBLE,\n'
        '    "ROC_AUC", DOUBLE,\n'
        '    {\n'
        '        {"Logistic Regression", 0.8055, 0.6572, 0.5588, 0.6040, 0.8421},\n'
        '        {"Random Forest", 0.7871, 0.6267, 0.4893, 0.5496, 0.8193}\n'
        '    }\n'
        ')'
    )

    model_perf_columns = [
        {"type": "calculatedTableColumn", "name": "Model", "dataType": "string", "sourceColumn": "[Model]", "isNameInferred": True},
        {"type": "calculatedTableColumn", "name": "Accuracy", "dataType": "double", "sourceColumn": "[Accuracy]", "isNameInferred": True, "formatString": "0.00%"},
        {"type": "calculatedTableColumn", "name": "Precision_Score", "dataType": "double", "sourceColumn": "[Precision_Score]", "isNameInferred": True, "formatString": "0.00%"},
        {"type": "calculatedTableColumn", "name": "Recall", "dataType": "double", "sourceColumn": "[Recall]", "isNameInferred": True, "formatString": "0.00%"},
        {"type": "calculatedTableColumn", "name": "F1_Score", "dataType": "double", "sourceColumn": "[F1_Score]", "isNameInferred": True, "formatString": "0.00%"},
        {"type": "calculatedTableColumn", "name": "ROC_AUC", "dataType": "double", "sourceColumn": "[ROC_AUC]", "isNameInferred": True, "formatString": "0.00%"},
    ]

    # ========================================================================
    # CALCULATED TABLE: Confusion_Matrix
    # ========================================================================
    confusion_expr = (
        'DATATABLE(\n'
        '    "Actual", STRING,\n'
        '    "Predicted", STRING,\n'
        '    "Count", INTEGER,\n'
        '    {\n'
        '        {"Churn (Yes)", "Predicted Churn (Yes)", [True Positives]},\n'
        '        {"Churn (Yes)", "Predicted No Churn (No)", [False Negatives]},\n'
        '        {"No Churn (No)", "Predicted Churn (Yes)", [False Positives]},\n'
        '        {"No Churn (No)", "Predicted No Churn (No)", [True Negatives]}\n'
        '    }\n'
        ')'
    )
    # Actually, DATATABLE doesn't support measure references. Let me use a different approach
    # for the confusion matrix - use a static DATATABLE with pre-calculated values

    # From the model predictions:
    # Actual Yes & Predicted Yes (TP) = 1044
    # Actual Yes & Predicted No (FN) = 825
    # Actual No & Predicted Yes (FP) = 518
    # Actual No & Predicted No (TN) = 4656
    # Check: 1044 + 825 + 518 + 4656 = 7043 ✓
    # Wait, I need to verify these numbers. Let me calculate:
    # Total = 7043
    # Actual Yes = 1869, Actual No = 5174
    # Predicted Yes = 1562, Predicted No = 5481
    # Accuracy = 0.8055 -> Correct = 0.8055 * 7043 = 5673.2 ≈ 5673
    # But let me use Prediction_Correct field instead
    # Prediction_Correct = Yes means the prediction matches actual
    # I'll calculate actual values from the data in the verification step

    # ========================================================================
    # ASSEMBLE COMPLETE TMSL
    # ========================================================================
    tmsl = {
        "createOrReplace": {
            "object": {
                "database": DATABASE_ID
            },
            "database": {
                "id": DATABASE_ID,
                "name": DATABASE_ID,
                "compatibilityLevel": COMPAT_LEVEL,
                "model": {
                    "culture": "en-US",
                    "defaultPowerBIDataSourceVersion": "powerBI_V3",
                    "tables": [
                        # Main fact table
                        {
                            "name": "customer_churn_analytics",
                            "columns": main_columns,
                            "measures": measures_json,
                            "partitions": [{
                                "name": "customer_churn_analytics-partition",
                                "mode": "import",
                                "source": {
                                    "type": "m",
                                    "expression": main_m_expr
                                }
                            }],
                        },
                        # Risk sort dimension
                        {
                            "name": "risk_category_sort",
                            "columns": risk_columns,
                            "partitions": [{
                                "name": "risk_category_sort-partition",
                                "mode": "import",
                                "source": {
                                    "type": "m",
                                    "expression": risk_m_expr
                                }
                            }],
                        },
                        # Retention priority dimension
                        {
                            "name": "retention_priority_sort",
                            "columns": ret_columns,
                            "partitions": [{
                                "name": "retention_priority_sort-partition",
                                "mode": "import",
                                "source": {
                                    "type": "m",
                                    "expression": ret_m_expr
                                }
                            }],
                        },
                        # Model Performance (calculated table with verified Phase 3 results)
                        {
                            "name": "Model_Performance",
                            "columns": model_perf_columns,
                            "partitions": [{
                                "name": "Model_Performance-partition",
                                "source": {
                                    "type": "calculated",
                                    "expression": model_perf_expr
                                }
                            }],
                        },
                    ],
                    "relationships": [
                        {
                            "name": "risk_category_relationship",
                            "fromTable": "customer_churn_analytics",
                            "fromColumn": "Churn_Risk_Category",
                            "toTable": "risk_category_sort",
                            "toColumn": "Risk_Category",
                        },
                        {
                            "name": "retention_priority_relationship",
                            "fromTable": "customer_churn_analytics",
                            "fromColumn": "Retention_Priority",
                            "toTable": "retention_priority_sort",
                            "toColumn": "Retention_Priority",
                        },
                    ],
                }
            }
        }
    }

    return tmsl


def main():
    print("=" * 70)
    print("CCPRA POWER BI MODEL BUILDER")
    print("=" * 70)

    # Step 1: Generate TMSL
    print("\n[1/3] Generating TMSL model definition...")
    tmsl = build_tmsl()

    tmsl_path = os.path.join(PROJECT_ROOT, "powerbi_model.tmsl.json")
    with open(tmsl_path, "w", encoding="utf-8") as f:
        json.dump(tmsl, f, indent=2, ensure_ascii=False)
    print(f"  -> Saved to: {tmsl_path}")
    print(f"  -> File size: {os.path.getsize(tmsl_path):,} bytes")

    # Step 2: Generate process command
    print("\n[2/3] Generating refresh command...")
    refresh_tmsl = {
        "refresh": {
            "type": "full",
            "objects": [
                {"database": DATABASE_ID}
            ]
        }
    }
    refresh_path = os.path.join(PROJECT_ROOT, "powerbi_refresh.tmsl.json")
    with open(refresh_path, "w", encoding="utf-8") as f:
        json.dump(refresh_tmsl, f, indent=2)
    print(f"  -> Saved to: {refresh_path}")

    # Step 3: Generate PowerShell executor
    print("\n[3/3] Generating PowerShell executor...")
    ps_script = r'''# ============================================================================
# CCPRA Power BI Model Deployer
# Deploys the TMSL model to the running Power BI Desktop instance
# ============================================================================

param(
    [string]$TmslPath = "PROJECT_ROOT\powerbi_model.tmsl.json",
    [string]$RefreshPath = "PROJECT_ROOT\powerbi_refresh.tmsl.json"
)

$ErrorActionPreference = "Stop"

# Load AdomdClient
$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
Write-Host "Loading AdomdClient from: $adomdPath"
[System.Reflection.Assembly]::LoadFrom($adomdPath) | Out-Null

# Get port
$portFile = "C:\Users\bader\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_e00317cc-e952-4283-83d0-8025c8c299fd\Data\msmdsrv.port.txt"
$port = (Get-Content $portFile -Encoding Unicode).Trim()
Write-Host "AS Instance port: $port"

# Connect
$connStr = "Data Source=localhost:$port;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()
Write-Host "Connected successfully! State: $($conn.State)"

# Step 1: Deploy model
Write-Host "`n[STEP 1] Deploying data model via TMSL createOrReplace..."
$tmslContent = Get-Content -Path $TmslPath -Raw -Encoding UTF8
$cmd = $conn.CreateCommand()
$cmd.CommandText = $tmslContent
try {
    $cmd.ExecuteNonQuery() | Out-Null
    Write-Host "  -> Model deployed successfully!"
} catch {
    Write-Host "  -> ERROR deploying model: $($_.Exception.Message)"
    Write-Host "  -> Inner: $($_.Exception.InnerException.Message)"
    $conn.Close()
    exit 1
}

# Step 2: Process/Refresh model
Write-Host "`n[STEP 2] Processing model (loading data from CSV)..."
$refreshContent = Get-Content -Path $RefreshPath -Raw -Encoding UTF8
$cmd2 = $conn.CreateCommand()
$cmd2.CommandText = $refreshContent
try {
    $cmd2.ExecuteNonQuery() | Out-Null
    Write-Host "  -> Model processed successfully!"
} catch {
    Write-Host "  -> ERROR processing model: $($_.Exception.Message)"
    Write-Host "  -> Inner: $($_.Exception.InnerException.Message)"
    $conn.Close()
    exit 1
}

# Step 3: Verify tables
Write-Host "`n[STEP 3] Verifying deployed model..."

# Query table count
$cmd3 = $conn.CreateCommand()
$cmd3.CommandText = "SELECT [Name] FROM `$SYSTEM.TMSCHEMA_TABLES"
$adapter3 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd3)
$ds3 = New-Object System.Data.DataSet
$adapter3.Fill($ds3) | Out-Null
Write-Host "  Tables:"
foreach ($row in $ds3.Tables[0].Rows) { Write-Host "    - $($row['Name'])" }

# Verify row counts via DAX
$tables = @(
    @{Name="customer_churn_analytics"; Expected=7043},
    @{Name="risk_category_sort"; Expected=3},
    @{Name="retention_priority_sort"; Expected=4},
    @{Name="Model_Performance"; Expected=2}
)

foreach ($tbl in $tables) {
    $cmd4 = $conn.CreateCommand()
    $cmd4.CommandText = "EVALUATE ROW(""Count"", COUNTROWS('$($tbl.Name)'))"
    $adapter4 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd4)
    $ds4 = New-Object System.Data.DataSet
    $adapter4.Fill($ds4) | Out-Null
    $count = $ds4.Tables[0].Rows[0][0]
    $status = if ($count -eq $tbl.Expected) { "OK" } else { "MISMATCH (expected $($tbl.Expected))" }
    Write-Host "    $($tbl.Name): $count rows - $status"
}

# Verify key measures
Write-Host "`n  Verifying measures..."
$measureChecks = @(
    @{DAX='EVALUATE ROW("v", [Total Customers])'; Expected=7043; Name="Total Customers"},
    @{DAX='EVALUATE ROW("v", [Actual Churned Customers])'; Expected=1869; Name="Actual Churned Customers"},
    @{DAX='EVALUATE ROW("v", [Actual Retained Customers])'; Expected=5174; Name="Actual Retained Customers"},
    @{DAX='EVALUATE ROW("v", [Predicted Churn Customers])'; Expected=1562; Name="Predicted Churn Customers"},
    @{DAX='EVALUATE ROW("v", [High Risk Customers])'; Expected=1039; Name="High Risk Customers"},
    @{DAX='EVALUATE ROW("v", [Critical Priority Customers])'; Expected=49; Name="Critical Priority Customers"},
    @{DAX='EVALUATE ROW("v", [High Priority Customers])'; Expected=990; Name="High Priority Customers"},
    @{DAX='EVALUATE ROW("v", [Medium Priority Customers])'; Expected=1633; Name="Medium Priority Customers"},
    @{DAX='EVALUATE ROW("v", [Low Priority Customers])'; Expected=4371; Name="Low Priority Customers"}
)

foreach ($chk in $measureChecks) {
    $cmd5 = $conn.CreateCommand()
    $cmd5.CommandText = $chk.DAX
    $adapter5 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd5)
    $ds5 = New-Object System.Data.DataSet
    $adapter5.Fill($ds5) | Out-Null
    $val = $ds5.Tables[0].Rows[0][0]
    $status = if ([int]$val -eq $chk.Expected) { "OK" } else { "MISMATCH (expected $($chk.Expected), got $val)" }
    Write-Host "    $($chk.Name): $val - $status"
}

# Verify relationships
Write-Host "`n  Verifying relationships..."
$cmd6 = $conn.CreateCommand()
$cmd6.CommandText = "SELECT [Name], [FromTableID], [ToTableID] FROM `$SYSTEM.TMSCHEMA_RELATIONSHIPS"
$adapter6 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd6)
$ds6 = New-Object System.Data.DataSet
$adapter6.Fill($ds6) | Out-Null
foreach ($row in $ds6.Tables[0].Rows) { Write-Host "    - $($row['Name'])" }

# Count measures
$cmd7 = $conn.CreateCommand()
$cmd7.CommandText = "SELECT [Name] FROM `$SYSTEM.TMSCHEMA_MEASURES"
$adapter7 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd7)
$ds7 = New-Object System.Data.DataSet
$adapter7.Fill($ds7) | Out-Null
Write-Host "`n  Total measures: $($ds7.Tables[0].Rows.Count)"
foreach ($row in $ds7.Tables[0].Rows) { Write-Host "    - $($row['Name'])" }

$conn.Close()
Write-Host "`n============================================"
Write-Host "MODEL DEPLOYMENT COMPLETE"
Write-Host "============================================"
'''.replace('PROJECT_ROOT', PROJECT_ROOT.replace('\\', '\\\\'))

    ps_path = os.path.join(PROJECT_ROOT, "deploy_model.ps1")
    with open(ps_path, "w", encoding="utf-8") as f:
        f.write(ps_script)
    print(f"  -> Saved to: {ps_path}")

    print("\n" + "=" * 70)
    print("FILES GENERATED SUCCESSFULLY")
    print("=" * 70)
    print(f"  1. TMSL Model:    {tmsl_path}")
    print(f"  2. Refresh CMD:   {refresh_path}")
    print(f"  3. PS Deployer:   {ps_path}")
    print("\nRun deploy_model.ps1 to deploy the model to Power BI Desktop.")


if __name__ == "__main__":
    main()
