"""
CCPRA Power BI Report Layout Generator

Generates the complete Report/Layout JSON structure with all 6 professional dashboard pages.
This can be injected into a PBIX file after initial save from Power BI Desktop.

After the user saves the PBIX with Ctrl+Shift+S, run inject_report_layout.py to add all visuals.
"""

import json
import uuid
import os

PROJECT_ROOT = r"C:\Users\bader\Desktop\CCPRA Project"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def uid():
    """Generate a unique visual container ID."""
    return uuid.uuid4().hex[:20]

def measure_ref(table, measure):
    """Create a measure reference expression."""
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": table}},
            "Property": measure
        }
    }

def column_ref(table, column):
    """Create a column reference expression."""
    return {
        "Column": {
            "Expression": {"SourceRef": {"Entity": table}},
            "Property": column
        }
    }

def make_card(x, y, w, h, table, measure_name, title, bg_color="#FFFFFF", value_color="#2C3E50"):
    """Create a KPI card visual container."""
    visual_id = uid()
    config = {
        "name": visual_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {"Data": [{"queryRef": f"{table}.{measure_name}"}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": table, "Type": 0}],
                "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": measure_name}, "Name": f"{table}.{measure_name}"}]
            },
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True,
            "objects": {
                "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "16D"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{value_color}'"}}}}}}}],
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fontSize": {"expr": {"Literal": {"Value": "10D"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#7F8C8D'"}}}}}}}],
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},"fontSize": {"expr": {"Literal": {"Value": "11D"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2C3E50'"}}}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{bg_color}'"}}}}},"transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}}}}],
                "padding": [{"properties": {"top": {"expr": {"Literal": {"Value": "8D"}}}, "bottom": {"expr": {"Literal": {"Value": "8D"}}}, "left": {"expr": {"Literal": {"Value": "12D"}}}, "right": {"expr": {"Literal": {"Value": "12D"}}}}}],
            }
        }
    }

    dt = {
        "objects": {
            "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "16D"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{value_color}'"}}}}}}}],
            "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fontSize": {"expr": {"Literal": {"Value": "10D"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#7F8C8D'"}}}}}}}],
        },
        "projectionOrdering": {"Data": [0]},
        "queryMetadata": {"Select": [{"Restatement": measure_name, "Name": f"{table}.{measure_name}", "Type": 3}]},
        "visualElements": [{"DataRoles": [{"Name": "Data", "Projection": 0, "isActive": False}]}],
        "selects": [{"displayName": measure_name, "queryName": f"{table}.{measure_name}", "roles": {"Data": True}, "type": {"category": None, "underlyingType": 260}, "expr": measure_ref(table, measure_name)}]
    }

    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
        "dataTransforms": json.dumps(dt)
    }

def make_slicer(x, y, w, h, table, column, title):
    """Create a slicer visual container."""
    visual_id = uid()
    config = {
        "name": visual_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {"Values": [{"queryRef": f"{table}.{column}"}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": table, "Type": 0}],
                "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": column}, "Name": f"{table}.{column}"}]
            },
            "objects": {
                "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
                "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2C3E50'"}}}}}}}],
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},"fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},"transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            }
        }
    }
    dt = {
        "projectionOrdering": {"Values": [0]},
        "queryMetadata": {"Select": [{"Restatement": column, "Name": f"{table}.{column}", "Type": 6}]},
        "visualElements": [{"DataRoles": [{"Name": "Values", "Projection": 0, "isActive": False}]}],
        "selects": [{"displayName": column, "queryName": f"{table}.{column}", "roles": {"Values": True}, "type": {"category": None, "underlyingType": 1}, "expr": column_ref(table, column)}]
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config), "filters": "[]", "dataTransforms": json.dumps(dt)}

