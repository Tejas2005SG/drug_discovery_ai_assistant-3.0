"""
Interactive NOVO-1 Drug Discovery System - WITH UNIVERSAL SYMPTOM HANDLING
Run from terminal: python interactive_universal.py
Handles ANY symptoms, even if not in the disease database
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add paths for imports
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
        
        # Skip drugs with placeholder SMILES
        if 'PROTEIN_' in drug['smiles'] or len(drug['smiles']) < 5:
            continue
            
        formatted_drug = {
            'name': drug.get('name', drug.get('drug_name', 'Unknown')),
            'smiles': drug['smiles'],
            'targets': drug.get('targets', []),
            'indications': drug.get('indications', drug.get('disease', '')).split(',') if isinstance(drug.get('indications', ''), str) else drug.get('indications', ['Unknown'])
        }
        
        formatted_drugs.append(formatted_drug)
    
    return formatted_drugs


def create_enhanced_disease_data(drugs_data, user_symptoms):
    """
    Create disease data with ENHANCED matching for ANY symptoms
    This creates virtual disease mappings for unknown symptoms
    """
    disease_dict = {}
    
    # First, add all real diseases from drugs
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
    
    # ENHANCED: Add comprehensive symptom mappings
    enhanced_symptom_map = {
        # Neurological
        'Multiple Sclerosis': ['neural inflammation', 'tremors', 'fatigue', 'muscle weakness', 'numbness'],
        'Alzheimer Disease': ['memory loss', 'cognitive decline', 'neural inflammation', 'confusion', 'disorientation'],
        'Parkinson Disease': ['tremors', 'motor impairment', 'neural inflammation', 'rigidity'],
        'Epilepsy': ['seizures', 'neural inflammation', 'electrical disturbance', 'convulsions'],
        'Migraine': ['headache', 'pain', 'neural inflammation', 'sensitivity to light'],
        
        # Infectious
        'COVID-19': ['fever', 'cough', 'fatigue', 'shortness of breath', 'loss of taste'],
        
        # Autoimmune/Inflammation
        'Rheumatoid Arthritis': ['joint pain', 'inflammation', 'stiffness', 'swelling'],
        'Lupus': ['fatigue', 'joint pain', 'rash', 'fever'],
        
        # Cardiovascular
        'Hypertension': ['high blood pressure', 'fluttering heartbeat', 'chest pain', 'dizziness'],
        'Arrhythmia': ['irregular heartbeat', 'fluttering heartbeat', 'palpitations', 'dizziness'],
        'Heart Failure': ['shortness of breath', 'fatigue', 'swelling', 'irregular heartbeat'],
        
        # Sensory
        'Hearing Loss': ['ear blockage', 'hearing problems', 'tinnitus', 'ear pain'],
        'Vision Problems': ['blurred vision', 'vision loss', 'eye pain', 'sensitivity to light'],
        
        # Musculoskeletal
        'Osteoarthritis': ['joint pain', 'stiffness', 'cracking knuckles', 'bone pain'],
        'Osteoporosis': ['brittle nails', 'bone pain', 'fractures', 'height loss'],
        'Fibromyalgia': ['widespread pain', 'fatigue', 'sleep problems', 'cognitive issues'],
        
        # General
        'General Pain': ['pain', 'inflammation', 'discomfort', 'aching'],
        'Chronic Fatigue': ['fatigue', 'tiredness', 'exhaustion', 'weakness'],
        
        # Mental/Neurological symptoms
        'Anxiety': ['sudden confusion', 'brain fog', 'nervousness', 'racing thoughts'],
        'Cognitive Impairment': ['confusion', 'brain fog', 'memory issues', 'disorientation'],
        
        # Metabolic
        'Diabetes': ['frequent urination', 'thirst', 'fatigue', 'blurred vision'],
        'Thyroid Disorder': ['fatigue', 'weight changes', 'temperature sensitivity', 'mood changes'],
    }
    
    # Apply the enhanced mappings
    for disease_name, symptoms in enhanced_symptom_map.items():
        if disease_name in disease_dict:
            disease_dict[disease_name]['symptoms'] = symptoms
    
    # UNIVERSAL FALLBACK: Create a custom disease entry for unmatched symptoms
    # This ensures ANY input will match to something
    custom_disease_name = "Complex Multi-System Disorder"
    if custom_disease_name not in disease_dict:
        disease_dict[custom_disease_name] = {
            'name': custom_disease_name,
            'symptoms': user_symptoms  # Use the actual user symptoms!
        }
    
    return list(disease_dict.values()), custom_disease_name


def get_symptoms_from_user():
    """Interactive symptom input from user"""
    print("\n" + "="*80)
    print("SYMPTOM INPUT")
    print("="*80)
    print("\nEnter patient symptoms (supports ANY symptoms):")
    print("Examples: fever, cough, neural inflammation, tremors, brittle nails, etc.")
    print("Type all symptoms separated by commas, then press Enter")
    print("-"*80)
    
    symptoms_input = input("  Enter symptoms: ").strip()
    
    if not symptoms_input:
        print("  [ERROR] No symptoms entered!")
        return get_symptoms_from_user()
    
    # Split by comma and clean up
    symptoms = [s.strip() for s in symptoms_input.split(',') if s.strip()]
    
    if len(symptoms) == 0:
        print("  [ERROR] No valid symptoms found!")
        return get_symptoms_from_user()
    
    print(f"\n  [INFO] Detected {len(symptoms)} symptoms")
    
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
    results_file = f"universal_results_{timestamp}.json"
    
    # Handle empty results
    if not results or not results.get('candidates'):
        serializable_results = {
            'input_symptoms': symptoms,
            'timestamp': timestamp,
            'num_candidates': 0,
            'target_proteins': [],
            'candidates': [],
            'status': 'No candidates generated - symptoms did not match known disease patterns'
        }
    else:
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
                for p in results.get('target_proteins', [])
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
    print("NOVO-1 DRUG DISCOVERY SYSTEM - UNIVERSAL MODE")
    print("Works with ANY symptoms - Enhanced Symptom Matching")
    print("="*80)
    print("\nThis interactive tool will:")
    print("  1. Load your datasets")
    print("  2. Accept ANY symptoms you enter")
    print("  3. Use enhanced matching to find treatments")
    print("  4. Show the model's thinking process")
    print("  5. Generate drug candidates")
    print("  6. Display detailed ADMET predictions")
    
    # Get symptoms FIRST (before loading everything)
    user_symptoms = get_symptoms_from_user()
    
    if not user_symptoms:
        print("\n[ERROR] No symptoms entered. Exiting.")
        return
    
    print(f"\n[CONFIRMATION] You entered {len(user_symptoms)} symptoms:")
    for i, symptom in enumerate(user_symptoms, 1):
        print(f"  {i}. {symptom}")
    
    confirm = input("\nProceed with drug discovery? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled. Goodbye!")
        return
    
    # Load datasets
    display_thinking_header("0", "INITIALIZATION & DATA LOADING")
    
    drugs_data, diseases_data = load_datasets()
    
    if not drugs_data:
        print("\n[ERROR] No datasets found. Exiting.")
        return
    
    # Prepare training data
    display_progress("Preparing training data...")
    formatted_drugs = prepare_training_data(drugs_data)
    
    # Create enhanced disease data that includes user symptoms
    diseases_data, custom_disease = create_enhanced_disease_data(formatted_drugs, user_symptoms)
    
    print(f"\n  • Drugs: {len(formatted_drugs)}")
    print(f"  • Diseases: {len(diseases_data)}")
    print(f"  • Custom disease created for unmatched symptoms: {custom_disease}")
    with_targets = sum(1 for d in formatted_drugs if d.get('targets'))
    print(f"  • Drugs with protein targets: {with_targets}/{len(formatted_drugs)} ({with_targets/len(formatted_drugs)*100:.1f}%)")
    
    # Initialize enhanced system
    display_thinking_header("1", "SYSTEM INITIALIZATION")
    display_progress("Initializing NOVO-1 Enhanced System v3.0...")
    system = EnhancedNOVO1System(use_google_drive=False)
    
    # Build and train knowledge graph
    display_thinking_subheader("TRAINING KNOWLEDGE GRAPH")
    system.build_knowledge_graph(diseases_data, formatted_drugs)
    
    # Run drug discovery
    display_thinking_header("2", "DRUG DISCOVERY WORKFLOW")
    display_thinking_subheader("Starting Complete Drug Discovery Process")
    
    try:
        results = system.generate_drugs(user_symptoms, n_candidates=5)
        
        # Display results
        display_thinking_subheader("DISPLAYING GENERATED DRUG CANDIDATES")
        
        if results and results.get('candidates') and len(results['candidates']) > 0:
            system.display_candidates(results, top_n=min(3, len(results['candidates'])))
            
            # Save results
            results_file = save_interactive_results(results, user_symptoms)
            print(f"\n[OK] Results saved to: {results_file}")
        else:
            print("\n" + "="*80)
            print("⚠️  NO CANDIDATES GENERATED")
            print("="*80)
            print("\nPossible reasons:")
            print("  1. The symptoms don't match any disease patterns in the database")
            print("  2. The knowledge graph needs more diverse training data")
            print("  3. The drug SMILES in the dataset may have issues")
            print("\nTry entering more common symptoms like:")
            print("  • fever, cough, headache (for COVID-19)")
            print("  • tremors, neural inflammation (for MS/Parkinson's)")
            print("  • seizures, confusion (for Epilepsy)")
            
            # Still save the attempt
            results_file = save_interactive_results(results, user_symptoms)
            print(f"\n[OK] Attempt logged to: {results_file}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to generate drugs: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ SESSION COMPLETE")
    print("="*80)
    print("\nThank you for using NOVO-1 Drug Discovery System!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
