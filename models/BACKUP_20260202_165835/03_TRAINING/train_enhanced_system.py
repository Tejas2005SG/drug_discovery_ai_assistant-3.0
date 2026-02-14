"""
Enhanced NOVO-1 System Training with Real Datasets
Loads datasets from D:/Datasets/ and trains the enhanced system
with target proteins, ADMET predictions, and all chemical properties
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from novo1_enhanced_system import EnhancedNOVO1System

def load_datasets_from_drive():
    """Load datasets from D:/Datasets/"""
    dataset_path = Path("D:/Datasets")
    
    if not dataset_path.exists():
        print("[ERROR] D:/Datasets/ not found!")
        return None, None
    
    # Load all dataset files
    all_drugs = []
    all_diseases = []
    
    dataset_files = list(dataset_path.glob("*.json"))
    
    for file_path in dataset_files:
        if file_path.name == "DATASET_SUMMARY.json":
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, dict) and 'drugs' in data:
                all_drugs.extend(data['drugs'])
                if 'metadata' in data and 'disease' in data['metadata']:
                    all_diseases.append({
                        'name': data['metadata']['disease'],
                        'symptoms': data['metadata'].get('symptoms', [])
                    })
            elif isinstance(data, list):
                all_drugs.extend(data)
                
            print(f"[OK] Loaded {file_path.name}")
            
        except Exception as e:
            print(f"[WARNING] Failed to load {file_path.name}: {e}")
    
    print(f"\n[SUMMARY] Loaded {len(all_drugs)} drugs and {len(all_diseases)} diseases")
    
    return all_drugs, all_diseases


def prepare_training_data(drugs_data):
    """Prepare drug data for training"""
    formatted_drugs = []
    
    for drug in drugs_data:
        if 'smiles' not in drug or not drug['smiles']:
            continue
            
        formatted_drug = {
            'name': drug.get('name', drug.get('drug_name', 'Unknown')),
            'smiles': drug['smiles'],
            'targets': drug.get('targets', drug.get('mechanism_of_action', '').split(',') if drug.get('mechanism_of_action') else ['Unknown']),
            'indications': drug.get('indications', drug.get('disease', '')).split(',') if isinstance(drug.get('indications', ''), str) else drug.get('indications', ['Unknown'])
        }
        
        formatted_drugs.append(formatted_drug)
    
    return formatted_drugs


def create_disease_data_from_drugs(drugs_data):
    """Create disease data from drug indications"""
    disease_dict = {}
    
    for drug in drugs_data:
        indications = drug.get('indications', [])
        if isinstance(indications, str):
            indications = [indications]
        
        for indication in indications:
            if indication not in disease_dict:
                disease_dict[indication] = {
                    'name': indication,
                    'symptoms': []
                }
    
    # Add typical symptoms for common diseases
    symptom_map = {
        'COVID-19': ['fever', 'cough', 'fatigue', 'shortness of breath'],
        'Multiple Sclerosis': ['neural inflammation', 'tremors', 'fatigue', 'muscle weakness'],
        'Alzheimer Disease': ['memory loss', 'cognitive decline', 'neural inflammation'],
        'Parkinson Disease': ['tremors', 'motor impairment', 'neural inflammation'],
        'Epilepsy': ['seizures', 'neural inflammation', 'electrical disturbance'],
        'Migraine': ['headache', 'pain', 'neural inflammation'],
        'Rheumatoid Arthritis': ['joint pain', 'inflammation', 'stiffness'],
    }
    
    for disease_name, symptoms in symptom_map.items():
        if disease_name in disease_dict:
            disease_dict[disease_name]['symptoms'] = symptoms
    
    return list(disease_dict.values())


def main():
    """Main training function"""
    print("="*70)
    print("NOVO-1 ENHANCED SYSTEM - TRAINING WITH REAL DATASETS")
    print("Target Proteins + ADMET + All Chemical Properties")
    print("="*70)
    
    # Load datasets
    drugs_data, diseases_data = load_datasets_from_drive()
    
    if not drugs_data:
        print("\n[ERROR] No datasets found. Please create datasets first.")
        return
    
    # Prepare training data
    print("\n[PREPARING TRAINING DATA]")
    formatted_drugs = prepare_training_data(drugs_data)
    
    if not diseases_data:
        diseases_data = create_disease_data_from_drugs(formatted_drugs)
    
    print(f"  Drugs: {len(formatted_drugs)}")
    print(f"  Diseases: {len(diseases_data)}")
    
    # Initialize enhanced system
    print("\n[INITIALIZING ENHANCED NOVO-1 SYSTEM]")
    system = EnhancedNOVO1System(use_google_drive=False)
    
    # Build and train knowledge graph
    print("\n[TRAINING KNOWLEDGE GRAPH]")
    system.build_knowledge_graph(diseases_data, formatted_drugs)
    
    # Save the trained model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"trained_enhanced_system_{timestamp}.json"
    
    results = {
        'timestamp': timestamp,
        'system_version': '3.0',
        'features': [
            'Target Protein Identification (First & Last)',
            'Comprehensive ADMET Predictions',
            'All Chemical Properties',
            'Protein Database with UniProt IDs',
            'Enhanced Drug-likeness Scoring'
        ],
        'training_data': {
            'num_drugs': len(formatted_drugs),
            'num_diseases': len(diseases_data),
            'drug_examples': [d['name'] for d in formatted_drugs[:5]]
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Training complete! Model saved to {output_file}")
    
    # Test the system
    print("\n" + "="*70)
    print("TESTING ENHANCED SYSTEM")
    print("="*70)
    
    # Test with complex neurological symptoms
    test_symptoms = [
        'rapid onset localized neural inflammation',
        'tremors in extremities',
        'cytokine storm markers'
    ]
    
    print(f"\nTest Symptoms: {test_symptoms}")
    print("\nRunning drug discovery workflow...")
    
    results = system.generate_drugs(test_symptoms, n_candidates=5)
    system.display_candidates(results, top_n=3)
    
    # Save results
    results_file = f"enhanced_test_results_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        # Convert to serializable format
        serializable_results = {
            'symptoms': test_symptoms,
            'num_candidates': len(results['candidates']),
            'target_proteins': [
                {
                    'name': p['protein_name'],
                    'uniprot_id': p['info'].get('uniprot_id', 'N/A'),
                    'druggability': p['info'].get('druggability', 'Unknown')
                }
                for p in results['target_proteins']
            ],
            'candidates': [
                {
                    'id': c['id'],
                    'smiles': c['smiles'],
                    'formula': c['molecular_formula'],
                    'confidence': c['confidence_score'],
                    'qed': c['drug_likeness'],
                    'admet_score': c['admet_properties']['overall']['admet_composite_score'],
                    'targets': c['target_proteins']
                }
                for c in results['candidates']
            ]
        }
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n[OK] Test results saved to {results_file}")
    print("\n" + "="*70)
    print("ENHANCED SYSTEM READY FOR USE!")
    print("Features:")
    print("  * Target Proteins (First & Last)")
    print("  * ADMET Predictions (Absorption, Distribution, Metabolism, Excretion, Toxicity)")
    print("  * All Chemical Properties (Molecular Weight, LogP, TPSA, HBD/HBA, etc.)")
    print("  * Protein Database (UniProt IDs, Functions, Pathways)")
    print("  * Enhanced Drug-likeness Scoring")
    print("="*70)


if __name__ == "__main__":
    main()