def make_donut(x, y, w, h, table, category_col, value_measure, title):
    """Create a donut chart visual container."""
    visual_id = uid()
    config = {
        "name": visual_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {"Category": [{"queryRef": f"{table}.{category_col}"}], "Y": [{"queryRef": f"{table}.{value_measure}"}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": table, "Type": 0}],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": category_col}, "Name": f"{table}.{category_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": value_measure}, "Name": f"{table}.{value_measure}"}
                ]
            },
            "drillFilterOtherVisuals": True,
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},"fontSize": {"expr": {"Literal": {"Value": "12D"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2C3E50'"}}}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}}}}],
            }
        }
    }
    dt = {
        "projectionOrdering": {"Category": [0], "Y": [1]},
        "queryMetadata": {"Select": [
            {"Restatement": category_col, "Name": f"{table}.{category_col}", "Type": 6},
            {"Restatement": value_measure, "Name": f"{table}.{value_measure}", "Type": 3}
        ]},
        "visualElements": [{"DataRoles": [{"Name": "Category", "Projection": 0}, {"Name": "Y", "Projection": 1}]}],
        "selects": [
            {"displayName": category_col, "queryName": f"{table}.{category_col}", "roles": {"Category": True}, "type": {"category": None, "underlyingType": 1}, "expr": column_ref(table, category_col)},
            {"displayName": value_measure, "queryName": f"{table}.{value_measure}", "roles": {"Y": True}, "type": {"category": None, "underlyingType": 260}, "expr": measure_ref(table, value_measure)}
        ]
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config), "filters": "[]", "dataTransforms": json.dumps(dt)}

def make_bar_chart(x, y, w, h, table, axis_col, value_measure, title, chart_type="clusteredBarChart", legend_col=None, legend_table=None):
    """Create a bar/column chart visual container."""
    visual_id = uid()
    projections = {"Category": [{"queryRef": f"{table}.{axis_col}"}], "Y": [{"queryRef": f"{table}.{value_measure}"}]}
    selects = [
        {"displayName": axis_col, "queryName": f"{table}.{axis_col}", "roles": {"Category": True}, "type": {"category": None, "underlyingType": 1}, "expr": column_ref(table, axis_col)},
        {"displayName": value_measure, "queryName": f"{table}.{value_measure}", "roles": {"Y": True}, "type": {"category": None, "underlyingType": 260}, "expr": measure_ref(table, value_measure)}
    ]
    from_items = [{"Name": "c", "Entity": table, "Type": 0}]
    select_items = [
        {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": axis_col}, "Name": f"{table}.{axis_col}"},
        {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": value_measure}, "Name": f"{table}.{value_measure}"}
    ]
    qm_selects = [
        {"Restatement": axis_col, "Name": f"{table}.{axis_col}", "Type": 6},
        {"Restatement": value_measure, "Name": f"{table}.{value_measure}", "Type": 3}
    ]
    data_roles = [{"Name": "Category", "Projection": 0}, {"Name": "Y", "Projection": 1}]

    if legend_col:
        lt = legend_table or table
        projections["Series"] = [{"queryRef": f"{lt}.{legend_col}"}]
        selects.append({"displayName": legend_col, "queryName": f"{lt}.{legend_col}", "roles": {"Series": True}, "type": {"category": None, "underlyingType": 1}, "expr": column_ref(lt, legend_col)})
        if lt != table:
            from_items.append({"Name": "l", "Entity": lt, "Type": 0})
            select_items.append({"Column": {"Expression": {"SourceRef": {"Source": "l"}}, "Property": legend_col}, "Name": f"{lt}.{legend_col}"})
        else:
            select_items.append({"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": legend_col}, "Name": f"{lt}.{legend_col}"})
        qm_selects.append({"Restatement": legend_col, "Name": f"{lt}.{legend_col}", "Type": 6})
        data_roles.append({"Name": "Series", "Projection": 2})

    config = {
        "name": visual_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": chart_type,
            "projections": projections,
            "prototypeQuery": {"Version": 2, "From": from_items, "Select": select_items},
            "drillFilterOtherVisuals": True,
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},"fontSize": {"expr": {"Literal": {"Value": "12D"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2C3E50'"}}}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}}}}],
            }
        }
    }
    dt = {
        "projectionOrdering": projections,
        "queryMetadata": {"Select": qm_selects},
        "visualElements": [{"DataRoles": data_roles}],
        "selects": selects
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config), "filters": "[]", "dataTransforms": json.dumps(dt)}

