r"""
CCPRA PBIX Assembler
Injects the generated report layout into a saved PBIX file.

Usage:
1. In Power BI Desktop, press Ctrl+Shift+S to Save As
2. Save to: C:\Users\bader\Desktop\CCPRA Project\CCPRA_Customer_Churn_Analytics.pbix
3. Close Power BI Desktop
4. Run this script to inject the 6-page report layout
5. Reopen the PBIX in Power BI Desktop
"""

import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parent
PBIX_PATH = PROJECT_ROOT / "CCPRA_Customer_Churn_Analytics.pbix"
LAYOUT_PATH = PROJECT_ROOT / "report_layout.json"
BACKUP_PBIX = PROJECT_ROOT / "CCPRA_Customer_Churn_Analytics_BACKUP.pbix"

# Also read the base theme from an existing PBIX
REFERENCE_PBIX = Path(r"C:\Users\bader\Desktop\BUSINESS INTELLEGENCE\BI_Week2_report1.pbix")


def main():
    print("=" * 70)
    print("CCPRA PBIX ASSEMBLER")
    print("=" * 70)

    if not PBIX_PATH.exists():
        print(f"\nERROR: PBIX file not found at: {PBIX_PATH}")
        print("\nPlease save the Power BI report first:")
        print("  1. Open Power BI Desktop (it should show your loaded model)")
        print("  2. Press Ctrl+Shift+S (Save As)")
        print(f"  3. Navigate to: {PROJECT_ROOT}")
        print("  4. Filename: CCPRA_Customer_Churn_Analytics")
        print("  5. Click Save")
        print("  6. CLOSE Power BI Desktop")
        print("  7. Run this script again")
        return False

    print(f"\nSource PBIX: {PBIX_PATH} ({PBIX_PATH.stat().st_size:,} bytes)")

    # Create backup
    shutil.copy2(PBIX_PATH, BACKUP_PBIX)
    print(f"Backup: {BACKUP_PBIX}")

    # Load report layout
    with open(LAYOUT_PATH, "r", encoding="utf-8") as f:
        layout = json.load(f)
    print(f"Report layout loaded: {len(layout['sections'])} pages, {sum(len(s['visualContainers']) for s in layout['sections'])} visuals")

    # Read existing PBIX contents
    print("\nReading existing PBIX contents...")
    existing_files = {}
    with zipfile.ZipFile(PBIX_PATH, 'r') as zf:
        for info in zf.infolist():
            existing_files[info.filename] = zf.read(info.filename)
            print(f"  Read: {info.filename} ({len(existing_files[info.filename]):,} bytes)")

    # Get the base theme from reference PBIX
    theme_data = None
    if REFERENCE_PBIX.exists():
        with zipfile.ZipFile(REFERENCE_PBIX, 'r') as ref_zf:
            for info in ref_zf.infolist():
                if "BaseThemes" in info.filename:
                    theme_data = ref_zf.read(info.filename)
                    theme_filename = info.filename
                    print(f"  Theme from reference: {info.filename}")
                    break

    # Replace Report/Layout with our generated layout
    layout_json_str = json.dumps(layout, ensure_ascii=False)
    layout_bytes = layout_json_str.encode('utf-16-le')
    existing_files["Report/Layout"] = layout_bytes
    print(f"\n  Injected Report/Layout: {len(layout_bytes):,} bytes")

    # Add theme file if we have one
    if theme_data:
        existing_files["Report/StaticResources/SharedResources/BaseThemes/CY26SU05.json"] = theme_data
        print(f"  Injected theme: {len(theme_data):,} bytes")

    # Write new PBIX
    print(f"\nWriting new PBIX: {PBIX_PATH}")
    temp_pbix = PBIX_PATH.with_name(f"{PBIX_PATH.name}.tmp")
    with zipfile.ZipFile(temp_pbix, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, data in existing_files.items():
            # DataModel should not be compressed (it's already compressed)
            if filename == "DataModel":
                zf.writestr(filename, data, compress_type=zipfile.ZIP_STORED)
            else:
                zf.writestr(filename, data)
            print(f"  Written: {filename} ({len(data):,} bytes)")

    # Replace original with new
    os.replace(temp_pbix, PBIX_PATH)
    print(f"\nFinal PBIX: {PBIX_PATH} ({PBIX_PATH.stat().st_size:,} bytes)")

    print("\n" + "=" * 70)
    print("PBIX ASSEMBLY COMPLETE!")
    print("=" * 70)
    print(f"\nOpen the file in Power BI Desktop:")
    print(f"  {PBIX_PATH}")
    print(f"\nPages injected:")
    for s in layout['sections']:
        print(f"  - {s['displayName']}: {len(s['visualContainers'])} visuals")
    print(f"\nTotal: {sum(len(s['visualContainers']) for s in layout['sections'])} visuals across {len(layout['sections'])} pages")
    print(f"\nBackup saved at: {BACKUP_PBIX}")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

