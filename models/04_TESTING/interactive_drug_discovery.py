"""
Interactive NOVO-1 Drug Discovery System
Run from terminal: python interactive_drug_discovery.py
Enter symptoms dynamically and see the model's thinking process
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add paths for imports
# The system files are now in 01_CORE_SYSTEM folder
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "01_CORE_SYSTEM"))

from novo1_enhanced_system import EnhancedNOVO1System

def load_datasets():
    """Load datasets from D:/Datasets/"""
    print("\n" + "="*80)
    print("LOADING DATASETS")
    print("="*80)
    
    dataset_path = Path("D:/Datasets")
    
    if not dataset_path.exists():
        print("[ERROR] D:/Datasets/ not found!")
        print("Please ensure datasets are in D:\\Datasets\\")
        return None, None
    
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
            'targets': drug.get('targets', []),
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
        'General Pain': ['pain', 'inflammation', 'discomfort'],
        'Cardiovascular Issues': ['fluttering heartbeat', 'irregular heartbeat', 'chest pain'],
        'Neurological Symptoms': ['confusion', 'sudden confusion', 'disorientation', 'brain fog'],
        'Sensory Issues': ['ear blockage', 'hearing problems', 'vision problems'],
        'Musculoskeletal': ['cracking knuckles', 'joint pain', 'brittle nails', 'bone pain'],
    }
    
    for disease_name, symptoms in symptom_map.items():
        if disease_name in disease_dict:
            disease_dict[disease_name]['symptoms'] = symptoms
    
    return list(disease_dict.values())


def get_symptoms_from_user():
    """Interactive symptom input from user"""
    print("\n" + "="*80)
    print("SYMPTOM INPUT")
    print("="*80)
    print("\nEnter patient symptoms:")
    print("Option 1: Type all symptoms separated by commas (e.g., fever, cough, headache)")
    print("Option 2: Enter one symptom per line, then press Enter twice when done")
    print("-"*80)
    
    symptoms = []
    
    # First, try to get all symptoms in one line (comma-separated)
    first_input = input("  Enter symptoms: ").strip()
    
    if ',' in first_input:
        # Split by comma and clean up
        symptoms = [s.strip() for s in first_input.split(',') if s.strip()]
        print(f"\n  [INFO] Detected {len(symptoms)} comma-separated symptoms")
    elif first_input:
        # Single symptom entered, continue with multi-line mode
        symptoms.append(first_input)
        
        # Continue getting more symptoms one per line
        symptom_count = 2
        print("\n  Enter additional symptoms (one per line), or press Enter to finish:")
        
        while True:
            symptom = input(f"  Symptom #{symptom_count}: ").strip()
            
            if symptom == '':
                break
            
            if symptom.lower() == 'done':
                break
            
            if symptom:
                symptoms.append(symptom)
                symptom_count += 1
    
    if len(symptoms) == 0:
        print("  [ERROR] No symptoms entered!")
        return get_symptoms_from_user()  # Recursive retry
    
    return symptoms


def display_thinking_header(step, title):
    """Display thinking process header"""
    print("\n" + "#"*80)
    print(f"STEP {step}: {title}")
    print("#"*80)


def display_thinking_subheader(title):
    """Display sub-header for thinking process"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def display_progress(message):
    """Display progress message"""
    print(f"\n  >> {message}")


def save_interactive_results(results, symptoms):
    """Save results from interactive session"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"interactive_results_{timestamp}.json"
    
    # Convert to serializable format
    serializable_results = {
        'input_symptoms': symptoms,
        'timestamp': timestamp,
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
    
    return results_file


def main():
    """Main interactive function"""
    print("\n" + "="*80)
    print("NOVO-1 DRUG DISCOVERY SYSTEM - INTERACTIVE MODE")
    print("Target Proteins + ADMET + All Chemical Properties")
    print("="*80)
    print("\nThis interactive tool will:")
    print("  1. Load your datasets")
    print("  2. Let you enter symptoms")
    print("  3. Show the model's thinking process")
    print("  4. Generate drug candidates")
    print("  5. Display detailed ADMET predictions")
    
    # Load datasets
    display_thinking_header("0", "INITIALIZATION & DATA LOADING")
    
    drugs_data, diseases_data = load_datasets()
    
    if not drugs_data:
        print("\n[ERROR] No datasets found. Exiting.")
        return
    
    # Prepare training data
    display_progress("Preparing training data...")
    formatted_drugs = prepare_training_data(drugs_data)
    
    if not diseases_data:
        diseases_data = create_disease_data_from_drugs(formatted_drugs)
    
    print(f"\n  • Drugs: {len(formatted_drugs)}")
    print(f"  • Diseases: {len(diseases_data)}")
    with_targets = sum(1 for d in formatted_drugs if d.get('targets'))
    print(f"  • Drugs with protein targets: {with_targets}/{len(formatted_drugs)} ({with_targets/len(formatted_drugs)*100:.1f}%)")
    
    # Initialize enhanced system
    display_thinking_header("1", "SYSTEM INITIALIZATION")
    display_progress("Initializing NOVO-1 Enhanced System v3.0...")
    system = EnhancedNOVO1System(use_google_drive=False)
    
    # Build and train knowledge graph
    display_thinking_subheader("TRAINING KNOWLEDGE GRAPH")
    system.build_knowledge_graph(diseases_data, formatted_drugs)
    
    # Interactive loop
    while True:
        # Get symptoms from user
        symptoms = get_symptoms_from_user()
        
        if not symptoms:
            print("\nNo symptoms entered. Exiting.")
            break
        
        print(f"\n[CONFIRMATION] You entered {len(symptoms)} symptoms:")
        for i, symptom in enumerate(symptoms, 1):
            print(f"  {i}. {symptom}")
        
        confirm = input("\nProceed with drug discovery? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled. Enter new symptoms...")
            continue
        
        # Run drug discovery
        display_thinking_header("2", "DRUG DISCOVERY WORKFLOW")
        display_thinking_subheader("Starting Complete Drug Discovery Process")
        
        try:
            results = system.generate_drugs(symptoms, n_candidates=5)
            
            # Display results
            display_thinking_subheader("DISPLAYING GENERATED DRUG CANDIDATES")
            system.display_candidates(results, top_n=3)
            
            # Save results
            results_file = save_interactive_results(results, symptoms)
            print(f"\n[OK] Results saved to: {results_file}")
            
        except Exception as e:
            print(f"\n[ERROR] Failed to generate drugs: {e}")
            import traceback
            traceback.print_exc()
        
        # Ask to continue
        print("\n" + "="*80)
        again = input("\nRun another discovery session? (y/n): ").strip().lower()
        if again != 'y':
            print("\nThank you for using NOVO-1 Drug Discovery System!")
            print("="*80)
            break
    
    print("\nGoodbye! 👋")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