def make_table(x, y, w, h, table, columns, title, column_display_names=None):
    """Create a table visual container."""
    visual_id = uid()
    if not column_display_names:
        column_display_names = columns

    projections = {"Values": [{"queryRef": f"{table}.{c}"} for c in columns]}
    from_item = [{"Name": "c", "Entity": table, "Type": 0}]
    select_items = []
    qm_selects = []
    selects = []

    for i, (col, display) in enumerate(zip(columns, column_display_names)):
        # Determine if measure or column
        is_measure = " " in col or col.startswith("Total") or col.startswith("Average") or col.startswith("Actual") or col.startswith("Predicted") or col.startswith("High") or col.startswith("Correct")
        if is_measure:
            select_items.append({"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": col}, "Name": f"{table}.{col}"})
            qm_selects.append({"Restatement": display, "Name": f"{table}.{col}", "Type": 3})
            selects.append({"displayName": display, "queryName": f"{table}.{col}", "roles": {"Values": True}, "type": {"category": None, "underlyingType": 260}, "expr": measure_ref(table, col)})
        else:
            select_items.append({"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": col}, "Name": f"{table}.{col}"})
            qm_selects.append({"Restatement": display, "Name": f"{table}.{col}", "Type": 6})
            selects.append({"displayName": display, "queryName": f"{table}.{col}", "roles": {"Values": True}, "type": {"category": None, "underlyingType": 1}, "expr": column_ref(table, col)})

    config = {
        "name": visual_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": projections,
            "prototypeQuery": {"Version": 2, "From": from_item, "Select": select_items},
            "drillFilterOtherVisuals": True,
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},"fontSize": {"expr": {"Literal": {"Value": "12D"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2C3E50'"}}}}}}}],
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}}}],
            }
        }
    }
    dt = {
        "projectionOrdering": {"Values": list(range(len(columns)))},
        "queryMetadata": {"Select": qm_selects},
        "visualElements": [{"DataRoles": [{"Name": "Values", "Projection": i} for i in range(len(columns))]}],
        "selects": selects
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config), "filters": "[]", "dataTransforms": json.dumps(dt)}

def make_text_box(x, y, w, h, text_content):
    """Create a text box visual container."""
    visual_id = uid()
    # Escape for PBI text paragraphs
    paragraphs = []
    for line in text_content.split("\n"):
        paragraphs.append({
            "textRuns": [{"value": line, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "12px"}}],
            "horizontalTextAlignment": "left"
        })

    config = {
        "name": visual_id,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{"properties": {"paragraphs": {"expr": {"Literal": {"Value": json.dumps(paragraphs)}}}}}]
            },
            "vcObjects": {
                "background": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},"transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}}}}],
            }
        }
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config), "filters": "[]"}

T = "customer_churn_analytics"  # Main table alias

# ============================================================================
# PAGE 1 — EXECUTIVE CHURN OVERVIEW
# ============================================================================
def build_page1():
    vcs = []
    # Title text box
    vcs.append(make_text_box(20, 10, 1240, 50,
        "Customer Churn Prediction & Retention Analytics"))

    # KPI Cards Row (6 cards)
    card_w = 190
    card_h = 100
    card_y = 70
    cards = [
        (T, "Total Customers", "Total Customers"),
        (T, "Actual Churned Customers", "Actual Churned"),
        (T, "Actual Churn Rate", "Actual Churn Rate"),
        (T, "Predicted Churn Customers", "Predicted Churn"),
        (T, "High Risk Customers", "High Risk"),
        (T, "Average Churn Probability", "Avg Churn Prob"),
    ]
    for i, (tbl, measure, title) in enumerate(cards):
        x = 20 + i * (card_w + 10)
        vcs.append(make_card(x, card_y, card_w, card_h, tbl, measure, title))

    # Row 2: Donut + Bar charts
    row2_y = 185
    vcs.append(make_donut(20, row2_y, 300, 250, T, "Churn", "Total Customers", "Actual Churn vs Retained"))
    vcs.append(make_bar_chart(330, row2_y, 300, 250, T, "Churn_Risk_Category", "Total Customers", "Churn Risk Distribution"))
    vcs.append(make_bar_chart(640, row2_y, 300, 250, T, "Retention_Priority", "Total Customers", "Retention Priority Distribution"))

    # Row 3: More charts
    row3_y = 445
    vcs.append(make_bar_chart(20, row3_y, 400, 250, T, "Contract", "Total Customers", "Churn by Contract", "clusteredColumnChart", "Churn"))
    vcs.append(make_bar_chart(430, row3_y, 400, 250, T, "InternetService", "Total Customers", "Churn by Internet Service", "clusteredColumnChart", "Churn"))

    # Slicers (right column)
    sx = 960
    slicer_w = 290
    slicer_h = 55
    slicers = [
        (T, "Contract", "Contract"),
        (T, "InternetService", "Internet Service"),
        (T, "Churn_Risk_Category", "Risk Category"),
        (T, "Retention_Priority", "Retention Priority"),
        (T, "PaymentMethod", "Payment Method"),
    ]
    for i, (tbl, col, title) in enumerate(slicers):
        vcs.append(make_slicer(sx, row2_y + i * (slicer_h + 5), slicer_w, slicer_h, tbl, col, title))

    return {
        "id": 0, "name": uid(), "displayName": "Executive Overview",
        "filters": "[]", "ordinal": 0, "visualContainers": vcs,
        "config": "{}", "displayOption": 1, "width": 1280, "height": 720
    }

