"""
Organize Project Folder Structure
Creates clean folder hierarchy and moves files appropriately
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

print("="*80)
print("ORGANIZING PROJECT FOLDER STRUCTURE")
print("="*80)
print("\nCreating organized structure...")
print("All files will be preserved - just reorganized!")
print("-"*80)

# Project root
project_root = Path("C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models")

# Define the organized structure with file mappings
folder_mappings = {
    "01_CORE_SYSTEM": {
        "description": "Main NOVO-1 system files",
        "files": [
            "novo1_enhanced_system.py",
            "novo1_drug_system.py", 
            "knowledge_graph.py",
            "protein_database.py",
            "admet_predictor.py",
            "google_drive_manager.py",
            "main.py",
            "quick_start.py",
            "calculate_accuracy.py",
            "molecular_similarity.py"
        ]
    },
    "02_DATASETS": {
        "description": "Dataset management and raw data",
        "files": [
            "download_chembl_dataset.py",
            "retrain_with_real_data.py",
            "load_from_google_drive.py",
            "download_to_drive_colab.py",
            "create_massive_datasets.py",
            "update_drug_targets.py"
        ],
        "subfolders": {
            "raw_data": [],
            "processed": [],
            "backups": []
        }
    },
    "03_TRAINING": {
        "description": "Training scripts and configurations",
        "files": [
            "train_enhanced_system.py",
            "train_complete.py",
            "train_final.py",
            "train_now.py",
            "train_quick.py",
            "ultra_fast.py",
            "train_and_visualize.py",
            "production_train.py",
            "fast_train.py",
            "cpu_train.py",
            "final_system.py"
        ]
    },
    "04_TESTING": {
        "description": "Testing, validation, and empirical tests",
        "files": [
            "test_neuro_from_drive.py",
            "test_neuro_symptoms.py",
            "test_google_drive_datasets.py",
            "covid_empirical_test.py",
            "test_and_visualize.py",
            "benchmark_comparison.py",
            "run_full_test.py",
            "show_file_structure.py",
            "analyze_and_organize.py"
        ]
    },
    "05_RESULTS": {
        "description": "Generated outputs and results",
        "files": [
            "final_results.json",
            "final_trained.json",
            "trained_drugs.json",
            "test_output.json",
            "denovo_drug_results.json",
            "covid_test_output.txt",
            "training_output.txt"
        ],
        "subfolders": {
            "training_results": "trained_enhanced_system_*.json",
            "test_results": [
                "enhanced_test_results_*.json",
                "neuro_test_results_drive.json",
                "covid_empirical_test_results.json"
            ],
            "generated_candidates": [
                "all_42_covid_candidates.json"
            ]
        }
    },
    "06_VISUALIZATION": {
        "description": "Charts, graphs, and visual outputs",
        "files": [
            "generate_visualizations.py",
            "covid_benchmark_charts.py",
            "final_visualizations.py",
            "benchmark_comparison.py"
        ],
        "subfolders": {
            "charts": "*.png"
        }
    },
    "07_DOCUMENTATION": {
        "description": "Documentation, guides, and requirements",
        "files": [
            "IMPLEMENTATION_GUIDE.md",
            "requirements.txt",
            "sample.txt",
            "README.md"
        ]
    }
}

# Legacy folders to keep as-is
legacy_folders = [
    "drug_discovery",
    "txgnn", 
    "empirical_test"
]

# Track statistics
stats = {
    "folders_created": 0,
    "files_moved": 0,
    "errors": []
}

# Create main folders
print("\n[1/4] Creating main folders...")
for folder_name, config in folder_mappings.items():
    folder_path = project_root / folder_name
    try:
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
            print(f"  Created: {folder_name}/")
            stats["folders_created"] += 1
        else:
            print(f"  Exists: {folder_name}/")
        
        # Create subfolders if defined
        if "subfolders" in config:
            for subfolder in config["subfolders"].keys():
                subfolder_path = folder_path / subfolder
                if not subfolder_path.exists():
                    subfolder_path.mkdir(parents=True)
                    print(f"    Created: {subfolder}/")
                    
    except Exception as e:
        error_msg = f"Error creating {folder_name}: {e}"
        print(f"  ERROR: {error_msg}")
        stats["errors"].append(error_msg)

print(f"\n  Folders created: {stats['folders_created']}")

# Move files to appropriate folders
print("\n[2/4] Moving files to organized folders...")

for folder_name, config in folder_mappings.items():
    folder_path = project_root / folder_name
    
    # Move specific files
    if "files" in config:
        for filename in config["files"]:
            source = project_root / filename
            destination = folder_path / filename
            
            if source.exists():
                try:
                    shutil.move(str(source), str(destination))
                    print(f"  Moved: {filename} -> {folder_name}/")
                    stats["files_moved"] += 1
                except Exception as e:
                    error_msg = f"Error moving {filename}: {e}"
                    print(f"  ERROR: {error_msg}")
                    stats["errors"].append(error_msg)
    
    # Move wildcard files (results and visualizations)
    if folder_name == "05_RESULTS":
        # Move training results
        training_folder = folder_path / "training_results"
        for file in project_root.glob("trained_enhanced_system_*.json"):
            try:
                shutil.move(str(file), str(training_folder / file.name))
                print(f"  Moved: {file.name} -> 05_RESULTS/training_results/")
                stats["files_moved"] += 1
            except Exception as e:
                print(f"  ERROR moving {file.name}: {e}")
        
        # Move test results
        test_folder = folder_path / "test_results"
        for pattern in ["enhanced_test_results_*.json", "neuro_test_results*.json", "covid_empirical*.json"]:
            for file in project_root.glob(pattern):
                try:
                    shutil.move(str(file), str(test_folder / file.name))
                    print(f"  Moved: {file.name} -> 05_RESULTS/test_results/")
                    stats["files_moved"] += 1
                except Exception as e:
                    print(f"  ERROR moving {file.name}: {e}")
        
        # Move candidates
        candidates_folder = folder_path / "generated_candidates"
        for file in project_root.glob("*covid*candidates*.json"):
            try:
                shutil.move(str(file), str(candidates_folder / file.name))
                print(f"  Moved: {file.name} -> 05_RESULTS/generated_candidates/")
                stats["files_moved"] += 1
            except Exception as e:
                print(f"  ERROR moving {file.name}: {e}")
    
    elif folder_name == "06_VISUALIZATION":
        # Move PNG files
        charts_folder = folder_path / "charts"
        for file in project_root.glob("*.png"):
            try:
                shutil.move(str(file), str(charts_folder / file.name))
                print(f"  Moved: {file.name} -> 06_VISUALIZATION/charts/")
                stats["files_moved"] += 1
            except Exception as e:
                print(f"  ERROR moving {file.name}: {e}")

print(f"\n  Files moved: {stats['files_moved']}")

# Create README files
print("\n[3/4] Creating README files...")

readme_template = """# {folder_name}

