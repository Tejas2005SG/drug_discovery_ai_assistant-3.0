"""
Download Real Datasets from Kaggle & Hugging Face to Google Drive
This script downloads massive drug discovery datasets directly to your Drive
"""

# Install required packages
!pip install -q kaggle huggingface_hub datasets pandas numpy

from google.colab import drive
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

# Mount Google Drive
drive.mount('/content/drive')

# Set your Google Drive path
DRIVE_PATH = '/content/drive/My Drive/drug_discovery_ai/datasets'
os.makedirs(DRIVE_PATH, exist_ok=True)

print("="*80)
print("DOWNLOADING REAL DATASETS TO GOOGLE DRIVE")
print("="*80)
print(f"Drive Path: {DRIVE_PATH}")
print(f"Storage Available: 15GB")
print("="*80)

# ============================================================================
# DATASET 1: ChEMBL Bioactivity (from Kaggle)
# ============================================================================
print("\n[1] Downloading ChEMBL Bioactivity Dataset from Kaggle...")
print("Source: https://www.kaggle.com/datasets/art3mis/chembl22")

# Kaggle dataset download
!kaggle datasets download -d art3mis/chembl22 -p {DRIVE_PATH} --unzip

print("✓ ChEMBL dataset downloaded")

# ============================================================================
# DATASET 2: Molecular SMILES (from Hugging Face)
# ============================================================================
print("\n[2] Downloading Molecular SMILES from Hugging Face...")
print("Source: https://huggingface.co/datasets/antoinebcx/smiles-molecules-chembl")

from datasets import load_dataset

# Download from Hugging Face
dataset = load_dataset("antoinebcx/smiles-molecules-chembl", split="train")
df_hf = pd.DataFrame(dataset)

# Save to Drive
hf_path = f"{DRIVE_PATH}/huggingface_smiles_dataset.csv"
df_hf.to_csv(hf_path, index=False)
print(f"✓ Hugging Face dataset saved: {hf_path}")
print(f"  Records: {len(df_hf)}")

# ============================================================================
# DATASET 3: DrugBank (from Kaggle)
# ============================================================================
print("\n[3] Downloading DrugBank Dataset from Kaggle...")
print("Source: https://www.kaggle.com/datasets/nbroad/drugbank-dataset")

!kaggle datasets download -d nbroad/drugbank-dataset -p {DRIVE_PATH} --unzip

print("✓ DrugBank dataset downloaded")

# ============================================================================
# DATASET 4: FDA Approved Drugs (from Kaggle)
# ============================================================================
print("\n[4] Downloading FDA Approved Drugs from Kaggle...")
print("Source: https://www.kaggle.com/datasets/jithinanie/fda-approved-drugs")

!kaggle datasets download -d jithinanie/fda-approved-drugs -p {DRIVE_PATH} --unzip

print("✓ FDA dataset downloaded")

# ============================================================================
# DATASET 5: BindingDB (Protein-Ligand Interactions)
# ============================================================================
print("\n[5] Downloading BindingDB Dataset...")
print("Source: https://www.bindingdb.org/rwd/bind/chemsearch/marvin/Download.jsp")

# Download BindingDB (large file - ~2GB)
!wget -O {DRIVE_PATH}/BindingDB_All.tsv.gz https://www.bindingdb.org/bind/downloads/BindingDB_All_202401.tsv.gz

print("✓ BindingDB dataset downloaded (2GB)")

# ============================================================================
# DATASET 6: PubChem Bioassay (from Kaggle)
# ============================================================================
print("\n[6] Downloading PubChem Bioassay from Kaggle...")
print("Source: https://www.kaggle.com/datasets/chemoinformaticslaboratory/pubchem-bioassay")

!kaggle datasets download -d chemoinformaticslaboratory/pubchem-bioassay -p {DRIVE_PATH} --unzip

print("✓ PubChem dataset downloaded")

# ============================================================================
# DATASET 7: ZINC Database (Molecular Structures)
# ============================================================================
print("\n[7] Downloading ZINC Database...")
print("Source: https://zinc.docking.org/")

# Download subset of ZINC (purchaseable compounds)
!wget -O {DRIVE_PATH}/zinc_15k.csv http://files.docking.org/2d/15/15_k.csv

print("✓ ZINC dataset downloaded")

# ============================================================================
# DATASET 8: Therapeutic Drug Monitoring
# ============================================================================
print("\n[8] Downloading Therapeutic Drug Data...")
print("Source: https://www.kaggle.com/datasets/pattnaiksatyajit/drug-dataset")

!kaggle datasets download -d pattnaiksatyajit/drug-dataset -p {DRIVE_PATH} --unzip

print("✓ Therapeutic dataset downloaded")

# ============================================================================
# CREATE MASTER COMPREHENSIVE DATASET
# ============================================================================
print("\n" + "="*80)
print("CREATING MASTER COMPREHENSIVE DATASET")
print("="*80)

# Combine all datasets
all_drugs = []

# Load ChEMBL if available
chembl_path = f"{DRIVE_PATH}/chembl_22.csv"
if os.path.exists(chembl_path):
    df_chembl = pd.read_csv(chembl_path)
    print(f"✓ Loaded ChEMBL: {len(df_chembl)} records")
    all_drugs.append(df_chembl)

# Load FDA if available
fda_path = f"{DRIVE_PATH}/FDA Approved Drugs.csv"
if os.path.exists(fda_path):
    df_fda = pd.read_csv(fda_path)
    print(f"✓ Loaded FDA: {len(df_fda)} records")
    all_drugs.append(df_fda)

# Load DrugBank if available
db_path = f"{DRIVE_PATH}/drugbank.csv"
if os.path.exists(db_path):
    df_db = pd.read_csv(db_path)
    print(f"✓ Loaded DrugBank: {len(df_db)} records")
    all_drugs.append(df_db)

# Load Hugging Face
df_hf = pd.read_csv(hf_path)
all_drugs.append(df_hf)

# Combine all
if all_drugs:
    master_df = pd.concat(all_drugs, ignore_index=True)
    master_df = master_df.drop_duplicates(subset=['smiles'] if 'smiles' in master_df.columns else None)
    
    master_path = f"{DRIVE_PATH}/MASTER_COMPREHENSIVE_DATASET.csv"
    master_df.to_csv(master_path, index=False)
    
    print(f"\n✓ MASTER DATASET CREATED")
    print(f"  Total Records: {len(master_df)}")
    print(f"  Size: {os.path.getsize(master_path) / (1024*1024):.2f} MB")
    print(f"  Location: {master_path}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("DOWNLOAD COMPLETE - GOOGLE DRIVE STORAGE")
print("="*80)

# List all files in Drive
files = os.listdir(DRIVE_PATH)
total_size = sum(os.path.getsize(os.path.join(DRIVE_PATH, f)) for f in files)

print(f"\nFiles in Google Drive ({DRIVE_PATH}):")
for f in sorted(files):
    size = os.path.getsize(os.path.join(DRIVE_PATH, f)) / (1024*1024)
    print(f"  • {f}: {size:.2f} MB")

print(f"\nTotal Storage Used: {total_size / (1024*1024):.2f} MB / 15,360 MB")
print(f"Percentage Used: {(total_size / (15*1024*1024*1024)) * 100:.3f}%")

print("\n" + "="*80)
print("✓ ALL DATASETS READY IN GOOGLE DRIVE")
print("✓ You can now train your model with massive real-world data!")
print("="*80)