# ============================================================================
# PAGE 2 — CHURN RISK ANALYSIS
# ============================================================================
def build_page2():
    vcs = []
    vcs.append(make_text_box(20, 10, 1240, 40, "Churn Risk Analysis"))

    # KPI Cards
    kpi_y = 60
    vcs.append(make_card(20, kpi_y, 200, 90, T, "Average Churn Probability", "Avg Churn Probability"))
    vcs.append(make_card(230, kpi_y, 200, 90, T, "High Risk Customers", "High Risk Customers", "#FFF5F5", "#E74C3C"))
    vcs.append(make_card(440, kpi_y, 200, 90, T, "Critical Priority Customers", "Critical Customers", "#FFF0F0", "#C0392B"))
    vcs.append(make_card(650, kpi_y, 200, 90, T, "High Risk Rate", "High Risk Rate"))

    # Charts
    row1_y = 165
    vcs.append(make_donut(20, row1_y, 300, 240, T, "Churn_Risk_Category", "Total Customers", "Risk Category Distribution"))
    vcs.append(make_bar_chart(330, row1_y, 310, 240, T, "Contract", "Total Customers", "Risk Category by Contract", "stackedBarChart", "Churn_Risk_Category"))
    vcs.append(make_bar_chart(650, row1_y, 310, 240, T, "InternetService", "Total Customers", "Risk Category by Internet Service", "stackedBarChart", "Churn_Risk_Category"))

    row2_y = 420
    vcs.append(make_bar_chart(20, row2_y, 300, 240, T, "PaymentMethod", "Total Customers", "Risk Category by Payment Method", "stackedBarChart", "Churn_Risk_Category"))
    vcs.append(make_bar_chart(330, row2_y, 310, 240, T, "Contract", "Average Churn Probability", "Avg Churn Probability by Contract"))
    vcs.append(make_bar_chart(650, row2_y, 310, 240, T, "Tenure_Group", "Average Churn Probability", "Avg Churn Probability by Tenure"))

    # Risk legend
    vcs.append(make_text_box(970, row1_y, 290, 120,
        "Risk Legend:\n🟢 Low Risk: Prob < 30%\n🟡 Medium Risk: 30% ≤ Prob < 60%\n🔴 High Risk: Prob ≥ 60%"))

    return {
        "id": 1, "name": uid(), "displayName": "Churn Risk Analysis",
        "filters": "[]", "ordinal": 1, "visualContainers": vcs,
        "config": "{}", "displayOption": 1, "width": 1280, "height": 720
    }

# ============================================================================
# PAGE 3 — RETENTION PRIORITY & ACTION
# ============================================================================
def build_page3():
    vcs = []
    vcs.append(make_text_box(20, 10, 1240, 40, "Retention Priority & Action"))

    # Priority KPI cards
    kpi_y = 60
    vcs.append(make_card(20, kpi_y, 200, 90, T, "Critical Priority Customers", "Priority 1 - Critical", "#FFF0F0", "#C0392B"))
    vcs.append(make_card(230, kpi_y, 200, 90, T, "High Priority Customers", "Priority 2 - High", "#FFF5F5", "#E74C3C"))
    vcs.append(make_card(440, kpi_y, 200, 90, T, "Medium Priority Customers", "Priority 3 - Medium", "#FFFBF0", "#F39C12"))
    vcs.append(make_card(650, kpi_y, 200, 90, T, "Low Priority Customers", "Priority 4 - Low", "#F0FFF0", "#2ECC71"))

    # Main retention action table
    table_cols = ["customerID", "Churn", "Predicted_Churn_Probability", "Churn_Risk_Percentage",
                  "Churn_Risk_Category", "Retention_Priority", "Retention_Action",
                  "MonthlyCharges", "tenure", "Contract", "InternetService", "PaymentMethod"]
    vcs.append(make_table(20, 160, 840, 540, T, table_cols, "Customer Retention Actions"))

    # Slicers
    sx = 875
    slicer_w = 385
    slicer_h = 55
    slicers = [
        (T, "Retention_Priority", "Retention Priority"),
        (T, "Churn_Risk_Category", "Risk Category"),
        (T, "Contract", "Contract"),
        (T, "InternetService", "Internet Service"),
        (T, "PaymentMethod", "Payment Method"),
        (T, "High_Risk_Flag", "High Risk Flag"),
    ]
    for i, (tbl, col, title) in enumerate(slicers):
        vcs.append(make_slicer(sx, 160 + i * (slicer_h + 5), slicer_w, slicer_h, tbl, col, title))

    return {
        "id": 2, "name": uid(), "displayName": "Retention Priority & Action",
        "filters": "[]", "ordinal": 2, "visualContainers": vcs,
        "config": "{}", "displayOption": 1, "width": 1280, "height": 720
    }

