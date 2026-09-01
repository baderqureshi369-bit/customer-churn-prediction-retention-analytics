"""
Examine the Report/Layout from a more complex PBIX to understand visual container format.
"""
import zipfile
import json
import os
import sys

# Use the largest/most complex PBIX
pbix_path = r"C:\Users\bader\Desktop\BUSINESS INTELLEGENCE\BI_Week3_report2.pbix"

print(f"Examining PBIX: {pbix_path}")
print(f"File size: {os.path.getsize(pbix_path):,} bytes")

with zipfile.ZipFile(pbix_path, 'r') as zf:
    print("\nFiles:")
    for info in zf.infolist():
        print(f"  {info.filename:60s} | {info.file_size:>10,}")

    # Read Report/Layout (UTF-16-LE)
    raw = zf.read("Report/Layout")
    layout_str = raw.decode('utf-16-le')
    layout = json.loads(layout_str)

    print(f"\nReport Layout keys: {list(layout.keys())}")
    print(f"Number of sections (pages): {len(layout.get('sections', []))}")

    for i, section in enumerate(layout.get('sections', [])):
        vcs = section.get('visualContainers', [])
        print(f"\n  Page {i}: '{section.get('displayName', 'N/A')}' - {len(vcs)} visuals - {section.get('width', '?')}x{section.get('height', '?')}")

        for j, vc in enumerate(vcs):
            config_str = vc.get('config', '{}')
            config = json.loads(config_str) if isinstance(config_str, str) else config_str
            visual_type = "unknown"
            try:
                visual_type = config.get('singleVisual', {}).get('visualType', 'unknown')
            except:
                pass

            x = vc.get('x', '?')
            y = vc.get('y', '?')
            w = vc.get('width', '?')
            h = vc.get('height', '?')
            print(f"    Visual {j}: type={visual_type:20s} | pos=({x},{y}) | size={w}x{h}")

    # Print full config of first page, first visual for detailed format understanding
    if layout.get('sections'):
        first_section = layout['sections'][0]
        if first_section.get('visualContainers'):
            first_vc = first_section['visualContainers'][0]
            config = json.loads(first_vc.get('config', '{}'))
            print("\n" + "=" * 70)
            print("FIRST VISUAL CONFIG (detailed):")
            print("=" * 70)
            print(json.dumps(config, indent=2)[:5000])

            if 'dataTransforms' in first_vc:
                dt = json.loads(first_vc['dataTransforms'])
                print("\n" + "=" * 70)
                print("FIRST VISUAL dataTransforms (first 3000 chars):")
                print("=" * 70)
                print(json.dumps(dt, indent=2)[:3000])

    # Print the report-level config
    report_config = json.loads(layout.get('config', '{}'))
    print("\n" + "=" * 70)
    print("REPORT CONFIG:")
    print("=" * 70)
    print(json.dumps(report_config, indent=2)[:2000])

    # Version file
    version = zf.read("Version").decode('utf-16-le')
    print(f"\nVersion: {version}")

    # Settings
    settings_raw = zf.read("Settings")
    settings_str = settings_raw.decode('utf-16-le')
    settings = json.loads(settings_str)
    print(f"\nSettings: {json.dumps(settings, indent=2)}")

    # Metadata
    meta_raw = zf.read("Metadata")
    meta_str = meta_raw.decode('utf-16-le')
    meta = json.loads(meta_str)
    print(f"\nMetadata: {json.dumps(meta, indent=2)}")

    # DataMashup size
    dm_size = zf.getinfo("DataModel").file_size
    print(f"\nDataModel size: {dm_size:,} bytes")
