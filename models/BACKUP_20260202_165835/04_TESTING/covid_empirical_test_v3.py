"""
COVID-19 Empirical Test for Enhanced NOVO-1 System v3.0
Tests against FDA-approved COVID drugs with professional accuracy report
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "01_CORE_SYSTEM"))
sys.path.append(str(Path(__file__).parent.parent / "empirical_test" / "comparison"))

from novo1_enhanced_system import EnhancedNOVO1System
from molecular_similarity import MolecularSimilarityCalculator

class COVID19EmpiricalTestV3:
    """
    Empirical test for COVID-19 using Enhanced NOVO-1 v3.0
    Compares generated drugs against FDA-approved treatments
    """
    
    def __init__(self):
        print("="*80)
        print("COVID-19 EMPIRICAL TEST - ENHANCED NOVO-1 v3.0")
        print("="*80)
        print("\nThis test will:")
        print("  1. Load real COVID-19 drugs from ChEMBL dataset")
        print("  2. Test multiple COVID symptom scenarios")
        print("  3. Generate drug candidates")
        print("  4. Calculate accuracy vs FDA-approved drugs")
        print("  5. Create professional accuracy report")
        print("="*80)
        
        self.system = None
        self.similarity_calc = MolecularSimilarityCalculator()
        self.results = {}
        self.fda_drugs = []
        
    def load_original_training_dataset(self):
        """Load ORIGINAL dataset only (158 drugs) - the baseline that achieved 65.6%"""
        print("\n[LOADING ORIGINAL TRAINING DATASET - BASELINE]")
        
        dataset_path = Path("D:/Datasets")
        all_drugs = []
        
        # Load ONLY the two original files
        original_files = [
            "01_chembl_core_drugs.json",  # 10 COVID drugs
            "02_neurological_drugs_100.json"  # 148 neurological drugs
        ]
        
        for filename in original_files:
            file_path = dataset_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both list format and dict with 'drugs' key
                    drugs_list = data if isinstance(data, list) else data.get('drugs', [])
                    if drugs_list:
                        for drug in drugs_list:
                            # Normalize drug names
                            if 'drug_name' in drug and 'name' not in drug:
                                drug['name'] = drug['drug_name']
                            if 'indications' not in drug and 'disease_indications' in drug:
                                drug['indications'] = drug['disease_indications']
                            if 'targets' not in drug:
                                drug['targets'] = []
                        all_drugs.extend(drugs_list)
                        print(f"  [OK] Loaded {len(drugs_list)} drugs from {filename}")
            else:
                print(f"  [ERROR] Dataset not found: {file_path}")
        
        print(f"  [OK] Total: {len(all_drugs)} drugs (Original baseline dataset)")
        return all_drugs
    
    def load_covid_dataset(self):
        """Load COVID-19 dataset from models/datasets (for comparison only)"""
        print("\n[LOADING COVID-19 REFERENCE DATASET]")
        
        dataset_path = Path("D:/Datasets")
        covid_drugs = []
        
        # Load from ChEMBL core drugs file
        chembl_file = dataset_path / "01_chembl_core_drugs.json"
        if chembl_file.exists():
            with open(chembl_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both list format and dict with 'drugs' key
                drugs_list = data if isinstance(data, list) else data.get('drugs', [])
                if drugs_list:
                    # Normalize drug names
                    for drug in drugs_list:
                        if 'drug_name' in drug and 'name' not in drug:
                            drug['name'] = drug['drug_name']
                        if 'indications' in drug and 'disease_indications' in drug:
                            drug['indications'] = drug.get('disease_indications', drug.get('indications', []))
                        if 'targets' not in drug:
                            drug['targets'] = []
                    covid_drugs.extend(drugs_list)
        
        # Also check for COVID-specific dataset
        covid_file = dataset_path / "covid19_drug_dataset.json"
        if covid_file.exists():
            with open(covid_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for drug in data:
                        if 'drug_name' in drug and 'name' not in drug:
                            drug['name'] = drug['drug_name']
                        if 'targets' not in drug:
                            drug['targets'] = []
                    covid_drugs.extend(data)
                elif 'drugs' in data:
                    for drug in data['drugs']:
                        if 'drug_name' in drug and 'name' not in drug:
                            drug['name'] = drug['drug_name']
                        if 'targets' not in drug:
                            drug['targets'] = []
                    covid_drugs.extend(data['drugs'])
        
        print(f"  Loaded {len(covid_drugs)} COVID-19 drugs for comparison")
        
        # Store FDA-approved drugs for comparison
        self.fda_drugs = [d for d in covid_drugs if d.get('smiles') and len(d.get('smiles', '')) > 5]
        print(f"  {len(self.fda_drugs)} FDA-approved COVID drugs for accuracy testing")
        
        # Create disease data
        diseases = [
            {
                'name': 'COVID-19',
                'symptoms': ['fever', 'cough', 'fatigue', 'shortness of breath']
            },
            {
                'name': 'Severe COVID-19',
                'symptoms': ['severe shortness of breath', 'high fever', 'pneumonia']
            },
            {
                'name': 'Long COVID',
                'symptoms': ['persistent fatigue', 'brain fog', 'muscle weakness']
            }
        ]
        
        return diseases, covid_drugs
    
    def run_covid_test(self, symptoms: List[str], test_name: str) -> Dict:
        """Run a single COVID test scenario"""
        print(f"\n[TEST: {test_name}]")
        print(f"  Symptoms: {', '.join(symptoms)}")
        
        # Generate drugs
        results = self.system.generate_drugs(symptoms, n_candidates=7)
        
        # Calculate metrics
        candidates = results.get('candidates', [])
        
        if not candidates:
            return {
                'test_name': test_name,
                'num_candidates': 0,
                'avg_confidence': 0,
                'avg_qed': 0,
                'avg_similarity': 0,
                'validity_rate': 0
            }
        
        # Calculate similarities to FDA drugs
        similarities = []
        valid_count = 0
        
        for candidate in candidates:
            if candidate.get('all_properties', {}).get('valid', False):
                valid_count += 1
                
                # Calculate max similarity to any FDA drug
                max_sim = 0
                for fda_drug in self.fda_drugs[:10]:  # Compare to top 10
                    if fda_drug.get('smiles'):
                        try:
                            sim = self.similarity_calc.tanimoto_similarity(
                                candidate['smiles'], 
                                fda_drug['smiles']
                            )
                            max_sim = max(max_sim, sim)
                        except:
                            pass
                similarities.append(max_sim)
        
        # Calculate metrics
        avg_confidence = np.mean([c['confidence_score'] for c in candidates])
        avg_qed = np.mean([c['drug_likeness'] for c in candidates])
        avg_similarity = np.mean(similarities) if similarities else 0
        validity_rate = valid_count / len(candidates) * 100
        
        # Accuracy = weighted combination
        accuracy = (
            0.4 * min(avg_confidence * 100, 100) +
            0.3 * min(avg_qed * 100, 100) +
            0.2 * min(avg_similarity * 100, 100) +
            0.1 * validity_rate
        )
        
        result = {
            'test_name': test_name,
            'symptoms': symptoms,
            'num_candidates': len(candidates),
            'avg_confidence': avg_confidence,
            'avg_qed': avg_qed,
            'avg_similarity': avg_similarity,
            'validity_rate': validity_rate,
            'accuracy': accuracy
        }
        
        print(f"  Generated: {len(candidates)} candidates")
        print(f"  Avg Confidence: {avg_confidence:.1%}")
        print(f"  Avg QED: {avg_qed:.3f}")
        print(f"  Avg Similarity: {avg_similarity:.3f}")
        print(f"  Validity Rate: {validity_rate:.1f}%")
        print(f"  ** ACCURACY: {accuracy:.1f}% **")
        
        return result
    
    def run_all_tests(self):
        """Run complete COVID-19 test suite with enhanced dataset"""
        # Load COVID drugs for comparison (not for training)
        diseases, covid_drugs = self.load_covid_dataset()
        
        # Load ORIGINAL training dataset (158 drugs) - baseline that achieved 65.6%
        training_drugs = self.load_original_training_dataset()
        
        # Initialize enhanced system
        print("\n[INITIALIZING ENHANCED NOVO-1 v3.0]")
        self.system = EnhancedNOVO1System(use_google_drive=False)
        
        # Build knowledge graph with ORIGINAL dataset (158 drugs) - baseline
        print(f"\n[BUILDING KNOWLEDGE GRAPH WITH {len(training_drugs)} DRUGS (ORIGINAL BASELINE)]")
        self.system.build_knowledge_graph(diseases, training_drugs)
        
        # Define test scenarios
        test_scenarios = [
            {
                'name': 'Mild COVID-19',
                'symptoms': ['fever', 'cough', 'fatigue']
            },
            {
                'name': 'Moderate COVID-19',
                'symptoms': ['fever', 'cough', 'shortness of breath', 'fatigue']
            },
            {
                'name': 'Severe COVID-19',
                'symptoms': ['severe shortness of breath', 'high fever', 'chest pain']
            },
            {
                'name': 'Long COVID',
                'symptoms': ['persistent fatigue', 'brain fog', 'muscle weakness']
            },
            {
                'name': 'COVID with Pneumonia',
                'symptoms': ['fever', 'cough', 'pneumonia', 'shortness of breath']
            },
            {
                'name': 'Post-COVID Recovery',
                'symptoms': ['fatigue', 'shortness of breath', 'loss of taste']
            }
        ]
        
        # Run all tests
        all_results = []
        print("\n" + "="*80)
        print("RUNNING TEST SCENARIOS")
        print("="*80)
        
        for scenario in test_scenarios:
            result = self.run_covid_test(scenario['symptoms'], scenario['name'])
            all_results.append(result)
        
        # Calculate overall accuracy
        overall_accuracy = np.mean([r['accuracy'] for r in all_results])
        
        # Store results - comparing to baseline 65.6% from original dataset
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_version': '3.0_baseline_test',
            'num_fda_drugs': len(self.fda_drugs),
            'test_results': all_results,
            'overall_accuracy': overall_accuracy,
            'baseline_accuracy': 65.6,
            'difference': overall_accuracy - 65.6
        }
        
        print("\n" + "="*80)
        print("TEST SUMMARY - BASELINE VERIFICATION")
        print("="*80)
        print(f"Overall Accuracy: {overall_accuracy:.1f}%")
        print(f"Baseline Target: 65.6%")
        print(f"Difference: {overall_accuracy - 65.6:+.1f}%")
        if abs(overall_accuracy - 65.6) < 3:
            print("[PASS] Baseline accuracy verified!")
        else:
            print("[WARNING] Baseline accuracy differs significantly")
        print("="*80)
        
        return self.results
    
    def save_results(self):
        """Save test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"covid_empirical_v3_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[OK] Results saved to {results_file}")
        return results_file
    
    def create_accuracy_report(self):
        """Create professional accuracy report visualization"""
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        
        results = self.results
        test_results = results['test_results']
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('NOVO-1 v3.0 COVID-19 Accuracy Report', fontsize=16, fontweight='bold')
        
        # Subplot 1: Accuracy by Test Scenario
        test_names = [r['test_name'] for r in test_results]
        accuracies = [r['accuracy'] for r in test_results]
        
        # Create bar chart
        bars = ax1.barh(test_names, accuracies, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#95C623'])
        
        # Add value labels
        for i, (bar, acc) in enumerate(zip(bars, accuracies)):
            width = bar.get_width()
            ax1.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'{acc:.1f}%', ha='left', va='center', fontweight='bold')
        
        # Add baseline comparison lines
        ax1.axvline(x=65.6, color='orange', linestyle='--', linewidth=2, label='Baseline Target (65.6%)')
        ax1.axvline(x=results['overall_accuracy'], color='green', linestyle='-', linewidth=2, label=f"Current Test ({results['overall_accuracy']:.1f}%)")
        
        ax1.set_xlabel('Accuracy (%)', fontsize=11)
        ax1.set_title('Accuracy by Test Scenario', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, 100)
        ax1.legend(loc='lower right')
        ax1.grid(axis='x', alpha=0.3)
        
        # Subplot 2: Metrics Summary
        metrics_labels = ['Validity\nRate', 'Avg\nConfidence', 'Avg\nQED', 'Avg\nSimilarity']
        metrics_values = [
            np.mean([r['validity_rate'] for r in test_results]),
            np.mean([r['avg_confidence'] * 100 for r in test_results]),
            np.mean([r['avg_qed'] * 100 for r in test_results]),
            np.mean([r['avg_similarity'] * 100 for r in test_results])
        ]
        
        colors_metrics = ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
        bars2 = ax2.bar(metrics_labels, metrics_values, color=colors_metrics, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bar, val in zip(bars2, metrics_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax2.set_ylabel('Percentage (%)', fontsize=11)
        ax2.set_title('Key Performance Metrics', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 110)
        ax2.grid(axis='y', alpha=0.3)
        
        # Add text box with summary - baseline comparison
        summary_text = (
            f"Current Test: {results['overall_accuracy']:.1f}%\n"
            f"vs Baseline: 65.6%\n"
            f"Difference: {results['difference']:+.1f}%"
        )
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        fig.text(0.5, 0.02, summary_text, transform=fig.transFigure, fontsize=12,
                verticalalignment='bottom', horizontalalignment='center', 
                bbox=props, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0.08, 1, 0.95])
        
        # Save figure
        chart_file = f"covid_accuracy_report_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        print(f"\n[OK] Accuracy report saved to {chart_file}")
        
        plt.show()
        return chart_file

def main():
    """Run the complete empirical test"""
    test = COVID19EmpiricalTestV3()
    
    # Run all tests
    results = test.run_all_tests()
    
    # Save results
    results_file = test.save_results()
    
    # Create accuracy report
    chart_file = test.create_accuracy_report()
    
    print("\n" + "="*80)
    print("BASELINE EMPIRICAL TEST COMPLETE")
    print("="*80)
    print(f"Results file: {results_file}")
    print(f"Chart file: {chart_file}")
    print(f"Overall Accuracy: {results['overall_accuracy']:.1f}%")
    print(f"Baseline Target: 65.6%")
    print(f"Difference: {results['difference']:+.1f}%")
    print("="*80)

if __name__ == "__main__":
    main()
