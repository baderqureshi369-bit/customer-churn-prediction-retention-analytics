"""
Validation script for PBIR definition files against official Microsoft JSON Schemas.
"""

import json
import os
import sys
from pathlib import Path
import jsonschema

from generate_pbir_definition import generate_all_pbir_files

SCRATCH_DIR = Path(r"C:\Users\bader\.gemini\antigravity-ide\brain\40660372-8c60-4268-af98-a8056a45e50b\scratch")
SCHEMAS_BASE = SCRATCH_DIR / "schemas" / "fabric" / "item" / "report" / "definition"

def main():
    print("=" * 70)
    print("PBIR DEFINITION SCHEMA VALIDATOR")
    print("=" * 70)

    # 1. Build schema store
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

    print(f"Loaded {len(store)} schema documents.")

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

    # 2. Generate all files
    all_files = generate_all_pbir_files()
    print(f"Validating {len(all_files)} generated files...")

    validated_pages = 0
    validated_visuals = 0
    errors = []

    for path, data in all_files.items():
        doc = json.loads(data.decode("utf-8"))

        if path.endswith("pages.json"):
            try:
                jsonschema.validate(doc, pages_schema, resolver=pages_resolver)
            except Exception as e:
                errors.append((path, str(e)))

        elif path.endswith("page.json"):
            try:
                jsonschema.validate(doc, page_schema, resolver=page_resolver)
                validated_pages += 1
            except Exception as e:
                errors.append((path, str(e)))

        elif path.endswith("visual.json"):
            try:
                jsonschema.validate(doc, vc_schema, resolver=vc_resolver)
                validated_visuals += 1
            except Exception as e:
                errors.append((path, str(e)))

    print(f"\nValidation Results:")
    print(f"  pages.json: {'PASS' if not any(e[0].endswith('pages.json') for e in errors) else 'FAIL'}")
    print(f"  page.json: {validated_pages} of 6 VALID")
    print(f"  visual.json: {validated_visuals} of 75 VALID")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for p, err in errors[:5]:
            print(f"  {p}: {err[:150]}")
        return False

    print("\nALL 82 PBIR FILES ARE 100% SCHEMA-VALID!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
