"""
CCPRA Power BI PBIX Builder
Creates a complete PBIX file by:
1. Extracting the DataModel from PBI Desktop's internal storage
2. Constructing the Report/Layout JSON with all 6 pages of visuals
3. Assembling the PBIX ZIP archive
"""

import json
import zipfile
import os
import struct
import uuid
import copy

PROJECT_ROOT = r"C:\Users\bader\Desktop\CCPRA Project"
OUTPUT_PBIX = os.path.join(PROJECT_ROOT, "CCPRA_Customer_Churn_Analytics.pbix")

# ============================================================================
# The DataModel binary cannot be extracted via backup (Diskless mode).
# Instead, we'll construct the PBIX by saving from PBI Desktop.
# But first, let's try to read the internal sqlite model file.
# ============================================================================

AS_WORKSPACE = r"C:\Users\bader\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_e00317cc-e952-4283-83d0-8025c8c299fd"
DB_FOLDER = os.path.join(AS_WORKSPACE, "Data", "3b747c39-23bb-417d-96e0-e976777f0047.0.db")

print("=" * 70)
print("INSPECTING PBI DESKTOP INTERNAL MODEL STORAGE")
print("=" * 70)

for root, dirs, files in os.walk(DB_FOLDER):
    for f in files:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        print(f"  {os.path.relpath(path, DB_FOLDER):40s} | {size:>10,} bytes")

# Check if there's a vmp file (Virtual Memory Partition) that contains the model data
vmp_path = os.path.join(AS_WORKSPACE, "Data", "master.vmp")
if os.path.exists(vmp_path):
    size = os.path.getsize(vmp_path)
    print(f"\nmaster.vmp: {size:,} bytes")

    # VMP files contain serialized model data - let's peek at the header
    with open(vmp_path, "rb") as f:
        header = f.read(min(256, size))
        print(f"Header (first 256 bytes, hex):")
        for i in range(0, min(256, len(header)), 16):
            hex_str = " ".join(f"{b:02x}" for b in header[i:i+16])
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in header[i:i+16])
            print(f"  {i:04x}: {hex_str:48s} {ascii_str}")

# Check the sqlite database
sqlite_path = os.path.join(DB_FOLDER, "metadata.sqlitedb")
if os.path.exists(sqlite_path):
    print(f"\nmetadata.sqlitedb: {os.path.getsize(sqlite_path):,} bytes")
    try:
        import sqlite3
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"SQLite tables: {[t[0] for t in tables]}")
        
        for table_name in [t[0] for t in tables]:
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            count = cursor.fetchone()[0]
            cursor.execute(f"PRAGMA table_info([{table_name}])")
            cols = cursor.fetchall()
            col_names = [c[1] for c in cols]
            print(f"  {table_name}: {count} rows, columns={col_names}")
            
            # Show first few rows if small
            if count <= 10:
                cursor.execute(f"SELECT * FROM [{table_name}] LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    # Truncate long binary data
                    display_row = []
                    for val in row:
                        if isinstance(val, bytes) and len(val) > 100:
                            display_row.append(f"<binary {len(val)} bytes>")
                        else:
                            display_row.append(val)
                    print(f"    {display_row}")
        
        conn.close()
    except Exception as e:
        print(f"SQLite error: {e}")

print("\nDone inspecting.")
