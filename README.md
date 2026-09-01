# Customer Churn Prediction & Retention Analytics (CCPRA)

An end-to-end enterprise customer churn analytics and predictive intelligence solution integrating automated Python data engineering, exploratory data analysis, machine learning classification, customer-level risk scoring and segmentation, and an interactive 6-page executive Power BI dashboard.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Project Objectives](#project-objectives)
- [Project Pipeline](#project-pipeline)
- [Phase 1 — Data Cleaning & Feature Engineering](#phase-1--data-cleaning--feature-engineering)
- [Phase 2 — Exploratory Data Analysis (EDA)](#phase-2--exploratory-data-analysis-eda)
- [Phase 3 — Machine Learning Modeling & Evaluation](#phase-3--machine-learning-modeling--evaluation)
- [Phase 4 — Prediction & Retention Analytics](#phase-4--prediction--retention-analytics)
- [Power BI Executive Dashboard](#power-bi-executive-dashboard)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Key Business Value](#key-business-value)
- [Limitations](#limitations)

---

## Project Overview

Customer churn poses a significant challenge in the telecommunications industry, where acquisition costs heavily exceed customer retention costs. The **Customer Churn Prediction & Retention Analytics (CCPRA)** project bridges advanced data science and business operations by delivering an end-to-end, production-ready system:

1. **Python Data Engineering**: Cleans, validates, and engineers domain features from raw telecommunication records.
2. **Exploratory Data Analysis**: Quantifies churn distribution across customer demographics, account structures, and subscribed services.
3. **Machine Learning Pipeline**: Evaluates multiple supervised classification algorithms under strict holdout validation, optimizing for discrimination power (ROC-AUC) and recall.
4. **Predictive Scoring & Risk Segmentation**: Assigns individual churn probabilities, operational risk categories, and prescriptive retention actions to all 7,043 customers.
5. **Business Intelligence (Power BI)**: Deploys a standardized star-schema semantic model and a 6-page interactive report for executive decision-makers and frontline retention specialists.

---

## Dataset

The project utilizes the **Telco Customer Churn** dataset:
- **Total Records**: 7,043 customer accounts
- **Raw Features**: 21 columns comprising customer demographics (e.g., gender, senior citizenship, partner/dependents), service subscriptions (e.g., internet type, tech support, online security, streaming), account tenure, contract terms, billing preferences, and historical charges.
- **Analytical Output**: Cleaned and enriched dataset with engineered cohorts (`Tenure_Group`, `Monthly_Charge_Range`), predicted probabilities, operational risk tiers, priority levels, and recommended actions (32 columns total).

---

## Project Objectives

- **Analyze Churn Behavior**: Identify statistical patterns, behavioral traits, and service combinations associated with elevated churn rates.
- **Identify High-Risk Segments**: Segment customer groups based on observed contract structures, tenure, and billing mechanisms.
- **Train & Compare Predictive Models**: Benchmark supervised classifiers using rigorous train-test splitting and cross-validation to isolate top-performing algorithms.
- **Predict Customer Churn**: Generate calibrated individual churn probabilities for every customer in the subscriber base.
- **Segment Risk Tiers**: Categorize customers into defined operational tiers (*Low Risk*, *Medium Risk*, *High Risk*).
- **Prescribe Targeted Retention Actions**: Map risk tiers and observed account friction points to prioritized, cost-effective interventions (*Critical*, *High*, *Medium*, *Low*).
- **Deliver Executive Power BI Dashboards**: Provide visual business intelligence enabling executive monitoring, cohort deep-dives, and individual customer lookups.

---

## Project Pipeline

```text
Raw Dataset (original_dataset.csv)
       │
       ▼
Phase 1: Data Cleaning & Feature Engineering (data_cleaning.py)
       │
       ▼
Phase 2: Exploratory Data Analysis (exploratory_analysis.py)
       │
       ▼
Phase 3: Machine Learning Modeling & Comparison (train_model.py)
       │
       ▼
Model Selection & Artifact Serialization (selected_churn_model.joblib)
       │
       ▼
Phase 4: Full-Base Prediction & Retention Strategy (generate_predictions.py)
       │
       ▼
Power BI Analytical Export & Star Schema (customer_churn_analytics.csv)
       │
       ▼
Interactive 6-Page Power BI Executive Dashboard (.pbix)
```

---

## Phase 1 — Data Cleaning & Feature Engineering

Executed via `src/data_cleaning.py`:
- **100% Record Preservation**: All 7,043 customer records were retained (0 rows dropped).
- **Data Type Resolution**: `TotalCharges` was stored as object/string with whitespace entries for new customers; parsed to numeric (`float64`).
- **Missing Value Handling**: Exactly 11 records contained blank `TotalCharges` strings, all corresponding to customers with `tenure = 0` (first-cycle accounts). These were cleanly imputed to `0.0`, resulting in **zero missing values** across the entire dataset.
- **Primary Key Validation**: Confirmed `customerID` is 100% unique across all 7,043 rows.
- **Feature Engineering**:
  - `Tenure_Group`: Segmented into 4 cohorts: `0–12 Months`, `13–24 Months`, `25–48 Months`, and `49–72 Months`.
  - `Monthly_Charge_Range`: Quantile-informed pricing bins: `$0–$35`, `$35.01–$70`, `$70.01–$90`, and `$90.01–$120`.

---

## Phase 2 — Exploratory Data Analysis (EDA)

Executed via `src/exploratory_analysis.py`, generating **20 analytical CSV files in `outputs/analysis/`** and **20 publication-grade PNG charts in `outputs/charts/`**. While addressing 10 core analytical questions (AQ1–AQ10), questions AQ4 (service subscriptions) and AQ8 (demographic factors) contain multiple sub-analyses (evaluating individual services and demographic attributes alongside combined summaries), which is why AQ1–AQ10 produce 20 detailed analytical outputs. Key verified observational findings include:

- **Overall Baseline Churn Rate**: **26.54%** (1,869 churned vs. 5,174 retained customers).
- **Contract Duration**: Customers on **Month-to-month contracts** experienced a **42.71%** churn rate, compared to **11.27%** for One-year and only **2.83%** for Two-year contracts.
- **Tenure Lifecycle**: Highest vulnerability occurs in year one (**0–12 months tenure**) at **47.44%** churn rate, dropping monotonically to **9.51%** for long-tenure customers (49–72 months).
- **Internet Service Architecture**: **Fiber optic internet** subscribers showed a **41.89%** churn rate, compared to **18.96%** for DSL and **7.40%** for non-internet customers.
- **Payment Methods**: Customers paying via **Electronic check** had an observed churn rate of **45.29%**, substantially higher than Credit card (15.24%), Bank transfer (16.71%), or Mailed check (19.11%).
- **Senior Demographics**: **Senior citizen** subscribers experienced a **41.68%** churn rate versus **23.61%** for non-seniors.
- **High-Risk Interaction**: The combination of **Month-to-month contracts** and **Fiber optic internet** represented the single largest high-risk concentration across the customer base.

*(Note: These figures reflect observational distributions within the historical dataset and do not imply causal mechanisms.)*

---

## Phase 3 — Machine Learning Modeling & Evaluation

Executed via `src/train_model.py`. An isolated machine learning pipeline was trained on an 80/20 stratified split (5,634 training records; 1,409 holdout test records) using one-hot encoding for categorical variables and standard scaling for numeric features.

### Official Holdout Test Performance (Untouched Evaluation Set)

| Evaluation Metric | Logistic Regression (Selected) | Random Forest |
| :--- | :---: | :---: |
| **ROC-AUC** | **84.21%** (0.8421) | 81.93% (0.8193) |
| **Accuracy** | **80.55%** (0.8055) | 78.71% (0.7871) |
| **Precision** | **65.72%** (0.6572) | 62.67% (0.6267) |
| **Recall** | **55.88%** (0.5588) | 48.93% (0.4893) |
| **F1 Score** | **60.40%** (0.6040) | 54.96% (0.5496) |

### Model Selection Rationale
**Logistic Regression** was selected as the approved production model because it outperformed Random Forest across every primary evaluation metric on the holdout test set:
- **+2.28% higher ROC-AUC** (84.21% vs. 81.93%), demonstrating superior probability calibration and discrimination across all classification thresholds.
- **+6.95% higher Recall** (55.88% vs. 48.93%), capturing significantly more true churners before departure.
- **+3.05% higher Precision** (65.72% vs. 62.67%) and **+5.44% higher F1 Score** (60.40% vs. 54.96%).
- Full pipeline and coefficients serialized to `models/selected_churn_model.joblib`.

---

## Phase 4 — Prediction & Retention Analytics

Executed via `src/generate_predictions.py`. The approved model was applied to score all 7,043 customer accounts, generating calibrated churn probabilities and operational segments:

- **Total Base Scored**: 7,043 customers
- **Model Predicted Churn (0.50 cutoff)**: 1,562 customers (22.18%)
- **Average Churn Probability**: 26.59% (Median: 18.87%, Range: 0.16% – 85.55%)

### Churn Risk Segmentation
- **Low Risk** (`Prob < 0.30`): **4,371 customers** (62.06%)
- **Medium Risk** (`0.30 <= Prob < 0.60`): **1,633 customers** (23.19%)
- **High Risk** (`Prob >= 0.60`): **1,039 customers** (14.75%)

### Operational Retention Priorities & Actions
- **Priority 1 — Critical** (`Prob >= 0.80`): **49 customers** (0.70%)
- **Priority 2 — High** (`0.60 <= Prob < 0.80`): **990 customers** (14.06%)
- **Priority 3 — Medium** (`0.30 <= Prob < 0.60`): **1,633 customers** (23.19%)
- **Priority 4 — Low** (`Prob < 0.30`): **4,371 customers** (62.06%)

### Segment Definitions & Fields
- **`Churn_Risk_Category`**: Strategic risk tiering (`Low Risk`, `Medium Risk`, `High Risk`) utilized for macro resource planning.
- **`High_Risk_Flag`**: Binary operational trigger (`Yes`/`No`) isolating all customers with churn probability $\ge 0.60$ (1,039 total).
- **`Retention_Priority`**: Four-level triage rank (`Critical`, `High`, `Medium`, `Low`) guiding intervention urgency.
- **`Retention_Action`**: Deterministic rule-based interventions mapped to customer friction points (e.g., contract upgrade incentives, automatic payment setup, tech support onboarding).

---

## Power BI Executive Dashboard

The solution includes a comprehensive, multi-page business intelligence report built on a star schema with explicit DAX measures and dimension sort orders. The dashboard is structured into six dedicated pages:

1. **Executive Overview**: High-level KPI scorecards (Total Customers, Total Churned, Churn Rate, High-Risk Volume, MRR at Risk), tenure trends, and contract distributions.
2. **Churn Risk Analysis**: Deep breakdown of risk categories, contract risks, billing methods, and service package correlations.
3. **Retention Priority & Action**: Operational command center displaying priority tiers, recommended retention initiatives, and associated monthly revenue exposure.
4. **Customer Risk Explorer**: Granular, filterable customer intelligence view with dynamic risk brackets, tenure slicers, and searchable account profiles.
5. **Model Performance**: Technical executive validation showcasing holdout test metrics, confusion matrix results, ROC-AUC comparison, and threshold analysis.
6. **High-Risk Customers**: Actionable operational roster isolating the 1,039 high-risk accounts and 49 critical-priority accounts with contact profiles and recommended retention plays.

---

## Technology Stack

- **Data Processing & Analytics**: Python 3.10+, Pandas, NumPy
- **Machine Learning**: Scikit-learn (LogisticRegression, RandomForestClassifier, Pipeline, ColumnTransformer)
- **Serialization**: Joblib
- **Data Visualization**: Matplotlib, Seaborn
- **Business Intelligence**: Microsoft Power BI Desktop, DAX (Data Analysis Expressions), Power Query (M)

---

## Project Structure

```text
CCPRA Project/
│
├── .gitignore                                 # Git ignore configuration
├── requirements.txt                           # Production pipeline dependencies
├── README.md                                  # Comprehensive project documentation
├── PROJECT_STRUCTURE.txt                      # Project layout tree
│
├── CCPRA_Customer_Churn_Analytics_FINAL.pbix  # Final Power BI production report
├── CCPRA_Customer_Churn_Analytics_WORKING.pbix# Power BI working development copy
├── CCPRA_Customer_Churn_Analytics_BACKUP.pbix # Power BI verified backup copy
│
├── data/
│   ├── raw/
│   │   └── original_dataset.csv               # Pristine raw dataset (7,043 rows)
│   ├── processed/
│   │   └── cleaned_customer_churn.csv         # Cleaned data with engineered features
│   └── powerbi/
│       ├── customer_churn_analytics.csv       # 32-column Power BI analytical fact table
│       ├── customer_churn_data_dictionary.csv # Complete metadata and field dictionary
│       ├── risk_category_sort.csv             # Dimension sort table for risk categories
│       └── retention_priority_sort.csv        # Dimension sort table for priority levels
│
├── src/
│   ├── data_cleaning.py                       # Phase 1: Cleaning & validation
│   ├── exploratory_analysis.py                # Phase 2: EDA & figure generation
│   ├── train_model.py                         # Phase 3: ML training, tuning & evaluation
│   └── generate_predictions.py                # Phase 4: Scoring, risk tiers & retention logic
│
├── models/
│   └── selected_churn_model.joblib            # Approved production model artifact
│
├── outputs/
│   ├── data_cleaning_report.txt               # Phase 1 data validation report
│   ├── eda_summary.txt                        # Phase 2 analytical findings report
│   ├── eda_validation_report.txt              # Phase 2 verification log
│   ├── analysis/                              # 20 analytical CSV files in outputs/analysis/
│   ├── charts/                                # 20 PNG charts in outputs/charts/
│   ├── model_results/                         # Phase 3 model metrics, ROC curves & CMs
│   └── predictions/                           # Phase 4 prediction summaries & logs
│
├── tools/
│   └── archive_powerbi_automation/            # Safely archived PBIR/TMSL automation scripts
│
└── archive/
    ├── original_download/                     # Redundant initial download archive
    │   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
    └── pbix_versions/                         # Archived earlier PBIX versions and test files
```

---

## How to Run

### 1. Environment Setup
Clone the repository and install required packages:
```bash
pip install -r requirements.txt
```

### 2. Execute Data & Modeling Pipeline
Run each phase sequentially from the project root:

```bash
# Phase 1: Clean raw data and engineer features
python src/data_cleaning.py

# Phase 2: Run exploratory data analysis and generate charts
python src/exploratory_analysis.py

# Phase 3: Train machine learning models and evaluate performance
python src/train_model.py

# Phase 4: Generate calibrated churn predictions and Power BI tables
python src/generate_predictions.py
```

### 3. Open Power BI Dashboard
Launch Microsoft Power BI Desktop and open:
- `CCPRA_Customer_Churn_Analytics_FINAL.pbix` (or `CCPRA_Customer_Churn_Analytics_WORKING.pbix`)
- If prompted to refresh data, ensure data source points to `data/powerbi/customer_churn_analytics.csv`.

---

## Key Business Value

- **Targeted Proactive Retention**: Shifts retention strategies from reactive firefighting after cancellation to proactive outreach before churn occurs.
- **Prioritized Budget Allocation**: Focuses limited retention marketing spend on the 49 Critical and 990 High-Risk accounts rather than diffusing budget across low-risk customers.
- **Actionable Account Remediation**: Equips account representatives with specific playbooks tailored to individual account drivers (e.g., offering annual contract discounts to high-churn month-to-month fiber customers).
- **Executive Visibility**: Provides leadership with continuous visibility into customer health, churn velocity, and monthly recurring revenue (MRR) exposure.

---

## Limitations

- **Cross-Sectional Observational Data**: The underlying dataset represents a historical snapshot; observed correlations between services (such as Fiber optic or Electronic checks) and churn do not prove causality without controlled A/B testing.
- **Static Feature Space**: Customer behavior evolves; model performance will experience concept drift over time. Periodic retraining is required as updated customer lifecycle data becomes available.
- **Deterministic Action Mapping**: Retention actions are generated via heuristic rules mapped to customer risk scores and account features; operational testing should be conducted to establish true campaign uplift.
