"""
CCPRA Power BI PBIR (Enhanced Report Format) Definition Generator

Generates the modern Power BI PBIR report definition structure:
- Report/definition/pages/pages.json
- Report/definition/pages/<page_id>/page.json
- Report/definition/pages/<page_id>/visuals/<visual_id>/visual.json

Compliant with Microsoft Fabric / Power BI Enhanced Report schemas:
- pagesMetadata: 1.1.0
- page: 2.1.0
- visualContainer: 2.0.0
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent
T = "customer_churn_analytics"

SCHEMA_PAGES = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"


def uid(prefix: str = "v") -> str:
    """Generate a clean unique visual ID."""
    return f"{prefix}_{uuid.uuid4().hex[:18]}"


def make_col_field(table: str, col: str) -> Dict[str, Any]:
    return {
        "Column": {
            "Expression": {"SourceRef": {"Entity": table}},
            "Property": col
        }
    }


def make_measure_field(table: str, measure: str) -> Dict[str, Any]:
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": table}},
            "Property": measure
        }
    }


# ============================================================================
# VISUAL CREATORS (PBIR FORMAT)
# ============================================================================

def make_pbir_textbox(
    x: int, y: int, w: int, h: int,
    text: str,
    font_size: str = "12pt",
    bold: bool = False,
    tab_order: int = 0
) -> Dict[str, Any]:
    paragraphs = []
    for line in text.split("\n"):
        run = {
            "value": line,
            "textStyle": {
                "fontFamily": "Segoe UI",
                "fontSize": font_size
            }
        }
        if bold:
            run["textStyle"]["fontWeight"] = "bold"
        paragraphs.append({
            "textRuns": [run],
            "horizontalTextAlignment": "left"
        })

    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid("tb"),
        "position": {
            "x": x, "y": y, "width": w, "height": h,
            "z": 0, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": paragraphs
                        }
                    }
                ]
            }
        }
    }


def make_pbir_card(
    x: int, y: int, w: int, h: int,
    table: str,
    field_name: str,
    title: str,
    is_measure: bool = True,
    tab_order: int = 0
) -> Dict[str, Any]:
    field_expr = make_measure_field(table, field_name) if is_measure else make_col_field(table, field_name)
    query_ref = f"{table}.{field_name}"

    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid("card"),
        "position": {
            "x": x, "y": y, "width": w, "height": h,
            "z": 0, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Data": {
                        "projections": [
                            {
                                "field": field_expr,
                                "queryRef": query_ref
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            }
        }
    }


def make_pbir_slicer(
    x: int, y: int, w: int, h: int,
    table: str,
    column: str,
    title: str,
    tab_order: int = 0
) -> Dict[str, Any]:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid("slicer"),
        "position": {
            "x": x, "y": y, "width": w, "height": h,
            "z": 0, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": make_col_field(table, column),
                                "queryRef": f"{table}.{column}"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            }
        }
    }


def make_pbir_donut(
    x: int, y: int, w: int, h: int,
    table: str,
    category_col: str,
    value_measure: str,
    title: str,
    tab_order: int = 0
) -> Dict[str, Any]:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid("donut"),
        "position": {
            "x": x, "y": y, "width": w, "height": h,
            "z": 0, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "donutChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": make_col_field(table, category_col),
                                "queryRef": f"{table}.{category_col}"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": make_measure_field(table, value_measure),
                                "queryRef": f"{table}.{value_measure}"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            }
        }
    }


def make_pbir_chart(
    x: int, y: int, w: int, h: int,
    table: str,
    axis_col: str,
    value_measure: str,
    title: str,
    chart_type: str = "clusteredBarChart",
    legend_col: str = None,
    legend_table: str = None,
    tab_order: int = 0
) -> Dict[str, Any]:
    query_state: Dict[str, Any] = {
        "Category": {
            "projections": [
                {
                    "field": make_col_field(table, axis_col),
                    "queryRef": f"{table}.{axis_col}"
                }
            ]
        },
        "Y": {
            "projections": [
                {
                    "field": make_measure_field(table, value_measure),
                    "queryRef": f"{table}.{value_measure}"
                }
            ]
        }
    }

    if legend_col:
        lt = legend_table or table
        query_state["Series"] = {
            "projections": [
                {
                    "field": make_col_field(lt, legend_col),
                    "queryRef": f"{lt}.{legend_col}"
                }
            ]
        }

    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid("chart"),
        "position": {
            "x": x, "y": y, "width": w, "height": h,
            "z": 0, "tabOrder": tab_order
        },
        "visual": {
            "visualType": chart_type,
            "query": {
                "queryState": query_state
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            }
        }
    }


def make_pbir_table(
    x: int, y: int, w: int, h: int,
    table: str,
    columns: List[str],
    title: str,
    column_display_names: List[str] = None,
    tab_order: int = 0
) -> Dict[str, Any]:
    if not column_display_names:
        column_display_names = columns

    projections = []
    for col, display in zip(columns, column_display_names):
        is_measure = (
            " " in col
            or col.startswith("Total")
            or col.startswith("Average")
            or col.startswith("Actual")
            or col.startswith("Predicted")
            or col.startswith("High")
            or col.startswith("Correct")
            or col in ["Accuracy", "Precision_Score", "Recall", "F1_Score", "ROC_AUC"]
        )
        if is_measure:
            field = make_measure_field(table, col)
        else:
            field = make_col_field(table, col)

        proj: Dict[str, Any] = {
            "field": field,
            "queryRef": f"{table}.{col}"
        }
        if display != col:
            proj["displayName"] = display
        projections.append(proj)

    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid("table"),
        "position": {
            "x": x, "y": y, "width": w, "height": h,
            "z": 0, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": projections
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            }
        }
    }


# ============================================================================
# PAGE DEFINITIONS (6 PAGES, 75 VISUALS)
# ============================================================================

def build_page_1() -> Dict[str, Any]:
    """Page 1 — Executive Overview (17 visuals)"""
    visuals = []
    tab = 0

    # 1. Header Banner
    visuals.append(make_pbir_textbox(20, 10, 1240, 50, "Customer Churn Prediction & Retention Analytics", font_size="16pt", bold=True, tab_order=tab))
    tab += 1

    # 2-7. KPI Cards (6 cards)
    cards = [
        (T, "Total Customers", "Total Customers"),
        (T, "Actual Churned Customers", "Actual Churned"),
        (T, "Actual Churn Rate", "Actual Churn Rate"),
        (T, "Predicted Churn Customers", "Predicted Churn"),
        (T, "High Risk Customers", "High Risk"),
        (T, "Average Churn Probability", "Avg Churn Prob"),
    ]
    card_w, card_h, card_y = 190, 100, 70
    for i, (tbl, measure, title) in enumerate(cards):
        x = 20 + i * (card_w + 10)
        visuals.append(make_pbir_card(x, card_y, card_w, card_h, tbl, measure, title, is_measure=True, tab_order=tab))
        tab += 1

    # 8-10. Row 2 Distribution Charts
    row2_y = 185
    visuals.append(make_pbir_donut(20, row2_y, 300, 250, T, "Churn", "Total Customers", "Actual Churn vs Retained", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(330, row2_y, 300, 250, T, "Churn_Risk_Category", "Total Customers", "Churn Risk Distribution", "clusteredBarChart", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(640, row2_y, 300, 250, T, "Retention_Priority", "Total Customers", "Retention Priority Distribution", "clusteredBarChart", tab_order=tab))
    tab += 1

    # 11-12. Row 3 Segmented Charts
    row3_y = 445
    visuals.append(make_pbir_chart(20, row3_y, 400, 250, T, "Contract", "Total Customers", "Churn by Contract", "clusteredColumnChart", "Churn", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(430, row3_y, 400, 250, T, "InternetService", "Total Customers", "Churn by Internet Service", "clusteredColumnChart", "Churn", tab_order=tab))
    tab += 1

    # 13-17. Slicers (5 slicers on the right)
    slicers = [
        ("Contract", "Contract"),
        ("InternetService", "Internet Service"),
        ("Churn_Risk_Category", "Risk Category"),
        ("Retention_Priority", "Retention Priority"),
        ("PaymentMethod", "Payment Method"),
    ]
    sx, sw, sh = 960, 290, 50
    for i, (col, title) in enumerate(slicers):
        visuals.append(make_pbir_slicer(sx, row2_y + i * (sh + 5), sw, sh, T, col, title, tab_order=tab))
        tab += 1

    return {
        "page_id": "page_01_executive_overview",
        "display_name": "Executive Overview",
        "visuals": visuals
    }


def build_page_2() -> Dict[str, Any]:
    """Page 2 — Churn Risk Analysis (12 visuals)"""
    visuals = []
    tab = 0

    # 1. Header Banner
    visuals.append(make_pbir_textbox(20, 10, 1240, 40, "Churn Risk Analysis", font_size="14pt", bold=True, tab_order=tab))
    tab += 1

    # 2-5. KPI Cards (4 cards)
    kpis = [
        ("Average Churn Probability", "Avg Churn Probability"),
        ("High Risk Customers", "High Risk Customers"),
        ("Critical Priority Customers", "Critical Customers"),
        ("High Risk Rate", "High Risk Rate"),
    ]
    for i, (m, t) in enumerate(kpis):
        visuals.append(make_pbir_card(20 + i * 210, 60, 200, 90, T, m, t, is_measure=True, tab_order=tab))
        tab += 1

    # 6-8. Row 1 Charts
    r1_y = 165
    visuals.append(make_pbir_donut(20, r1_y, 300, 240, T, "Churn_Risk_Category", "Total Customers", "Risk Category Distribution", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(330, r1_y, 310, 240, T, "Contract", "Total Customers", "Risk Category by Contract", "stackedBarChart", "Churn_Risk_Category", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(650, r1_y, 310, 240, T, "InternetService", "Total Customers", "Risk Category by Internet Service", "stackedBarChart", "Churn_Risk_Category", tab_order=tab))
    tab += 1

    # 9-11. Row 2 Charts
    r2_y = 420
    visuals.append(make_pbir_chart(20, r2_y, 300, 240, T, "PaymentMethod", "Total Customers", "Risk Category by Payment Method", "stackedBarChart", "Churn_Risk_Category", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(330, r2_y, 310, 240, T, "Contract", "Average Churn Probability", "Avg Churn Probability by Contract", "clusteredBarChart", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(650, r2_y, 310, 240, T, "Tenure_Group", "Average Churn Probability", "Avg Churn Probability by Tenure", "clusteredBarChart", tab_order=tab))
    tab += 1

    # 12. Risk Legend Textbox
    visuals.append(make_pbir_textbox(
        970, r1_y, 290, 120,
        "Risk Legend:\n🟢 Low Risk: Prob < 30%\n🟡 Medium Risk: 30% ≤ Prob < 60%\n🔴 High Risk: Prob ≥ 60%",
        font_size="11pt",
        tab_order=tab
    ))
    tab += 1

    return {
        "page_id": "page_02_churn_risk",
        "display_name": "Churn Risk Analysis",
        "visuals": visuals
    }


def build_page_3() -> Dict[str, Any]:
    """Page 3 — Retention Priority & Action (12 visuals)"""
    visuals = []
    tab = 0

    # 1. Header Banner
    visuals.append(make_pbir_textbox(20, 10, 1240, 40, "Retention Priority & Action", font_size="14pt", bold=True, tab_order=tab))
    tab += 1

    # 2-5. Priority KPI cards (4 cards)
    pri_cards = [
        ("Critical Priority Customers", "Priority 1 - Critical"),
        ("High Priority Customers", "Priority 2 - High"),
        ("Medium Priority Customers", "Priority 3 - Medium"),
        ("Low Priority Customers", "Priority 4 - Low"),
    ]
    for i, (m, t) in enumerate(pri_cards):
        visuals.append(make_pbir_card(20 + i * 210, 60, 200, 90, T, m, t, is_measure=True, tab_order=tab))
        tab += 1

    # 6. Main Customer Retention Action Table
    table_cols = [
        "customerID", "Churn", "Predicted_Churn_Probability", "Churn_Risk_Percentage",
        "Churn_Risk_Category", "Retention_Priority", "Retention_Action",
        "MonthlyCharges", "tenure", "Contract", "InternetService", "PaymentMethod"
    ]
    visuals.append(make_pbir_table(20, 160, 840, 540, T, table_cols, "Customer Retention Actions", tab_order=tab))
    tab += 1

    # 7-12. Slicers (6 slicers on the right)
    slicers = [
        ("Retention_Priority", "Retention Priority"),
        ("Churn_Risk_Category", "Risk Category"),
        ("Contract", "Contract"),
        ("InternetService", "Internet Service"),
        ("PaymentMethod", "Payment Method"),
        ("High_Risk_Flag", "High Risk Flag"),
    ]
    for i, (col, title) in enumerate(slicers):
        visuals.append(make_pbir_slicer(875, 160 + i * 55, 385, 50, T, col, title, tab_order=tab))
        tab += 1

    return {
        "page_id": "page_03_retention_action",
        "display_name": "Retention Priority & Action",
        "visuals": visuals
    }


def build_page_4() -> Dict[str, Any]:
    """Page 4 — Customer Risk Explorer (16 visuals)"""
    visuals = []
    tab = 0

    # 1. Header Banner
    visuals.append(make_pbir_textbox(20, 10, 1240, 40, "Customer Risk Explorer", font_size="14pt", bold=True, tab_order=tab))
    tab += 1

    # 2. Customer ID Search Slicer
    visuals.append(make_pbir_slicer(20, 60, 300, 55, T, "customerID", "Search Customer ID", tab_order=tab))
    tab += 1

    # 3-15. Customer Attribute Cards (13 cards in 4 columns)
    detail_fields = [
        ("customerID", "Customer ID"),
        ("Predicted_Churn_Probability", "Churn Probability"),
        ("Churn_Risk_Percentage", "Churn Risk %"),
        ("Churn_Risk_Category", "Risk Category"),
        ("Retention_Priority", "Retention Priority"),
        ("Predicted_Churn", "Predicted Churn"),
        ("Churn", "Actual Churn"),
        ("MonthlyCharges", "Monthly Charges"),
        ("TotalCharges", "Total Charges"),
        ("tenure", "Tenure (Months)"),
        ("Contract", "Contract"),
        ("InternetService", "Internet Service"),
        ("PaymentMethod", "Payment Method"),
    ]
    card_w, card_h, start_y = 190, 80, 130
    cols_per_row = 4
    for i, (fld, disp) in enumerate(detail_fields):
        row = i // cols_per_row
        col = i % cols_per_row
        x = 20 + col * (card_w + 10)
        y = start_y + row * (card_h + 10)
        visuals.append(make_pbir_card(x, y, card_w, card_h, T, fld, disp, is_measure=False, tab_order=tab))
        tab += 1

    # 16. Retention Action Card (Full Width)
    visuals.append(make_pbir_card(20, start_y + 4 * (card_h + 10), 800, 90, T, "Retention_Action", "Retention Action", is_measure=False, tab_order=tab))
    tab += 1

    return {
        "page_id": "page_04_risk_explorer",
        "display_name": "Customer Risk Explorer",
        "visuals": visuals
    }


def build_page_5() -> Dict[str, Any]:
    """Page 5 — Model Performance (13 visuals)"""
    visuals = []
    tab = 0

    # 1. Header Banner
    visuals.append(make_pbir_textbox(20, 10, 1240, 40, "Model Performance", font_size="14pt", bold=True, tab_order=tab))
    tab += 1

    # 2. Model Selection Rationale
    visuals.append(make_pbir_textbox(
        20, 60, 600, 60,
        "Selected Model: Logistic Regression\nSelection Reason: Higher ROC-AUC, Recall, Precision, and F1-Score than Random Forest",
        font_size="11pt",
        tab_order=tab
    ))
    tab += 1

    # 3-7. Static KPI Metric Textboxes (5 metrics)
    metrics = [
        ("Accuracy", "80.55%"),
        ("Precision", "65.72%"),
        ("Recall", "55.88%"),
        ("F1 Score", "60.40%"),
        ("ROC-AUC", "84.21%"),
    ]
    for i, (label, val) in enumerate(metrics):
        visuals.append(make_pbir_textbox(20 + i * 245, 130, 230, 75, f"{label}\n{val}", font_size="13pt", bold=True, tab_order=tab))
        tab += 1

    # 8. Model Comparison Table
    model_cols = ["Model", "Accuracy", "Precision_Score", "Recall", "F1_Score", "ROC_AUC"]
    model_displays = ["Model", "Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
    visuals.append(make_pbir_table(20, 220, 600, 150, "Model_Performance", model_cols, "Model Comparison", model_displays, tab_order=tab))
    tab += 1

    # 9. Model Comparison Bar Chart
    visuals.append(make_pbir_chart(640, 220, 620, 150, "Model_Performance", "Model", "Accuracy", "Model Comparison — Accuracy", "clusteredColumnChart", tab_order=tab))
    tab += 1

    # 10-11. Actual vs Predicted Charts
    visuals.append(make_pbir_chart(20, 385, 400, 250, T, "Churn", "Total Customers", "Actual Churn Distribution", "clusteredColumnChart", tab_order=tab))
    tab += 1
    visuals.append(make_pbir_chart(430, 385, 400, 250, T, "Predicted_Churn", "Total Customers", "Predicted Churn Distribution", "clusteredColumnChart", tab_order=tab))
    tab += 1

    # 12. Prediction Accuracy Donut
    visuals.append(make_pbir_donut(850, 385, 390, 250, T, "Prediction_Correct", "Total Customers", "Prediction Accuracy", tab_order=tab))
    tab += 1

    # 13. Confusion Matrix Explanation
    visuals.append(make_pbir_textbox(
        20, 650, 1240, 50,
        "Confusion Matrix: TP (Actual=Yes, Predicted=Yes), TN (Actual=No, Predicted=No), FP (Actual=No, Predicted=Yes), FN (Actual=Yes, Predicted=No)",
        font_size="11pt",
        tab_order=tab
    ))
    tab += 1

    return {
        "page_id": "page_05_model_performance",
        "display_name": "Model Performance",
        "visuals": visuals
    }


def build_page_6() -> Dict[str, Any]:
    """Page 6 — High-Risk Customers (5 visuals)"""
    visuals = []
    tab = 0

    # 1. Header Banner
    visuals.append(make_pbir_textbox(20, 10, 1240, 40, "High-Risk Customer Table", font_size="14pt", bold=True, tab_order=tab))
    tab += 1

    # 2-4. KPI Cards
    visuals.append(make_pbir_card(20, 60, 200, 90, T, "High Risk Customers", "High Risk Customers", is_measure=True, tab_order=tab))
    tab += 1
    visuals.append(make_pbir_card(230, 60, 200, 90, T, "Critical Priority Customers", "Critical Priority", is_measure=True, tab_order=tab))
    tab += 1
    visuals.append(make_pbir_card(440, 60, 200, 90, T, "At-Risk Revenue", "At-Risk Revenue", is_measure=True, tab_order=tab))
    tab += 1

    # 5. High-Risk Customer Table
    hr_cols = [
        "customerID", "Churn", "Predicted_Churn", "Predicted_Churn_Probability",
        "Churn_Risk_Percentage", "Churn_Risk_Category", "Retention_Priority",
        "Contract", "MonthlyCharges", "tenure", "Retention_Action"
    ]
    visuals.append(make_pbir_table(20, 165, 1240, 530, T, hr_cols, "High-Risk Customers (Probability ≥ 60%)", tab_order=tab))
    tab += 1

    return {
        "page_id": "page_06_high_risk",
        "display_name": "High-Risk Customers",
        "visuals": visuals
    }


# ============================================================================
# MAIN EXPORT FUNCTION
# ============================================================================

def generate_all_pbir_files() -> Dict[str, bytes]:
    """
    Generate all files under Report/definition/pages/ for the 6 pages and 75 visuals.
    Returns dictionary of {zip_path: file_bytes}.
    """
    pages_data = [
        build_page_1(),
        build_page_2(),
        build_page_3(),
        build_page_4(),
        build_page_5(),
        build_page_6(),
    ]

    files: Dict[str, bytes] = {}

    # 1. Report/definition/pages/pages.json
    page_order = [p["page_id"] for p in pages_data]
    pages_meta = {
        "$schema": SCHEMA_PAGES,
        "pageOrder": page_order,
        "activePageName": page_order[0]
    }
    files["Report/definition/pages/pages.json"] = json.dumps(pages_meta, indent=2, ensure_ascii=False).encode("utf-8")

    # 2. Each page and its visuals
    for p in pages_data:
        pid = p["page_id"]
        page_def = {
            "$schema": SCHEMA_PAGE,
            "name": pid,
            "displayName": p["display_name"],
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280
        }
        files[f"Report/definition/pages/{pid}/page.json"] = json.dumps(page_def, indent=2, ensure_ascii=False).encode("utf-8")

        for v in p["visuals"]:
            vid = v["name"]
            files[f"Report/definition/pages/{pid}/visuals/{vid}/visual.json"] = json.dumps(v, indent=2, ensure_ascii=False).encode("utf-8")

    return files


if __name__ == "__main__":
    files = generate_all_pbir_files()
    print("Generated PBIR Files:")
    print(f"  Total files: {len(files)}")
    pages = [k for k in files if k.endswith("page.json") and not k.endswith("pages.json")]
    visuals = [k for k in files if k.endswith("visual.json")]
    print(f"  Pages: {len(pages)}")
    print(f"  Visuals: {len(visuals)}")
