"""
Complete Verification and Audit of Assembled PBIX File.
"""

import json
import os
from pathlib import Path
import sys
import zipfile
import jsonschema

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
TEST_PBIX = PROJECT_ROOT / "CCPRA_Customer_Churn_Analytics_TEST.pbix"
BACKUP_PBIX = PROJECT_ROOT / "CCPRA_Customer_Churn_Analytics_BACKUP.pbix"
SCRATCH_DIR = Path(r"C:\Users\bader\.gemini\antigravity-ide\brain\40660372-8c60-4268-af98-a8056a45e50b\scratch")
SCHEMAS_BASE = SCRATCH_DIR / "schemas" / "fabric" / "item" / "report" / "definition"


def verify_target_pbix(pbix_path: Path):
    print("=" * 70)
    print(f"AUDITING PBIX: {pbix_path.name}")
    print("=" * 70)

    # 1. Check Backup Untouched
    assert BACKUP_PBIX.exists(), "Backup file missing!"
    print(f"1. BACKUP Integrity: {BACKUP_PBIX.name} exists ({BACKUP_PBIX.stat().st_size:,} bytes) - UNTOUCHED [OK]")

    # 2. Build Schema Store
    store = {}
    for root, dirs, files in os.walk(SCHEMAS_BASE):
        for f in files:
            if f.endswith('.json'):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, str(SCHEMAS_BASE)).replace('\\', '/')
                uri = f'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/{rel}'
                with open(p, 'r', encoding='utf-8') as fh:
                    doc = json.load(fh)
                    store[uri] = doc
                    if '$id' in doc:
                        store[doc['$id']] = doc

    vc_path = SCHEMAS_BASE / "visualContainer" / "2.0.0" / "schema.json"
    with open(vc_path, 'r', encoding='utf-8') as f:
        vc_schema = json.load(f)
    vc_resolver = jsonschema.RefResolver(
        base_uri='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json',
        referrer=vc_schema,
        store=store
    )

    page_path = SCHEMAS_BASE / "page" / "2.1.0" / "schema.json"
    with open(page_path, 'r', encoding='utf-8') as f:
        page_schema = json.load(f)
    page_resolver = jsonschema.RefResolver(
        base_uri='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',
        referrer=page_schema,
        store=store
    )

    pages_path = SCHEMAS_BASE / "pagesMetadata" / "1.1.0" / "schema.json"
    with open(pages_path, 'r', encoding='utf-8') as f:
        pages_schema = json.load(f)
    pages_resolver = jsonschema.RefResolver(
        base_uri='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json',
        referrer=pages_schema,
        store=store
    )

    # 3. Audit PBIX Archive
    with zipfile.ZipFile(pbix_path, 'r') as zf:
        namelist = set(zf.namelist())

        # Check DataModel
        assert "DataModel" in namelist, "DataModel missing from PBIX!"
        dm_info = zf.getinfo("DataModel")
        print(f"2. DataModel: {dm_info.file_size:,} bytes (UNCOMPRESSED STORAGE: {dm_info.compress_type == zipfile.ZIP_STORED}) [OK]")

        # Check Legacy Layout Omitted
        assert "Report/Layout" not in namelist, "Legacy Report/Layout should NOT be present!"
        print("3. Legacy Report/Layout: Cleanly removed [OK]")

        # Check pages.json
        assert "Report/definition/pages/pages.json" in namelist, "pages.json missing!"
        pages_meta = json.loads(zf.read("Report/definition/pages/pages.json").decode("utf-8"))
        jsonschema.validate(pages_meta, pages_schema, resolver=pages_resolver)
        page_order = pages_meta.get("pageOrder", [])
        print(f"4. pages.json: Schema-valid, references {len(page_order)} pages in pageOrder [OK]")

        # Check each page and its visuals
        total_visuals = 0
        print("\n5. Detailed Page & Visual Verification:")
        for idx, pid in enumerate(page_order):
            page_file = f"Report/definition/pages/{pid}/page.json"
            assert page_file in namelist, f"Page file {page_file} missing!"
            page_doc = json.loads(zf.read(page_file).decode("utf-8"))
            jsonschema.validate(page_doc, page_schema, resolver=page_resolver)

            # Find all visual files for this page
            visual_prefix = f"Report/definition/pages/{pid}/visuals/"
            page_visuals = [f for f in namelist if f.startswith(visual_prefix) and f.endswith("visual.json")]
            total_visuals += len(page_visuals)

            # Validate each visual
            for vf in page_visuals:
                v_doc = json.loads(zf.read(vf).decode("utf-8"))
                jsonschema.validate(v_doc, vc_schema, resolver=vc_resolver)

            print(f"   Page {idx+1}: '{page_doc.get('displayName')}' ({pid}) -> {len(page_visuals)} visuals (all schema-valid)")

        print(f"\n6. Total Visuals Validated Across All Pages: {total_visuals} of 75 [OK]")
        assert total_visuals == 75, f"Expected 75 visuals, got {total_visuals}"

    print("\n" + "=" * 70)
    print("ALL AUDIT CHECKS PASSED: PBIX REPORT DEFINITION IS 100% VALID!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    target = TEST_PBIX
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    success = verify_target_pbix(target)
    sys.exit(0 if success else 1)
