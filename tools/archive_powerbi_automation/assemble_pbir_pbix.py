"""
CCPRA PBIR PBIX Assembler

Packages the modern PBIR report definition into the PBIX file.
Creates CCPRA_Customer_Churn_Analytics_TEST.pbix first to preserve backup and existing files.
"""

import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

from generate_pbir_definition import generate_all_pbir_files

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_PBIX = PROJECT_ROOT / "CCPRA_Customer_Churn_Analytics.pbix"
BACKUP_PBIX = PROJECT_ROOT / "CCPRA_Customer_Churn_Analytics_BACKUP.pbix"
TEST_PBIX = PROJECT_ROOT / "CCPRA_Customer_Churn_Analytics_TEST.pbix"


def assemble_pbix(target_pbix: Path) -> bool:
    print("=" * 70)
    print("CCPRA PBIR PBIX ASSEMBLER")
    print("=" * 70)

    if not SOURCE_PBIX.exists():
        print(f"ERROR: Source PBIX not found at: {SOURCE_PBIX}")
        return False

    # Verify backup exists and record its stats
    if BACKUP_PBIX.exists():
        backup_size = BACKUP_PBIX.stat().st_size
        print(f"Verified BACKUP exists ({backup_size:,} bytes) - will NOT be touched.")
    else:
        print(f"WARNING: No backup found at {BACKUP_PBIX}. Creating one now...")
        shutil.copy2(SOURCE_PBIX, BACKUP_PBIX)

    # 1. Read existing PBIX contents
    print(f"\nReading source PBIX: {SOURCE_PBIX} ({SOURCE_PBIX.stat().st_size:,} bytes)...")
    existing_files = {}
    with zipfile.ZipFile(SOURCE_PBIX, 'r') as zf:
        for info in zf.infolist():
            # Skip legacy Report/Layout
            if info.filename == "Report/Layout":
                print(f"  [OMIT LEGACY]: {info.filename}")
                continue
            # Skip old injected theme CY26SU05
            if "CY26SU05" in info.filename:
                print(f"  [OMIT OLD THEME]: {info.filename}")
                continue
            # Skip old default blank page
            if info.filename.startswith("Report/definition/pages/"):
                print(f"  [REPLACING OLD PAGE]: {info.filename}")
                continue
            existing_files[info.filename] = zf.read(info.filename)
            print(f"  Preserved: {info.filename} ({len(existing_files[info.filename]):,} bytes)")

    # 2. Generate modern PBIR report definition
    print("\nGenerating PBIR definition (6 pages, 75 visuals)...")
    pbir_files = generate_all_pbir_files()
    print(f"  Generated {len(pbir_files)} PBIR definition files.")

    for filename, data in pbir_files.items():
        existing_files[filename] = data

    # 3. Write target PBIX
    print(f"\nWriting target PBIX: {target_pbix}")
    temp_pbix = target_pbix.with_name(f"{target_pbix.name}.tmp")
    with zipfile.ZipFile(temp_pbix, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, data in existing_files.items():
            if filename == "DataModel":
                zf.writestr(filename, data, compress_type=zipfile.ZIP_STORED)
            else:
                zf.writestr(filename, data)

    # Atomically replace
    if target_pbix.exists():
        target_pbix.unlink()
    os.replace(temp_pbix, target_pbix)
    print(f"Final target PBIX size: {target_pbix.stat().st_size:,} bytes")

    # 4. Verification of the target PBIX
    print("\nVerifying target PBIX contents...")
    with zipfile.ZipFile(target_pbix, 'r') as zf:
        namelist = set(zf.namelist())

        # Check pages.json
        assert "Report/definition/pages/pages.json" in namelist, "Missing pages.json"
        pages_meta = json.loads(zf.read("Report/definition/pages/pages.json").decode("utf-8"))
        page_order = pages_meta.get("pageOrder", [])
        print(f"  pages.json pageOrder count: {len(page_order)}")
        assert len(page_order) == 6, f"Expected 6 pages in pageOrder, got {len(page_order)}"

        # Check each page.json
        for pid in page_order:
            page_json_path = f"Report/definition/pages/{pid}/page.json"
            assert page_json_path in namelist, f"Missing {page_json_path}"
            pdef = json.loads(zf.read(page_json_path).decode("utf-8"))
            print(f"  Page '{pdef.get('displayName')}' ({pid}): OK")

        # Check visuals count
        visual_files = [f for f in namelist if f.endswith("visual.json")]
        print(f"  Total visual.json files in archive: {len(visual_files)}")
        assert len(visual_files) == 75, f"Expected 75 visual.json files, got {len(visual_files)}"

        # Check DataModel intact
        assert "DataModel" in namelist, "Missing DataModel!"
        dm_size = zf.getinfo("DataModel").file_size
        print(f"  DataModel size: {dm_size:,} bytes (INTACT)")

        # Confirm Report/Layout is NOT in archive
        assert "Report/Layout" not in namelist, "Legacy Report/Layout should NOT be in archive"
        print("  Legacy Report/Layout removed: OK")

    print("\n" + "=" * 70)
    print("ASSEMBLY & VERIFICATION SUCCESSFUL!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    target = TEST_PBIX
    if len(sys.argv) > 1 and sys.argv[1] == "--final":
        target = SOURCE_PBIX

    success = assemble_pbix(target)
    sys.exit(0 if success else 1)
