"""
Quick Drug Discovery Runner - Hardcoded Symptoms
Edit this file to change symptoms, then run: python run_discovery.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "01_CORE_SYSTEM"))

from novo1_enhanced_system import EnhancedNOVO1System

# ============================================
# EDIT THESE SYMPTOMS HERE
# ============================================
SYMPTOMS = [
    'brittle toenails',
    'cracking knuckles', 
    'ear blockage',
    'fluttering heartbeat',
    'sudden confusion'
]
# ============================================

print("="*80)
print("NOVO-1 DRUG DISCOVERY - QUICK RUN")
print("="*80)
print(f"\nSymptoms: {', '.join(SYMPTOMS)}")
print("-"*80)

# Load datasets
def load_datasets():
    dataset_path = Path("D:/Datasets")
    all_drugs = []
    all_diseases = []
    
    # Try to load enhanced dataset first
    enhanced_file = dataset_path / "03_complete_drug_dataset_enhanced.json"
    if enhanced_file.exists():
        try:
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'drugs' in data:
                all_drugs.extend(data['drugs'])
                print(f"[OK] Loaded enhanced dataset with {len(data['drugs'])} drugs")
        except Exception as e:
            print(f"[WARNING] Could not load enhanced dataset: {e}")
    
    # Also load other datasets if enhanced not available
    if not all_drugs:
        for file_path in dataset_path.glob("*.json"):
            if file_path.name in ["DATASET_SUMMARY.json", "03_complete_drug_dataset_enhanced.json"]:
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict) and 'drugs' in data:
                    all_drugs.extend(data['drugs'])
                elif isinstance(data, list):
                    all_drugs.extend(data)
            except:
                pass
    
    return all_drugs, all_diseases

def prepare_training_data(drugs_data):
    formatted_drugs = []
    for drug in drugs_data:
        if 'smiles' not in drug or not drug['smiles']:
            continue
        if 'PROTEIN_' in drug['smiles'] or len(drug['smiles']) < 5:
            continue
        formatted_drugs.append({
            'name': drug.get('name', 'Unknown'),
            'smiles': drug['smiles'],
            'targets': drug.get('targets', []),
            'indications': drug.get('indications', ['Unknown'])
        })
    return formatted_drugs

# Load and prepare
drugs_data, _ = load_datasets()
formatted_drugs = prepare_training_data(drugs_data)

print(f"Loaded {len(formatted_drugs)} drugs")

# Initialize and train
system = EnhancedNOVO1System(use_google_drive=False)
system.build_knowledge_graph([], formatted_drugs)

# Run discovery
results = system.generate_drugs(SYMPTOMS, n_candidates=5)

# Display results
system.display_candidates(results, top_n=5)

# Save results - COMPACT VERSION (without huge fingerprint arrays)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = f"discovery_results_{timestamp}.json"

# Create compact output without the massive fingerprint data
compact_candidates = []
for c in results.get('candidates', []):
    compact_candidates.append({
        'id': c['id'],
        'smiles': c['smiles'],
        'molecular_formula': c['molecular_formula'],
        'molecular_weight': c['all_properties']['molecular_weight'],
        'qed': c['drug_likeness'],
        'confidence_score': c['confidence_score'],
        'target_proteins': c['target_proteins'],
        'source_drugs': c['source_drugs'],
        'admet_summary': {
            'oral_bioavailability': c['admet_properties']['absorption']['oral_bioavailability_pct'],
            'bbb_penetration': c['admet_properties']['distribution']['blood_brain_barrier_logbb'],
            'toxicity_risk': c['admet_properties']['toxicity']['overall_toxicity_risk'],
            'drug_likeness_score': c['admet_properties']['overall']['drug_likeness_score']
        },
        'passes_lipinski': c['passes_lipinski']
    })

output = {
    'symptoms': SYMPTOMS,
    'num_candidates': len(compact_candidates),
    'timestamp': timestamp,
    'candidates': compact_candidates
}

with open(results_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n[OK] Results saved to: {results_file}")
print(f"[INFO] File size reduced by excluding 2048-bit fingerprint arrays")
print("="*80)