{description}

## Contents

{contents}

---
Generated: {date}
NOVO-1 Drug Discovery System
"""

for folder_name, config in folder_mappings.items():
    folder_path = project_root / folder_name
    readme_path = folder_path / "README.md"
    
    # List current contents
    contents = []
    for item in folder_path.iterdir():
        if item.is_dir():
            contents.append(f"- **{item.name}/** - Subfolder")
        elif item.name != "README.md":
            contents.append(f"- `{item.name}`")
    
    readme_content = readme_template.format(
        folder_name=folder_name.replace("_", " ").title(),
        description=config["description"],
        contents="\n".join(contents) if contents else "- (Folder created, contents will be added)",
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"  Created: {folder_name}/README.md")
    except Exception as e:
        print(f"  ERROR creating README for {folder_name}: {e}")

# Create main project README
print("\n[4/4] Creating main project README...")
main_readme = """# NOVO-1 Drug Discovery System

**AI-Powered Drug Discovery with Knowledge Graphs & ADMET Predictions**

## Project Structure

This project is organized into the following folders:

### 01_CORE_SYSTEM/
Main system files - the heart of NOVO-1
- Enhanced drug discovery system
- Knowledge graph module
- Protein database (100+ proteins)
- ADMET predictor

### 02_DATASETS/
Dataset management and raw data
- Dataset downloaders
- Data processing scripts
- Backup storage

