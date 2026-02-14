"""
Complete Folder Structure Analysis and Organization Script
Analyzes current structure and creates organized folder structure
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

print("="*80)
print("COMPLETE FOLDER STRUCTURE ANALYSIS & ORGANIZATION")
print("="*80)

# Get project root
project_root = Path("C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models")

print("\n" + "="*80)
print("CURRENT STRUCTURE ANALYSIS")
print("="*80)

current_files = {
    "Python Scripts (.py)": list(project_root.glob("*.py")),
    "JSON Data (.json)": list(project_root.glob("*.json")),
    "Images (.png)": list(project_root.glob("*.png")),
    "Documentation (.md, .txt)": list(project_root.glob("*.md")) + list(project_root.glob("*.txt")),
    "Other": []
}

# Remove counted files from "Other"
counted = set()
for category, files in current_files.items():
    if category != "Other":
        for f in files:
            counted.add(f.name)

other_files = [f for f in project_root.glob("*") if f.is_file() and f.name not in counted and not f.name.startswith('.')]
current_files["Other"] = other_files

print("\nFILE STATISTICS:")
print("-"*80)
for category, files in current_files.items():
    if files:
        print(f"\n{category}: {len(files)} files")
        for f in files[:5]:
            size = f.stat().st_size / 1024
            print(f"  - {f.name} ({size:.1f} KB)")
        if len(files) > 5:
            print(f"  ... and {len(files)-5} more")

# Check subdirectories
print("\nSUBDIRECTORIES:")
print("-"*80)
for subdir in project_root.iterdir():
    if subdir.is_dir() and not subdir.name.startswith('.'):
        files = list(subdir.rglob("*"))
        py_files = [f for f in files if f.suffix == '.py']
        json_files = [f for f in files if f.suffix == '.json']
        print(f"\n{subdir.name}/")
        print(f"  Total items: {len(files)}")
        print(f"  Python files: {len(py_files)}")
        print(f"  JSON files: {len(json_files)}")

print("\n" + "="*80)
print("PROPOSED ORGANIZED STRUCTURE")
print("="*80)

organized_structure = """
C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models/
|
├── 01_CORE_SYSTEM/                          <- Main system files
│   ├── README.md
│   ├── novo1_enhanced_system.py            <- Enhanced NOVO-1 v3.0
│   ├── novo1_drug_system.py                <- Original NOVO-1 system
│   ├── knowledge_graph.py                  <- Knowledge graph module
│   ├── protein_database.py                 <- 100+ protein database
│   ├── admet_predictor.py                  <- ADMET predictions
│   ├── google_drive_manager.py             <- Drive integration
│   ├── main.py                             <- Main entry point
│   └── quick_start.py                      <- Quick demo
│
├── 02_DATASETS/                             <- All datasets
│   ├── README.md
│   ├── raw_data/                           <- Original datasets
│   │   ├── download_chembl_dataset.py
│   │   ├── retrain_with_real_data.py
│   │   └── load_from_google_drive.py
│   ├── processed/                          <- Processed data
│   └── backups/                            <- Backup files
│
├── 03_TRAINING/                             <- Training scripts
│   ├── README.md
│   ├── train_enhanced_system.py            <- Main training
│   ├── train_complete.py
│   ├── train_final.py
│   ├── train_now.py
│   ├── train_quick.py
│   └── update_drug_targets.py              <- Target mapping
│
├── 04_TESTING/                              <- Testing & validation
│   ├── README.md
│   ├── test_neuro_from_drive.py
│   ├── test_neuro_symptoms.py
│   ├── test_google_drive_datasets.py
│   ├── covid_empirical_test.py
│   ├── test_and_visualize.py
│   ├── benchmark_comparison.py
│   └── empirical_test/                     <- Existing test suite
│       ├── comparison/
│       ├── data/
│       ├── models/
│       ├── results/
│       ├── visualization/
│       └── run_full_test.py
│
├── 05_RESULTS/                              <- Generated outputs
│   ├── README.md
│   ├── training_results/                   <- Training outputs
│   │   ├── trained_enhanced_system_*.json
│   │   └── training_output.txt
│   ├── test_results/                       <- Test outputs
│   │   ├── enhanced_test_results_*.json
│   │   ├── neuro_test_results_drive.json
│   │   └── covid_empirical_test_results.json
│   └── generated_candidates/               <- Drug candidates
│       └── all_42_covid_candidates.json
│
├── 06_VISUALIZATION/                        <- Charts & graphs
│   ├── README.md
│   ├── generate_visualizations.py
│   ├── covid_benchmark_charts.py
│   ├── final_visualizations.py
│   └── charts/                             <- PNG outputs
│       ├── covid_benchmark_professional.png
│       ├── architecture_diagram.png
│       └── *.png
│
├── 07_DOCUMENTATION/                        <- Docs & guides
│   ├── README.md
│   ├── IMPLEMENTATION_GUIDE.md             <- Main guide
│   ├── requirements.txt
│   └── sample.txt
│
└── 08_LEGACY/                               <- Legacy code
    ├── README.md
    ├── drug_discovery/                     <- Old drug discovery
    └── txgnn/                              <- TXGNN framework
"""

print(organized_structure)

print("\n" + "="*80)
print("TOTAL FILES TO ORGANIZE:")
print("="*80)

total_py = len(current_files["Python Scripts (.py)"])
total_json = len(current_files["JSON Data (.json)"])
total_png = len(current_files["Images (.png)"])
total_doc = len(current_files["Documentation (.md, .txt)"])
total_other = len(current_files["Other"])

print(f"\nPython Scripts: {total_py}")
print(f"JSON Files: {total_json}")
print(f"Image Files: {total_png}")
print(f"Documentation: {total_doc}")
print(f"Other Files: {total_other}")
print(f"\nTOTAL: {total_py + total_json + total_png + total_doc + total_other} files")

print("\n" + "="*80)
print("LEGACY FOLDERS (Keep as-is):")
print("="*80)
print("- drug_discovery/ (6 Python files)")
print("- txgnn/ (11 Python files, README, guides)")
print("- empirical_test/ (9 Python files, data, results)")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nNext: Run organize_folders.py to create structure")
print("All files will be preserved - just reorganized!")
print("="*80)
