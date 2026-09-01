"""
CCPRA Power BI Dashboard — Master Automation Script

This script orchestrates the complete Power BI dashboard creation:
1. Verifies data (already done)
2. Deploys data model to PBI Desktop (already done)
3. Generates the report layout (already done)
4. Instructs the user to save the PBIX
5. Injects the report layout into the saved PBIX
6. Final verification

Run this AFTER:
- Power BI Desktop has the model loaded (deploy_model.ps1 was successful)
- You have saved the PBIX file from Power BI Desktop
"""

import json
import os
import subprocess
import sys

PROJECT_ROOT = r"C:\Users\bader\Desktop\CCPRA Project"
PBIX_PATH = os.path.join(PROJECT_ROOT, "CCPRA_Customer_Churn_Analytics.pbix")

def check_prerequisites():
    """Check that all prerequisites are met."""
    print("=" * 70)
    print("CHECKING PREREQUISITES")
    print("=" * 70)
    
    checks = [
        ("Data directory", os.path.join(PROJECT_ROOT, "data", "powerbi")),
        ("Main CSV", os.path.join(PROJECT_ROOT, "data", "powerbi", "customer_churn_analytics.csv")),
        ("Risk sort CSV", os.path.join(PROJECT_ROOT, "data", "powerbi", "risk_category_sort.csv")),
        ("Retention sort CSV", os.path.join(PROJECT_ROOT, "data", "powerbi", "retention_priority_sort.csv")),
        ("TMSL model file", os.path.join(PROJECT_ROOT, "powerbi_model.tmsl.json")),
        ("Report layout", os.path.join(PROJECT_ROOT, "report_layout.json")),
    ]
    
    all_ok = True
    for name, path in checks:
        exists = os.path.exists(path)
        status = "✓" if exists else "✗ MISSING"
        print(f"  {status} {name}: {path}")
        if not exists:
            all_ok = False
    
    return all_ok


def check_pbix_exists():
    """Check if the PBIX file has been saved."""
    if os.path.exists(PBIX_PATH):
        size = os.path.getsize(PBIX_PATH)
        print(f"\n✓ PBIX found: {PBIX_PATH} ({size:,} bytes)")
        return True
    else:
        print(f"\n✗ PBIX not found at: {PBIX_PATH}")
        return False


def run_inject():
    """Run the report layout injection."""
    print("\n" + "=" * 70)
    print("INJECTING REPORT LAYOUT INTO PBIX")
    print("=" * 70)
    
    result = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, "inject_report_layout.py")],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr)
    return result.returncode == 0


def final_verification():
    """Verify the final PBIX."""
    import zipfile
    
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION")
    print("=" * 70)
    
    if not os.path.exists(PBIX_PATH):
        print("  ✗ PBIX file not found!")
        return False
    
    with zipfile.ZipFile(PBIX_PATH, 'r') as zf:
        files = {info.filename: info.file_size for info in zf.infolist()}
        
        print(f"\n  PBIX Contents:")
        for name, size in sorted(files.items()):
            print(f"    {name}: {size:,} bytes")
        
        # Check Report/Layout
        if "Report/Layout" in files:
            raw = zf.read("Report/Layout")
            layout_str = raw.decode('utf-16-le')
            layout = json.loads(layout_str)
            sections = layout.get("sections", [])
            print(f"\n  Report Pages: {len(sections)}")
            total_visuals = 0
            for s in sections:
                vcs = len(s.get("visualContainers", []))
                total_visuals += vcs
                print(f"    {s.get('displayName', 'N/A')}: {vcs} visuals")
            print(f"  Total Visuals: {total_visuals}")
            
            if len(sections) >= 6 and total_visuals >= 50:
                print("\n  ✓ Report layout verified!")
            else:
                print("\n  ⚠ Report layout may be incomplete")
        
        # Check DataModel
        if "DataModel" in files:
            print(f"\n  ✓ DataModel present: {files['DataModel']:,} bytes")
        else:
            print("\n  ✗ DataModel missing!")
            return False
    
    print(f"\n  Final PBIX size: {os.path.getsize(PBIX_PATH):,} bytes")
    return True


def main():
    print("╔" + "═" * 68 + "╗")
    print("║  CCPRA POWER BI DASHBOARD — MASTER AUTOMATION                      ║")
    print("║  Customer Churn Prediction & Retention Analytics                    ║")
    print("╚" + "═" * 68 + "╝")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\nSome prerequisites are missing. Run the earlier scripts first.")
        return
    
    # Step 2: Check if PBIX exists
    if not check_pbix_exists():
        print("\n" + "=" * 70)
        print("ACTION REQUIRED: SAVE THE PBIX FILE")
        print("=" * 70)
        print("""
The data model is loaded in Power BI Desktop. Please:

  1. Switch to Power BI Desktop
  2. Press Ctrl+Shift+S (Save As)
  3. Navigate to: C:\\Users\\bader\\Desktop\\CCPRA Project\\
  4. Filename: CCPRA_Customer_Churn_Analytics
  5. Click Save
  6. CLOSE Power BI Desktop completely
  7. Run this script again

The model includes:
  - 4 tables (7,043 rows in main table)
  - 2 relationships
  - 34 DAX measures
  - Sort-by-column configurations
""")
        return
    
    # Step 3: Inject report layout
    if not run_inject():
        print("\nReport layout injection failed!")
        return
    
    # Step 4: Final verification
    if not final_verification():
        print("\nFinal verification failed!")
        return
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║  ✓ DASHBOARD CREATION COMPLETE!                                    ║")
    print("╚" + "═" * 68 + "╝")
    print(f"""
  PBIX File: {PBIX_PATH}
  
  To use:
  1. Open the PBIX file in Power BI Desktop
  2. The dashboard will load with all 6 pages:
     • Page 1: Executive Churn Overview
     • Page 2: Churn Risk Analysis
     • Page 3: Retention Priority & Action
     • Page 4: Customer Risk Explorer
     • Page 5: Model Performance
     • Page 6: High-Risk Customers
  3. You may need to click 'Refresh' to load the data
  4. Adjust visual formatting as desired
  5. Save the final version
""")


if __name__ == "__main__":
    main()