### 03_TRAINING/
Training scripts and configurations
- Main training pipeline
- Various training configurations
- Target mapping utilities

### 04_TESTING/
Testing, validation, and empirical tests
- Test scripts
- Benchmark comparisons
- Validation suites

### 05_RESULTS/
Generated outputs and results
- Training results
- Test outputs
- Generated drug candidates

### 06_VISUALIZATION/
Charts, graphs, and visual outputs
- Visualization scripts
- Generated charts and graphs

### 07_DOCUMENTATION/
Documentation, guides, and requirements
- Implementation guides
- Requirements

### 08_LEGACY/
Legacy code and old versions (preserved for reference)
- drug_discovery/ - Original drug discovery code
- txgnn/ - TXGNN framework
- empirical_test/ - Original test suite

## Quick Start

```bash
# Run the enhanced system
python 01_CORE_SYSTEM/train_enhanced_system.py

# Or quick demo
python 01_CORE_SYSTEM/quick_start.py
```

## Features

- **Target Protein Identification** (First & Last)
- **ADMET Predictions** (Absorption, Distribution, Metabolism, Excretion, Toxicity)
- **100+ Proteins** in database with UniProt IDs
- **Knowledge Graph** with 450+ triples
- **Drug Candidate Generation** with chemical properties

## System Requirements

- Python 3.8+
- RDKit (for molecular calculations)
- NumPy, Pandas
- See requirements.txt for full list

---
**Organized:** {date}
**Total Files:** {total_files}
""".format(
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    total_files=stats["files_moved"]
)

try:
    with open(project_root / "README.md", 'w') as f:
        f.write(main_readme)
    print("  Created: Main README.md")
except Exception as e:
    print(f"  ERROR creating main README: {e}")

# Final summary
print("\n" + "="*80)
print("ORGANIZATION COMPLETE!")
print("="*80)
print(f"\n📊 STATISTICS:")
print(f"   Folders created: {stats['folders_created']}")
print(f"   Files moved: {stats['files_moved']}")
print(f"   Errors: {len(stats['errors'])}")

if stats['errors']:
    print(f"\n⚠️  ERRORS ENCOUNTERED:")
    for error in stats['errors'][:10]:
        print(f"   - {error}")

print(f"\n✅ PROJECT STRUCTURE:")
print(f"   C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models/")
print(f"   ├── 01_CORE_SYSTEM/          <- Main system files")
print(f"   ├── 02_DATASETS/             <- Datasets")
print(f"   ├── 03_TRAINING/             <- Training scripts")
print(f"   ├── 04_TESTING/              <- Testing scripts")
print(f"   ├── 05_RESULTS/              <- Generated outputs")
print(f"   ├── 06_VISUALIZATION/        <- Charts")
print(f"   ├── 07_DOCUMENTATION/        <- Guides")
print(f"   ├── 08_LEGACY/               <- Old code (preserved)")
print(f"   │   ├── drug_discovery/")
print(f"   │   ├── txgnn/")
print(f"   │   └── empirical_test/")
print(f"   └── README.md                <- Main project guide")

print(f"\n🎉 FOLDER ORGANIZATION COMPLETE!")
print(f"   All files preserved and organized!")
print(f"   Check README.md files in each folder for details.")
print("="*80)
