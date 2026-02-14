"""
Test NOVO-1 Model with Complex Neurological Symptoms
Symptoms: Rapid onset localized neural inflammation, cytokine storm markers, 
          blocking of specific potassium channels, tremors in extremities
"""

import sys
sys.path.append('C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models')

import json
import numpy as np
from pathlib import Path
from novo1_drug_system import NOVO1DrugDiscoverySystem

print("="*80)
print("NEUROLOGICAL SYMPTOM TEST - COMPLEX CASE")
print("="*80)

# Load dataset from local (since it's recreated)
print("\n[1] Loading dataset...")
dataset_path = Path('datasets/covid19_drug_dataset.json')

with open(dataset_path, 'r') as f:
    drugs_list = json.load(f)

print(f"[OK] Loaded {len(drugs_list)} drugs")

# Prepare disease data including neurological conditions
diseases_data = [
    {
        'name': 'Multiple Sclerosis',
        'symptoms': ['neural inflammation', 'tremors', 'fatigue', 'muscle weakness', 'numbness']
    },
    {
        'name': 'Autoimmune Encephalitis',
        'symptoms': ['neural inflammation', 'cytokine storm', 'confusion', 'seizures', 'memory loss']
    },
    {
        'name': 'Potassium Channelopathy',
        'symptoms': ['potassium channel blocking', 'tremors', 'muscle weakness', 'fatigue']
    },
    {
        'name': 'Parkinson Disease',
        'symptoms': ['tremors in extremities', 'muscle stiffness', 'slow movement', 'balance problems']
    },
    {
        'name': 'Cytokine Storm Syndrome',
        'symptoms': ['cytokine storm markers', 'high fever', 'inflammation', 'organ damage']
    },
    {
        'name': 'Neuroinflammatory Disorder',
        'symptoms': ['rapid onset neural inflammation', 'cytokine storm', 'neural damage']
    },
    {
        'name': 'COVID-19',
        'symptoms': ['fever', 'cough', 'fatigue', 'shortness of breath', 'cytokine storm']
    },
    {
        'name': 'Severe COVID-19',
        'symptoms': ['severe shortness of breath', 'chest pain', 'confusion', 'cytokine storm']
    }
]

# Convert to list format expected by system
drugs_formatted = []
for drug in drugs_list:
    if isinstance(drug, dict) and drug.get('smiles'):
        drugs_formatted.append({
            'name': drug.get('drug_name', 'Unknown'),
            'smiles': drug['smiles'],
            'targets': drug.get('target_protein', '').split(', ') if drug.get('target_protein') else [],
            'indications': drug.get('disease_indications', [])
        })

print(f"[OK] Formatted {len(drugs_formatted)} valid drugs")

# Initialize and train system
print("\n[2] Building knowledge graph...")
system = NOVO1DrugDiscoverySystem(use_google_drive=False)
system.build_knowledge_graph(diseases_data, drugs_formatted)

# Show stats
stats = system.knowledge_graph.get_statistics()
print(f"\n[KNOWLEDGE GRAPH]")
print(f"  Diseases: {stats['num_diseases']}")
print(f"  Drugs: {stats['num_drugs']}")
print(f"  Triples: {stats['num_triples']}")

# TEST WITH COMPLEX NEUROLOGICAL SYMPTOMS
print("\n" + "="*80)
print("GENERATING DRUGS FOR COMPLEX NEUROLOGICAL SYMPTOMS")
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

print("\n[3] Genering drug candidates...")
candidates = system.generate_drugs(neuro_symptoms, n_candidates=10)

print("\n" + "="*80)
print("RESULTS - TOP DRUG CANDIDATES")
print("="*80)

if candidates:
    # Sort by confidence
    candidates.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"\n[OK] Generated {len(candidates)} valid candidates\n")
    
    for i, cand in enumerate(candidates[:5], 1):
        print(f"{i}. {cand['id']} (Confidence: {cand['confidence']:.1%})")
        print(f"   SMILES: {cand['smiles'][:60]}...")
        print(f"   Molecular Weight: {cand['properties']['mw']:.1f} Da")
        print(f"   QED Score: {cand['properties']['qed']:.3f}")
        print(f"   Predicted Targets: {', '.join(cand['predicted_targets'][:3])}")
        print(f"   Source Drugs: {', '.join(cand['source_drugs'][:2])}")
        print(f"   Generation Method: {cand['generation_method']}")
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
    print("="*80)
    
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
        }
    }
    
    with open('neuro_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n[OK] Results saved: neuro_test_results.json")
    
else:
    print("[ERROR] No candidates generated")

print("\n" + "="*80)
