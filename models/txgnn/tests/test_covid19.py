"""
COVID-19 Drug Repurposing Test Suite
Tests TxGNN predictions on COVID-19 symptoms.
"""

import sys
import os
# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from txgnn.utils.predictor import TxGNNPredictor


class COVID19Tester:
    """Test TxGNN on COVID-19 symptoms and known treatments."""
    
    def __init__(self):
        self.predictor = TxGNNPredictor()
        
        # Standard COVID-19 symptoms
        self.covid_symptoms = {
            'mild': ['fever', 'cough', 'fatigue', 'loss_of_taste'],
            'moderate': ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'loss_of_smell', 'muscle_pain'],
            'severe': ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'chest_pain', 'difficulty_breathing', 'chills'],
        }
        
        # Known COVID-19 treatments (ground truth)
        self.known_treatments = [
            'remdesivir', 'paxlovid', 'molnupiravir',  # Antivirals
            'dexamethasone',  # Anti-inflammatory for severe cases
            'baricitinib', 'tocilizumab',  # Immunomodulators
        ]
        
        # Symptomatic treatments
        self.symptomatic_treatments = [
            'acetaminophen', 'ibuprofen',  # Fever/pain
            'dextromethorphan',  # Cough
        ]
    
    def test_symptom_set(self, severity: str, top_k: int = 15):
        """Test predictions for a specific severity level."""
        symptoms = self.covid_symptoms[severity]
        
        print(f"\n{'='*70}")
        print(f"COVID-19 {severity.upper()} CASE TEST")
        print(f"{'='*70}")
        print(f"Symptoms: {', '.join(symptoms)}")
        print(f"{'='*70}")
        
        predictions = self.predictor.predict_drugs(symptoms, top_k=top_k)
        
        # Evaluate against known treatments
        print(f"\nEVALUATION:")
        print(f"Known effective treatments for COVID-19:")
        for drug in self.known_treatments:
            status = "[OK] FOUND" if any(d[0] == drug for d in predictions) else "[X] Not in top-k"
            print(f"  - {drug:20s} {status}")
        
        return predictions
    
    def run_all_tests(self):
        """Run tests for all severity levels."""
        print("\n" + "="*70)
        print("COVID-19 DRUG REPURPOSING TEST SUITE")
        print("="*70)
        print("\nThis test evaluates TxGNN's ability to predict drug candidates")
        print("for COVID-19 based on symptom patterns.")
        print("\nNote: Model uses random initialization (not trained on real data)")
        print("Real predictions require training on large-scale biomedical data.")
        print("="*70)
        
        results = {}
        
        for severity in ['mild', 'moderate', 'severe']:
            results[severity] = self.test_symptom_set(severity)
        
        # Summary
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print(f"{'='*70}")
        print("\nThis demonstration shows the TxGNN architecture predicting")
        print("drug candidates from COVID-19 symptoms.")
        print("\nFor production use, the model should be trained on:")
        print("- PrimeKG knowledge graph (100K+ nodes)")
        print("- Clinical trial data")
        print("- Drug-disease interaction databases")
        print("- Real-world evidence from patient records")
        print(f"{'='*70}\n")
        
        return results
    
    def test_individual_symptom(self, symptom: str):
        """Test predictions for a single symptom."""
        print(f"\n{'='*70}")
        print(f"TESTING: {symptom.upper()}")
        print(f"{'='*70}")
        
        predictions = self.predictor.predict_drugs([symptom], top_k=10)
        return predictions
    
    def interactive_test(self):
        """Interactive testing mode."""
        print("\n" + "="*70)
        print("INTERACTIVE COVID-19 DRUG PREDICTION")
        print("="*70)
        print("\nAvailable symptoms:")
        
        all_symptoms = []
        for symptom_list in self.covid_symptoms.values():
            all_symptoms.extend(symptom_list)
        all_symptoms = list(set(all_symptoms))
        
        for i, symptom in enumerate(all_symptoms, 1):
            print(f"  {i:2d}. {symptom}")
        
        print("\nEnter symptoms (comma-separated) or 'quit' to exit:")
        print("Example: fever, cough, fatigue")
        
        while True:
            user_input = input("\nSymptoms > ").strip().lower()
            
            if user_input == 'quit':
                break
            
            symptoms = [s.strip() for s in user_input.split(',')]
            self.predictor.predict_drugs(symptoms, top_k=10)


def main():
    """Main test runner."""
    tester = COVID19Tester()
    
    # Run automated tests
    tester.run_all_tests()
    
    # Uncomment for interactive mode:
    # tester.interactive_test()


if __name__ == "__main__":
    main()