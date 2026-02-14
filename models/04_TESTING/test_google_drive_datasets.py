"""
Load datasets from Google Drive and test enhanced NOVO-1 system
Uses Google Drive as the primary dataset source
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from novo1_enhanced_system import EnhancedNOVO1System
from google_drive_manager import GoogleDriveManager

def load_datasets_from_google_drive(drive_manager):
    """Load datasets from Google Drive"""
    print("\n[LOADING DATASETS FROM GOOGLE DRIVE]")
    print("-"*70)
    
    all_drugs = []
    all_diseases = []
    
    # List of dataset files to load
    dataset_files = [
        "01_chembl_core_drugs.json",
        "02_neurological_drugs_100.json",
        "chembl_drug_dataset.json",
        "covid19_drug_dataset.json"
    ]
    
    for filename in dataset_files:
        try:
            print(f"\n  Loading: {filename}")
            data = drive_manager.load_dataset(filename)
            
            if data:
                if isinstance(data, dict) and 'drugs' in data:
                    all_drugs.extend(data['drugs'])
                    if 'metadata' in data and 'disease' in data['metadata']:
                        all_diseases.append({
                            'name': data['metadata']['disease'],
                            'symptoms': data['metadata'].get('symptoms', [])
                        })
                    print(f"    ✓ Loaded {len(data['drugs'])} drugs")
                elif isinstance(data, list):
                    all_drugs.extend(data)
                    print(f"    ✓ Loaded {len(data)} drugs")
            else:
                print(f"    ✗ File not found or empty")
                
        except Exception as e:
            print(f"    ✗ Error loading {filename}: {e}")
    
    print(f"\n[SUMMARY]")
    print(f"  Total drugs loaded: {len(all_drugs)}")
    print(f"  Total diseases: {len(all_diseases)}")
    
    return all_drugs, all_diseases

def prepare_training_data(drugs_data):
    """Prepare drug data for training"""
    formatted_drugs = []
    
    for drug in drugs_data:
        if 'smiles' not in drug or not drug['smiles']:
            continue
            
        # Handle different field names
        drug_name = drug.get('name', drug.get('drug_name', drug.get('compound_name', 'Unknown')))
        indications = drug.get('indications', drug.get('disease', ''))
        if isinstance(indications, str):
            indications = [indications]
        
        formatted_drug = {
            'name': drug_name,
            'smiles': drug['smiles'],
            'targets': drug.get('targets', []),
            'indications': indications
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
            if indication and indication not in disease_dict:
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
    """Main training function with Google Drive"""
    print("="*70)
    print("NOVO-1 ENHANCED SYSTEM - GOOGLE DRIVE DATASETS")
    print("Loading datasets from Google Drive and testing")
    print("="*70)
    
    # Initialize Google Drive manager
    print("\n[CONNECTING TO GOOGLE DRIVE]")
    # Use the drive folder ID from the URL you provided
    drive_folder_id = "1rsUlQu1PwHKEBQjHjkuXdAdJ1z6oeCPG"
    drive_manager = GoogleDriveManager(drive_path=None)
    
    # Load datasets from Google Drive
    drugs_data, diseases_data = load_datasets_from_google_drive(drive_manager)
    
    if not drugs_data:
        print("\n[ERROR] No datasets loaded from Google Drive!")
        print("Make sure files are accessible and not corrupted.")
        return
    
    # Prepare training data
    print("\n[PREPARING TRAINING DATA]")
    formatted_drugs = prepare_training_data(drugs_data)
    
    if not diseases_data:
        diseases_data = create_disease_data_from_drugs(formatted_drugs)
    
    print(f"  Drugs: {len(formatted_drugs)}")
    print(f"  Diseases: {len(diseases_data)}")
    
    # Check how many drugs have targets
    with_targets = sum(1 for d in formatted_drugs if d.get('targets'))
    print(f"  Drugs with protein targets: {with_targets}/{len(formatted_drugs)} ({with_targets/len(formatted_drugs)*100:.1f}%)")
    
    # Initialize enhanced system
    print("\n[INITIALIZING ENHANCED NOVO-1 SYSTEM]")
    system = EnhancedNOVO1System(use_google_drive=False)
    
    # Build and train knowledge graph
    print("\n[TRAINING KNOWLEDGE GRAPH]")
    system.build_knowledge_graph(diseases_data, formatted_drugs)
    
    # Save training info
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test the system
    print("\n" + "="*70)
    print("TESTING ENHANCED SYSTEM WITH GOOGLE DRIVE DATA")
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
    results_file = f"google_drive_test_results_{timestamp}.json"
    
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
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n[OK] Test results saved to {results_file}")
    
    # Summary
    print("\n" + "="*70)
    print("✅ GOOGLE DRIVE TEST COMPLETE!")
    print("="*70)
    print(f"\n📊 STATISTICS:")
    print(f"   • Total drugs from Google Drive: {len(formatted_drugs)}")
    print(f"   • Drugs with targets: {with_targets}")
    print(f"   • Coverage: {with_targets/len(formatted_drugs)*100:.1f}%")
    print(f"   • Candidates generated: {len(results['candidates'])}")
    print(f"   • Average confidence: {sum(c['confidence_score'] for c in results['candidates'])/len(results['candidates'])*100:.1f}%")
    
    print(f"\n📁 FILES CREATED:")
    print(f"   • {results_file}")
    print(f"   • trained_enhanced_system_{timestamp}.json")
    
    print("\n🎯 TARGET PROTEINS IDENTIFIED:")
    for protein in results['target_proteins'][:5]:
        info = protein['info']
        print(f"   • {protein['protein_name']} [{info.get('uniprot_id', 'N/A')}]")
        print(f"     Family: {info.get('protein_family', 'Unknown')}")
        print(f"     Druggability: {info.get('druggability', 'Unknown')}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
