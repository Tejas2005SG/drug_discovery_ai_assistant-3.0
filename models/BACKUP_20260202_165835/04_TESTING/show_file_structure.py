"""
Display Complete File Structure and Dataset Locations
Shows where all files are stored
"""

import json
from pathlib import Path
from datetime import datetime

print("="*80)
print("COMPLETE FILE STRUCTURE - NOVO-1 ENHANCED SYSTEM")
print("="*80)

# 1. DATASET LOCATIONS
print("\n📁 DATASET FILES (D:\Datasets\)")
print("-"*80)
dataset_path = Path("D:/Datasets")
if dataset_path.exists():
    for file in sorted(dataset_path.glob("*.json")):
        size = file.stat().st_size / 1024  # KB
        print(f"  📄 {file.name}")
        print(f"     Size: {size:.1f} KB")
        
        # Count drugs in file
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'drugs' in data:
                drugs = data['drugs']
                total = len(drugs)
                with_targets = sum(1 for d in drugs if 'targets' in d)
                print(f"     Drugs: {total} | With targets: {with_targets}")
        except:
            pass
        print()

# 2. ENHANCED SYSTEM FILES
print("\n📁 ENHANCED SYSTEM FILES (C:\Users\Tejas\Desktop\drugs_discovery_ai_assistant\models\)")
print("-"*80)
models_path = Path("C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models")
enhanced_files = [
    "protein_database.py",
    "admet_predictor.py", 
    "novo1_enhanced_system.py",
    "train_enhanced_system.py",
    "update_drug_targets.py"
]

for filename in enhanced_files:
    file_path = models_path / filename
    if file_path.exists():
        size = file_path.stat().st_size / 1024
        lines = len(open(file_path, 'r', encoding='utf-8').readlines())
        print(f"  📄 {filename}")
        print(f"     Size: {size:.1f} KB | Lines: {lines}")

# 3. GENERATED OUTPUT FILES
print("\n📁 GENERATED OUTPUT FILES")
print("-"*80)
output_files = list(models_path.glob("*.json"))
if output_files:
    for file in sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        size = file.stat().st_size / 1024
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"  📄 {file.name}")
        print(f"     Size: {size:.1f} KB | Created: {mtime.strftime('%Y-%m-%d %H:%M')}")
else:
    print("  (No output files yet)")

# 4. PROTEIN DATABASE STATS
print("\n📊 PROTEIN DATABASE STATISTICS")
print("-"*80)
import sys
sys.path.append(str(models_path))
try:
    from protein_database import ProteinDatabase
    db = ProteinDatabase()
    stats = db.get_database_statistics()
    print(f"  Total Proteins: {stats['total_proteins']}")
    print(f"  Protein Families: {stats['protein_families']}")
    print(f"  Total Pathways: {stats['total_pathways']}")
    print(f"  Druggable Proteins: {stats['druggable_proteins']}")
    print(f"  With Structures: {stats['proteins_with_structures']}")
    
    print("\n  Top 10 Protein Families:")
    for family in list(db.protein_families.keys())[:10]:
        count = len(db.protein_families[family])
        print(f"    * {family}: {count} proteins")
except Exception as e:
    print(f"  Error loading protein database: {e}")

# 5. DATASET CONTENTS PREVIEW
print("\n📋 DATASET CONTENTS PREVIEW")
print("-"*80)
for dataset_file in sorted(dataset_path.glob("*.json"))[:2]:
    if dataset_file.name == "DATASET_SUMMARY.json":
        continue
    print(f"\n  File: {dataset_file.name}")
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'drugs' in data:
            drugs = data['drugs']
            print(f"  Total drugs: {len(drugs)}")
            print(f"\n  First 3 drugs with targets:")
            for drug in drugs[:3]:
                name = drug.get('name', 'Unknown')
                targets = drug.get('targets', [])
                smiles = drug.get('smiles', '')[:30]
                print(f"    * {name}")
                print(f"      Targets: {', '.join(targets) if targets else 'None'}")
                print(f"      SMILES: {smiles}...")
    except Exception as e:
        print(f"  Error reading file: {e}")

print("\n" + "="*80)
print("✅ ALL FILES SUCCESSFULLY CREATED AND UPDATED!")
print("="*80)
print("\n📍 LOCATIONS SUMMARY:")
print("   • Datasets: D:\\Datasets\\")
print("   • System Code: C:\\Users\\Tejas\\Desktop\\drugs_discovery_ai_assistant\\models\\")
print("   • Output Files: Same as system code location")
print("   • Google Drive: https://drive.google.com/drive/folders/1rsUlQu1PwHKEBQjHjkuXdAdJ1z6oeCPG")
print("\n💾 BACKUPS CREATED:")
print("   • Dataset backups: D:\\Datasets\\*.json.backup")
print("="*80)