# ============================================================================
# PAGE 4 — CUSTOMER RISK EXPLORER
# ============================================================================
def build_page4():
    vcs = []
    vcs.append(make_text_box(20, 10, 1240, 40, "Customer Risk Explorer"))

    # Customer ID search slicer
    vcs.append(make_slicer(20, 60, 300, 55, T, "customerID", "Search Customer ID"))

    # Customer detail cards (2 columns)
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

    card_w = 190
    card_h = 80
    start_y = 130
    cols_per_row = 4
    for i, (field, display) in enumerate(detail_fields):
        row = i // cols_per_row
        col = i % cols_per_row
        x = 20 + col * (card_w + 10)
        y = start_y + row * (card_h + 10)
        vcs.append(make_card(x, y, card_w, card_h, T, field, display))

    # Retention Action (full width)
    vcs.append(make_card(20, start_y + 4 * (card_h + 10), 800, 90, T, "Retention_Action", "Retention Action"))

    return {
        "id": 3, "name": uid(), "displayName": "Customer Risk Explorer",
        "filters": "[]", "ordinal": 3, "visualContainers": vcs,
        "config": "{}", "displayOption": 1, "width": 1280, "height": 720
    }

# ============================================================================
# PAGE 5 — MODEL PERFORMANCE
# ============================================================================
def build_page5():
    vcs = []
    vcs.append(make_text_box(20, 10, 1240, 40, "Model Performance"))

    # Model info text box
    vcs.append(make_text_box(20, 60, 600, 60,
        "Selected Model: Logistic Regression\nSelection Reason: Higher ROC-AUC, Recall, Precision, and F1-Score than Random Forest"))

    # KPI Cards for Logistic Regression metrics
    kpi_y = 130
    metrics = [
        ("Accuracy", "80.55%"),
        ("Precision", "65.72%"),
        ("Recall", "55.88%"),
        ("F1 Score", "60.40%"),
        ("ROC-AUC", "84.21%"),
    ]
    # Use text boxes for static metrics
    for i, (label, value) in enumerate(metrics):
        x = 20 + i * 240
        vcs.append(make_text_box(x, kpi_y, 220, 75, f"{label}\n{value}"))

    # Model comparison table
    model_cols = ["Model", "Accuracy", "Precision_Score", "Recall", "F1_Score", "ROC_AUC"]
    model_displays = ["Model", "Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
    vcs.append(make_table(20, 220, 600, 150, "Model_Performance", model_cols, "Model Comparison", model_displays))

    # Model comparison bar chart
    vcs.append(make_bar_chart(640, 220, 620, 150, "Model_Performance", "Model", "Accuracy", "Model Comparison — Accuracy", "clusteredColumnChart"))

    # Actual vs Predicted comparison
    vcs.append(make_bar_chart(20, 385, 400, 250, T, "Churn", "Total Customers", "Actual Churn Distribution", "clusteredColumnChart"))
    vcs.append(make_bar_chart(430, 385, 400, 250, T, "Predicted_Churn", "Total Customers", "Predicted Churn Distribution", "clusteredColumnChart"))

    # Prediction accuracy donut
    vcs.append(make_donut(850, 385, 390, 250, T, "Prediction_Correct", "Total Customers", "Prediction Accuracy"))

    # Confusion matrix table
    cm_cols = ["Churn", "Predicted_Churn", "customerID"]
    vcs.append(make_text_box(20, 650, 1240, 50, "Confusion Matrix: TP (Actual=Yes, Predicted=Yes), TN (Actual=No, Predicted=No), FP (Actual=No, Predicted=Yes), FN (Actual=Yes, Predicted=No)"))

    return {
        "id": 4, "name": uid(), "displayName": "Model Performance",
        "filters": "[]", "ordinal": 4, "visualContainers": vcs,
        "config": "{}", "displayOption": 1, "width": 1280, "height": 720
    }

# ============================================================================
# PAGE 6 — HIGH-RISK CUSTOMER TABLE
# ============================================================================
def build_page6():
    vcs = []
    vcs.append(make_text_box(20, 10, 1240, 40, "High-Risk Customer Table"))

    # KPI Cards
    vcs.append(make_card(20, 60, 200, 90, T, "High Risk Customers", "High Risk Customers", "#FFF5F5", "#E74C3C"))
    vcs.append(make_card(230, 60, 200, 90, T, "Critical Priority Customers", "Critical Priority", "#FFF0F0", "#C0392B"))
    vcs.append(make_card(440, 60, 200, 90, T, "At-Risk Revenue", "At-Risk Revenue"))

    # High risk table
    hr_cols = ["customerID", "Churn", "Predicted_Churn", "Predicted_Churn_Probability",
               "Churn_Risk_Percentage", "Churn_Risk_Category", "Retention_Priority",
               "Contract", "MonthlyCharges", "tenure", "Retention_Action"]
    vcs.append(make_table(20, 165, 1240, 530, T, hr_cols, "High-Risk Customers (Probability ≥ 60%)"))

    # Page-level filter for High_Risk_Flag = "Yes"
    page_filter = [{
        "name": uid(),
        "expression": column_ref(T, "High_Risk_Flag"),
        "filter": {
            "Version": 2,
            "From": [{"Name": "c", "Entity": T, "Type": 0}],
            "Where": [{
                "Condition": {
                    "In": {
                        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "High_Risk_Flag"}}],
                        "Values": [[{"Literal": {"Value": "'Yes'"}}]]
                    }
                }
            }]
        },
        "type": "Categorical",
        "howCreated": 1,
        "isHiddenInViewMode": False
    }]

    return {
        "id": 5, "name": uid(), "displayName": "High-Risk Customers",
        "filters": json.dumps(page_filter), "ordinal": 5, "visualContainers": vcs,
        "config": "{}", "displayOption": 1, "width": 1280, "height": 720
    }

