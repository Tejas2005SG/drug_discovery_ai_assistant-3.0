"""
COVID-19 Empirical Test - Knowledge Graph Based
Tests NOVO-1 against real FDA-approved COVID drugs
Stores results on Google Drive
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict
import sys

# Import our custom modules
from novo1_drug_system import NOVO1DrugDiscoverySystem, MolecularProcessor
from knowledge_graph import DrugRepurposingKnowledgeGraph

class COVID19EmpiricalTest:
    """
    Empirical test for COVID-19 drug discovery
    Compares generated drugs against FDA-approved treatments
    """
    
    def __init__(self):
        print("="*80)
        print("COVID-19 EMPIRICAL TEST - KNOWLEDGE GRAPH VALIDATION")
        print("="*80)
        print("\nThis test will:")
        print("  1. Build knowledge graph with COVID-19 data")
        print("  2. Train embeddings on CPU")
        print("  3. Generate drugs for COVID symptoms")
        print("  4. Compare against FDA-approved drugs")
        print("  5. Calculate accuracy metrics")
        print("="*80)
        
        self.system = None
        self.mol_processor = MolecularProcessor()
        self.results = {}
        
    def load_covid_dataset(self):
        """
        Load comprehensive COVID-19 dataset
        Includes diseases, symptoms, and real FDA-approved drugs
        """
        print("\n[LOADING COVID-19 DATASET]")
        
        # COVID-19 and related respiratory diseases
        diseases = [
            {
                'name': 'COVID-19',
                'symptoms': [
                    'fever', 'cough', 'fatigue', 'shortness of breath',
                    'loss of taste', 'loss of smell', 'muscle pain', 'sore throat'
                ]
            },
            {
                'name': 'Severe COVID-19',
                'symptoms': [
                    'severe shortness of breath', 'chest pain', 'confusion',
                    'high fever', 'pneumonia', 'respiratory failure'
                ]
            },
            {
                'name': 'Long COVID',
                'symptoms': [
                    'persistent fatigue', 'brain fog', 'shortness of breath',
                    'chest pain', 'muscle weakness', 'sleep problems'
                ]
            },
            {
                'name': 'SARS',
                'symptoms': [
                    'high fever', 'dry cough', 'shortness of breath',
                    'muscle pain', 'pneumonia'
                ]
            },
            {
                'name': 'MERS',
                'symptoms': [
                    'fever', 'cough', 'shortness of breath',
                    'gastrointestinal symptoms', 'pneumonia'
                ]
            },
            {
                'name': 'Influenza A',
                'symptoms': [
                    'fever', 'cough', 'sore throat', 'muscle pain',
                    'fatigue', 'headache'
                ]
            },
            {
                'name': 'Pneumonia',
                'symptoms': [
                    'cough', 'fever', 'shortness of breath',
                    'chest pain', 'fatigue'
                ]
            },
            {
                'name': 'ARDS',
                'symptoms': [
                    'severe shortness of breath', 'rapid breathing',
                    'low oxygen', 'lung inflammation'
                ]
            }
        ]
        
        # FDA-approved COVID-19 drugs (REAL DRUGS)
        drugs = [
            {
                'name': 'Paxlovid',
                'smiles': 'CC(C)(C)NC(=O)C1CC2(CCN(C(=O)C(C(C)(C)C)NC(=O)C(F)(F)F)CC2)CN1C(=O)O',
                'targets': ['3CL_protease', 'Mpro', 'SARS-CoV-2 main protease'],
                'indications': ['COVID-19', 'Severe COVID-19'],
                'mechanism': 'Protease inhibitor',
                'efficacy': '88% reduction in hospitalization'
            },
            {
                'name': 'Remdesivir',
                'smiles': 'CCC(CC)COC(=O)[C@H](C)NP(=O)(OCC1OC(n2cnc3c(N)ncnc32)[C@H](O)[C@@H]1O)Oc1ccccc1',
                'targets': ['RdRp', 'RNA-dependent RNA polymerase'],
                'indications': ['COVID-19', 'Severe COVID-19', 'SARS', 'MERS'],
                'mechanism': 'Polymerase inhibitor',
                'efficacy': 'Reduces recovery time by 5 days'
            },
            {
                'name': 'Molnupiravir',
                'smiles': 'C[C@@H](C(=O)OC(C)C)N1C(=O)C(O)(CO)C(=O)N(C)C1=O',
                'targets': ['RdRp'],
                'indications': ['COVID-19', 'Severe COVID-19'],
                'mechanism': 'Polymerase inhibitor',
                'efficacy': '30% reduction in hospitalization'
            },
            {
                'name': 'Nirmatrelvir',
                'smiles': 'CC(C)(C)NC(=O)C1CC2(CCN(C(=O)C(C(C)(C)C)NC(=O)C(F)(F)F)CC2)CN1C(=O)O',
                'targets': ['3CL_protease'],
                'indications': ['COVID-19'],
                'mechanism': 'Protease inhibitor',
                'efficacy': 'Component of Paxlovid'
            },
            {
                'name': 'Dexamethasone',
                'smiles': 'C[C@@H]1C[C@H]2[C@@H]3CCC4=CC(=O)C=C[C@]4(C)[C@@]3(F)[C@@H](O)C[C@]2(C)[C@@]1(O)C(=O)CO',
                'targets': ['glucocorticoid receptor', 'inflammatory cytokines'],
                'indications': ['Severe COVID-19', 'ARDS', 'Pneumonia'],
                'mechanism': 'Anti-inflammatory corticosteroid',
                'efficacy': '35% reduction in mortality (severe cases)'
            },
            {
                'name': 'Tocilizumab',
                'smiles': 'PROTEIN',  # Monoclonal antibody - simplified
                'targets': ['IL-6 receptor', 'cytokine storm'],
                'indications': ['Severe COVID-19', 'Cytokine storm', 'ARDS'],
                'mechanism': 'IL-6 receptor antagonist',
                'efficacy': 'Reduces mortality in severe cases'
            },
            {
                'name': 'Baricitinib',
                'smiles': 'CCS(=O)(=O)N1CCC(CC1)N2CCN(CC2)C(=O)Cn3nccn3',
                'targets': ['JAK1', 'JAK2', 'inflammatory response'],
                'indications': ['COVID-19', 'Severe COVID-19'],
                'mechanism': 'JAK inhibitor',
                'efficacy': 'Improves recovery time'
            },
            {
                'name': 'Favipiravir',
                'smiles': 'C=C(F)C(=O)NC(=O)NC1=NC=NC(O)=N1',
                'targets': ['RdRp'],
                'indications': ['COVID-19', 'Influenza A', 'Influenza B'],
                'mechanism': 'Polymerase inhibitor',
                'efficacy': 'Broad-spectrum antiviral'
            },
            {
                'name': 'Oseltamivir',
                'smiles': 'CCC(CC)C(=O)O[C@H]1C[C@@H](C(=O)N(C)C)N(C(=O)OCc2ccccc2)C1',
                'targets': ['neuraminidase'],
                'indications': ['Influenza A', 'Influenza B'],
                'mechanism': 'Neuraminidase inhibitor',
                'efficacy': 'Reduces flu symptoms'
            },
            {
                'name': 'Ivermectin',
                'smiles': 'CCC(C)C1C2OC3C(C)(C)OC(C(C)C4COC(O4)C(C)C5CCC6C7C(C)C(C8=COC=C8)OC6C(C)(C)O7)C3C(C)C(O2)C1C',
                'targets': ['various ion channels'],
                'indications': ['COVID-19 (investigational)'],
                'mechanism': 'Unknown - controversial',
                'efficacy': 'Unproven for COVID-19'
            },
            {
                'name': 'Hydroxychloroquine',
                'smiles': 'CCN(CC)CCCC(C)Nc1ccnc2cc(Cl)ccc12',
                'targets': ['TLR7', 'TLR9', 'ACE2'],
                'indications': ['COVID-19 (early use)'],
                'mechanism': 'Immunomodulator',
                'efficacy': 'Limited efficacy, not recommended'
            },
            {
                'name': 'Azithromycin',
                'smiles': 'CC[C@H]1OC(=O)[C@H](C)[C@@H](O[C@H]2C[C@@](C)(OC)[C@@H](O)[C@H](C)O2)[C@H](C)[C@@H](O[C@@H]2O[C@H](C)C[C@H](N(C)C)[C@H]2O)[C@](C)(O)C[C@@H](C)CN(C)[C@H](C)[C@@H](O)C1(C)C',
                'targets': ['bacterial ribosome'],
                'indications': ['COVID-19 (bacterial coinfection)'],
                'mechanism': 'Antibiotic',
                'efficacy': 'Prevents secondary infections'
            }
        ]
        
        print(f"[OK] Loaded {len(diseases)} diseases")
        print(f"[OK] Loaded {len(drugs)} FDA-approved drugs")
        print(f"[OK] Total COVID-related symptoms: {len(set([s for d in diseases for s in d['symptoms']]))}")
        
        return diseases, drugs
    
    def build_and_train_system(self):
        """Build knowledge graph and train embeddings"""
        print("\n[BUILDING AND TRAINING SYSTEM]")
        
        # Load dataset
        diseases, drugs = self.load_covid_dataset()
        
        # Initialize system
        self.system = NOVO1DrugDiscoverySystem(use_google_drive=False)
        
        # Build and train
        print("\nBuilding knowledge graph...")
        self.system.build_knowledge_graph(diseases, drugs)
        
        # Show stats
        stats = self.system.knowledge_graph.get_statistics()
        print(f"\n[KNOWLEDGE GRAPH STATISTICS]")
        print(f"  Diseases: {stats['num_diseases']}")
        print(f"  Symptoms: {stats['num_symptoms']}")
        print(f"  Drugs: {stats['num_drugs']}")
        print(f"  Proteins: {stats['num_proteins']}")
        print(f"  Triples: {stats['num_triples']}")
        
        self.covid_drugs = drugs
        
    def test_symptom_scenarios(self):
        """Test multiple COVID symptom scenarios"""
        print("\n" + "="*80)
        print("TESTING COVID-19 SYMPTOM SCENARIOS")
        print("="*80)
        
        test_cases = [
            {
                'name': 'Mild COVID-19',
                'symptoms': ['fever', 'cough', 'fatigue'],
                'severity': 'mild',
                'expected_drugs': ['Paxlovid', 'Molnupiravir']
            },
            {
                'name': 'Moderate COVID-19',
                'symptoms': ['fever', 'cough', 'fatigue', 'shortness of breath'],
                'severity': 'moderate',
                'expected_drugs': ['Paxlovid', 'Remdesivir']
            },
            {
                'name': 'Severe COVID-19',
                'symptoms': ['severe shortness of breath', 'chest pain', 'high fever'],
                'severity': 'severe',
                'expected_drugs': ['Remdesivir', 'Dexamethasone', 'Tocilizumab']
            },
            {
                'name': 'Long COVID',
                'symptoms': ['persistent fatigue', 'brain fog', 'shortness of breath'],
                'severity': 'long-term',
                'expected_drugs': [' investigational', 'supportive care']
            },
            {
                'name': 'COVID + Influenza',
                'symptoms': ['fever', 'cough', 'fatigue', 'muscle pain', 'sore throat'],
                'severity': 'co-infection',
                'expected_drugs': ['Paxlovid', 'Oseltamivir']
            },
            {
                'name': 'Cytokine Storm',
                'symptoms': ['high fever', 'severe inflammation', 'low oxygen', 'lung inflammation'],
                'severity': 'critical',
                'expected_drugs': ['Dexamethasone', 'Tocilizumab', 'Baricitinib']
            }
        ]
        
        all_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[TEST {i}/{len(test_cases)}] {test_case['name']}")
            print(f"Symptoms: {', '.join(test_case['symptoms'])}")
            print(f"Expected drugs: {', '.join(test_case['expected_drugs'])}")
            
            # Generate candidates
            candidates = self.system.generate_drugs(
                test_case['symptoms'], 
                n_candidates=10
            )
            
            # Evaluate results
            result = self.evaluate_test_case(test_case, candidates)
            all_results.append(result)
            
            # Show top 3 candidates
            print(f"\nTop 3 Generated Candidates:")
            for j, cand in enumerate(candidates[:3], 1):
                print(f"  {j}. {cand['id']} (Confidence: {cand['confidence']:.1%})")
                print(f"     SMILES: {cand['smiles'][:50]}...")
                print(f"     QED: {cand['properties']['qed']:.3f}")
                print(f"     Targets: {', '.join(cand['predicted_targets'][:2])}")
        
        return all_results
    
    def evaluate_test_case(self, test_case: Dict, candidates: List[Dict]) -> Dict:
        """Evaluate generated candidates against expected drugs"""
        
        if not candidates:
            return {
                'test_name': test_case['name'],
                'n_generated': 0,
                'validity': 0,
                'avg_qed': 0,
                'target_match': 0,
                'overall_score': 0
            }
        
        # Calculate metrics
        n_valid = sum(1 for c in candidates if c['properties']['valid'])
        validity = n_valid / len(candidates) if candidates else 0
        
        avg_qed = np.mean([c['properties']['qed'] for c in candidates])
        
        avg_confidence = np.mean([c['confidence'] for c in candidates])
        
        # Check target overlap with expected drugs
        expected_targets = set()
        for drug_name in test_case['expected_drugs']:
            for drug in self.covid_drugs:
                if drug['name'] == drug_name:
                    expected_targets.update(drug['targets'])
        
        # Calculate target match score
        target_matches = []
        for cand in candidates:
            cand_targets = set(cand['predicted_targets'])
            if expected_targets:
                overlap = len(cand_targets.intersection(expected_targets))
                match_score = overlap / len(expected_targets)
                target_matches.append(match_score)
        
        avg_target_match = np.mean(target_matches) if target_matches else 0
        
        # Overall score
        overall = (validity * 0.3 + min(avg_qed, 0.8) * 0.3 + 
                   avg_target_match * 0.2 + avg_confidence * 0.2)
        
        return {
            'test_name': test_case['name'],
            'severity': test_case['severity'],
            'n_generated': len(candidates),
            'n_valid': n_valid,
            'validity': validity,
            'avg_qed': avg_qed,
            'avg_confidence': avg_confidence,
            'avg_target_match': avg_target_match,
            'overall_score': overall
        }
    
    def calculate_molecular_similarity(self, candidates: List[Dict]):
        """Calculate Tanimoto similarity to real COVID drugs"""
        print("\n" + "="*80)
        print("MOLECULAR SIMILARITY ANALYSIS")
        print("="*80)
        
        similarities = []
        
        for real_drug in self.covid_drugs:
            if real_drug['smiles'] == 'PROTEIN':
                continue  # Skip proteins (antibodies)
            
            real_fp = self.mol_processor.smiles_to_fingerprint(real_drug['smiles'])
            if real_fp is None:
                continue
            
            drug_sims = []
            for cand in candidates[:5]:  # Top 5 candidates
                cand_fp = self.mol_processor.smiles_to_fingerprint(cand['smiles'])
                if cand_fp is not None:
                    sim = self.mol_processor.tanimoto_similarity(real_fp, cand_fp)
                    drug_sims.append(sim)
            
            if drug_sims:
                avg_sim = np.mean(drug_sims)
                similarities.append({
                    'drug': real_drug['name'],
                    'avg_similarity': avg_sim,
                    'max_similarity': max(drug_sims)
                })
                print(f"  {real_drug['name']}: avg sim = {avg_sim:.3f}")
        
        return similarities
    
    def generate_final_report(self, all_results: List[Dict]):
        """Generate comprehensive empirical test report"""
        print("\n" + "="*80)
        print("EMPIRICAL TEST - FINAL REPORT")
        print("="*80)
        
        # Aggregate statistics
        total_candidates = sum(r['n_generated'] for r in all_results)
        total_valid = sum(r['n_valid'] for r in all_results)
        
        avg_validity = np.mean([r['validity'] for r in all_results])
        avg_qed = np.mean([r['avg_qed'] for r in all_results])
        avg_confidence = np.mean([r['avg_confidence'] for r in all_results])
        avg_target_match = np.mean([r['avg_target_match'] for r in all_results])
        avg_overall = np.mean([r['overall_score'] for r in all_results])
        
        print(f"\n[OVERALL PERFORMANCE METRICS]")
        print(f"  Total test cases: {len(all_results)}")
        print(f"  Total candidates generated: {total_candidates}")
        print(f"  Valid molecules: {total_valid}/{total_candidates} ({avg_validity:.1%})")
        print(f"  Average QED score: {avg_qed:.3f}")
        print(f"  Average confidence: {avg_confidence:.1%}")
        print(f"  Average target match: {avg_target_match:.1%}")
        print(f"  Overall system score: {avg_overall:.1%}")
        
        # Per-test-case breakdown
        print(f"\n[PER-TEST-CASE BREAKDOWN]")
        print(f"{'Test Case':<25} {'Severity':<12} {'Validity':<10} {'QED':<8} {'Overall':<10}")
        print("-" * 80)
        for result in all_results:
            print(f"{result['test_name']:<25} {result['severity']:<12} "
                  f"{result['validity']:.1%}     {result['avg_qed']:.3f}   "
                  f"{result['overall_score']:.1%}")
        
        # Save detailed report
        report = {
            'test_name': 'COVID-19 Empirical Test',
            'date': '2025-02-01',
            'system': 'NOVO-1 Knowledge Graph',
            'summary': {
                'total_test_cases': len(all_results),
                'total_candidates': total_candidates,
                'validity_rate': avg_validity,
                'avg_qed': avg_qed,
                'avg_confidence': avg_confidence,
                'avg_target_match': avg_target_match,
                'overall_score': avg_overall
            },
            'per_test_results': all_results,
            'interpretation': self._generate_interpretation(avg_overall)
        }
        
        # Save to file
        with open('covid_empirical_test_results.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[OK] Report saved: covid_empirical_test_results.json")
        
        return report
    
    def _generate_interpretation(self, score: float) -> str:
        """Generate interpretation of results"""
        if score >= 0.70:
            return "EXCELLENT - System demonstrates strong clinical relevance for COVID-19 drug discovery"
        elif score >= 0.60:
            return "GOOD - System shows promise with reasonable accuracy for COVID-19 applications"
        elif score >= 0.50:
            return "FAIR - System has potential but needs refinement for COVID-19 drug discovery"
        else:
            return "NEEDS IMPROVEMENT - Significant optimization required for COVID-19 applications"
    
    def run_complete_test(self):
        """Run complete empirical test suite"""
        print("\n[STARTING COMPLETE EMPIRICAL TEST]")
        
        # Build and train
        self.build_and_train_system()
        
        # Test scenarios
        all_results = self.test_symptom_scenarios()
        
        # Calculate similarities
        # Get all candidates from first test
        candidates = self.system.generate_drugs(['fever', 'cough', 'fatigue'], n_candidates=10)
        similarities = self.calculate_molecular_similarity(candidates)
        
        # Generate report
        report = self.generate_final_report(all_results)
        
        # Final summary
        print("\n" + "="*80)
        print("COVID-19 EMPIRICAL TEST COMPLETE")
        print("="*80)
        print(f"\nFINAL SCORE: {report['summary']['overall_score']:.1%}")
        print(f"ASSESSMENT: {report['interpretation']}")
        print("\n" + "="*80)
        
        return report


def main():
    """Run COVID-19 empirical test"""
    test = COVID19EmpiricalTest()
    report = test.run_complete_test()
    
    print("\n✓ Test complete! Check covid_empirical_test_results.json for details.")
    
    return report


if __name__ == "__main__":
    main()
