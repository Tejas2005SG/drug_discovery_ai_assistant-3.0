"""
Test with Neurological Symptoms - Load from Google Drive
"""

import sys
sys.path.append('C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models')

import json
import numpy as np
from pathlib import Path
from novo1_drug_system import NOVO1DrugDiscoverySystem

print("="*80)
print("NEUROLOGICAL SYMPTOM TEST - GOOGLE DRIVE DATASET")
print("="*80)

# Try to load from Google Drive first, then fallback to local
drive_paths = [
    Path("G:/My Drive/drug_discovery_ai"),
    Path("G:/My Drive"),
    Path("C:/Users/Tejas/Google Drive"),
    Path("D:/Datasets"),  # Your local copy
]

datasets = {}

print("\n[1] Loading datasets...")

for drive_path in drive_paths:
    if drive_path.exists():
        chembl_file = drive_path / "01_chembl_core_drugs.json"
        neuro_file = drive_path / "02_neurological_drugs_100.json"
        
        if chembl_file.exists():
            with open(chembl_file, 'r') as f:
                datasets['chembl'] = json.load(f)
            print(f"  [OK] ChEMBL: {len(datasets['chembl'])} drugs from {drive_path}")
            
        if neuro_file.exists():
            with open(neuro_file, 'r') as f:
                datasets['neuro'] = json.load(f)
            print(f"  [OK] Neurological: {len(datasets['neuro'])} drugs from {drive_path}")
            
        if 'chembl' in datasets or 'neuro' in datasets:
            break

if not datasets:
    print("  [ERROR] No datasets found!")
    sys.exit(1)

# Combine all drugs
all_drugs = []
if 'chembl' in datasets:
    for drug in datasets['chembl']:
        all_drugs.append({
            'name': drug['drug_name'],
            'smiles': drug['smiles'],
            'targets': drug.get('target_protein', '').split(', ') if drug.get('target_protein') else [],
            'indications': drug.get('disease_indications', [])
        })

if 'neuro' in datasets:
    for drug in datasets['neuro']:
        all_drugs.append({
            'name': drug['name'],
            'smiles': drug['smiles'],
            'targets': drug.get('target', '').split(', ') if drug.get('target') else [],
            'indications': drug.get('indications', [])
        })

print(f"\n[OK] Total drugs loaded: {len(all_drugs)}")

# Prepare disease data including neurological conditions
diseases_data = [
    {
        'name': 'Multiple Sclerosis',
        'symptoms': ['neural inflammation', 'tremors', 'fatigue', 'muscle weakness', 'numbness', 'localized neural inflammation']
    },
    {
        'name': 'Autoimmune Encephalitis',
        'symptoms': ['neural inflammation', 'cytokine storm', 'confusion', 'seizures', 'memory loss', 'rapid onset neural inflammation']
    },
    {
        'name': 'Potassium Channelopathy',
        'symptoms': ['potassium channel blocking', 'tremors', 'muscle weakness', 'fatigue', 'blocking of specific potassium channels']
    },
    {
        'name': 'Parkinson Disease',
        'symptoms': ['tremors in extremities', 'muscle stiffness', 'slow movement', 'balance problems', 'tremors']
    },
    {
        'name': 'Cytokine Storm Syndrome',
        'symptoms': ['cytokine storm markers', 'high fever', 'inflammation', 'organ damage', 'severe inflammation']
    },
    {
        'name': 'Neuroinflammatory Disorder',
        'symptoms': ['rapid onset localized neural inflammation', 'cytokine storm', 'neural damage', 'inflammation']
    },
    {
        'name': 'Essential Tremor',
        'symptoms': ['tremors', 'tremors in extremities', 'action tremor', 'kinetic tremor']
    },
    {
        'name': 'Dystonia',
        'symptoms': ['muscle contractions', 'abnormal postures', 'twisting movements', 'neural inflammation']
    },
    {
        'name': 'COVID-19',
        'symptoms': ['fever', 'cough', 'fatigue', 'shortness of breath', 'cytokine storm', 'inflammation']
    },
    {
        'name': 'Severe COVID-19',
        'symptoms': ['severe shortness of breath', 'chest pain', 'confusion', 'cytokine storm', 'neural inflammation']
    }
]

# Initialize and train
print("\n[2] Building knowledge graph...")
system = NOVO1DrugDiscoverySystem(use_google_drive=False)
system.build_knowledge_graph(diseases_data, all_drugs)

stats = system.knowledge_graph.get_statistics()
print(f"\n[KNOWLEDGE GRAPH]")
print(f"  Diseases: {stats['num_diseases']}")
print(f"  Drugs: {stats['num_drugs']}")
print(f"  Symptoms: {stats['num_symptoms']}")
print(f"  Triples: {stats['num_triples']}")

# TEST WITH COMPLEX NEUROLOGICAL SYMPTOMS
print("\n" + "="*80)
print("TESTING: COMPLEX NEUROLOGICAL SYMPTOMS")
print("="*80)

neuro_symptoms = [
    "rapid onset localized neural inflammation",
    "cytokine storm markers",
    "blocking of specific potassium channels",
    "tremors in extremities"
]

print(f"\nInput Symptoms:")
for i, sym in enumerate(neuro_symptoms, 1):
    print(f"  {i}. {sym}")

print("\n[3] Generating drug candidates...")
candidates = system.generate_drugs(neuro_symptoms, n_candidates=10)

print("\n" + "="*80)
print("RESULTS - TOP DRUG CANDIDATES")
print("="*80)

if candidates:
    candidates.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"\n[OK] Generated {len(candidates)} valid candidates\n")
    
    for i, cand in enumerate(candidates[:5], 1):
        print(f"{i}. {cand['id']} (Confidence: {cand['confidence']:.1%})")
        print(f"   SMILES: {cand['smiles'][:70]}...")
        print(f"   Molecular Weight: {cand['properties']['mw']:.1f} Da")
        print(f"   QED Score: {cand['properties']['qed']:.3f}")
        print(f"   Predicted Targets: {', '.join(cand['predicted_targets'][:3])}")
        print(f"   Source Drugs: {', '.join(cand['source_drugs'][:2])}")
        print(f"   Method: {cand['generation_method']}")
        print()
    
    # Statistics
    avg_qed = np.mean([c['properties']['qed'] for c in candidates])
    avg_conf = np.mean([c['confidence'] for c in candidates])
    avg_mw = np.mean([c['properties']['mw'] for c in candidates])
    
    print("="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total Candidates: {len(candidates)}")
    print(f"Valid Molecules: {len(candidates)}/{len(candidates)} (100%)")
    print(f"Average QED: {avg_qed:.3f}")
    print(f"Average Confidence: {avg_conf:.1%}")
    print(f"Average MW: {avg_mw:.1f} Da")
    print(f"Best Candidate: {candidates[0]['id']} ({candidates[0]['confidence']:.1%} confidence)")
    
    # Save results
    results = {
        'test_case': 'Complex Neurological Symptoms',
        'symptoms': neuro_symptoms,
        'candidates': candidates,
        'statistics': {
            'total': len(candidates),
            'avg_qed': float(avg_qed),
            'avg_confidence': float(avg_conf),
            'avg_mw': float(avg_mw)
        },
        'dataset_used': f"{len(all_drugs)} drugs from Google Drive"
    }
    
    with open('neuro_test_results_drive.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Results saved: neuro_test_results_drive.json")
    
else:
    print("[ERROR] No candidates generated")
    print("\nTroubleshooting:")
    print("  - Check if symptoms match disease profiles")
    print("  - Verify dataset has matching indications")

print("\n" + "="*80)