# ============================================================================
# ASSEMBLE COMPLETE LAYOUT
# ============================================================================

def build_report_layout():
    """Build the complete Report/Layout JSON."""
    pages = [
        build_page1(),
        build_page2(),
        build_page3(),
        build_page4(),
        build_page5(),
        build_page6(),
    ]

    report_config = {
        "version": "5.73",
        "themeCollection": {
            "baseTheme": {
                "name": "CY26SU05",
                "version": {"visual": "2.9.0", "report": "3.3.0", "page": "2.3.1"},
                "type": 2
            }
        },
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "settings": {
            "useNewFilterPaneExperience": True,
            "allowChangeFilterTypes": True,
            "useStylableVisualContainerHeader": True,
            "queryLimitOption": 6,
            "useEnhancedTooltips": True,
            "exportDataMode": 1,
            "useDefaultAggregateDisplayName": True
        },
        "objects": {
            "section": [{"properties": {"verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}}}]
        }
    }

    layout = {
        "id": 0,
        "resourcePackages": [{
            "resourcePackage": {
                "name": "SharedResources",
                "type": 2,
                "items": [{"type": 202, "path": "BaseThemes/CY26SU05.json", "name": "CY26SU05"}],
                "disabled": False
            }
        }],
        "sections": pages,
        "config": json.dumps(report_config),
        "layoutOptimization": 0
    }

    return layout


def main():
    print("=" * 70)
    print("CCPRA REPORT LAYOUT GENERATOR")
    print("=" * 70)

    layout = build_report_layout()

    # Save layout JSON for inspection
    layout_path = os.path.join(PROJECT_ROOT, "report_layout.json")
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=2, ensure_ascii=False)

    print(f"Report layout generated: {layout_path}")
    print(f"Pages: {len(layout['sections'])}")
    for s in layout['sections']:
        print(f"  - {s['displayName']}: {len(s['visualContainers'])} visuals")

    total_visuals = sum(len(s['visualContainers']) for s in layout['sections'])
    print(f"Total visuals: {total_visuals}")

    # Save as UTF-16-LE for PBIX compatibility
    layout_bin_path = os.path.join(PROJECT_ROOT, "report_layout_utf16.bin")
    layout_json_str = json.dumps(layout, ensure_ascii=False)
    with open(layout_bin_path, "wb") as f:
        f.write(layout_json_str.encode('utf-16-le'))

    print(f"\nUTF-16-LE layout: {layout_bin_path} ({os.path.getsize(layout_bin_path):,} bytes)")


if __name__ == "__main__":
    main()
