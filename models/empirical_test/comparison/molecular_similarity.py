"""
Molecular Similarity Calculator
Compares generated drugs with FDA-approved reference drugs
Uses Tanimoto coefficient and other molecular fingerprints
"""

import sys
sys.path.append('C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models')

import json
import numpy as np
from collections import Counter

class MolecularSimilarityCalculator:
    """
    Calculate molecular similarity between generated and reference drugs
    Uses multiple metrics: Tanimoto, structural similarity, target overlap
    """
    
    def __init__(self):
        self.similarity_threshold = 0.7
        print("="*70)
        print("MOLECULAR SIMILARITY CALCULATOR")
        print("="*70)
    
    def smiles_to_fingerprint(self, smiles):
        """
        Convert SMILES to simple binary fingerprint
        Uses character n-grams as features
        """
        if not smiles or len(smiles) < 3:
            return set()
        
        # Create n-gram features (3-character segments)
        ngrams = set()
        for i in range(len(smiles) - 2):
            ngrams.add(smiles[i:i+3])
        
        return ngrams
    
    def tanimoto_similarity(self, smiles1, smiles2):
        """
        Calculate Tanimoto coefficient between two molecules
        Tanimoto = |A ∩ B| / |A ∪ B|
        
        Returns:
            float: Similarity score [0, 1]
        """
        fp1 = self.smiles_to_fingerprint(smiles1)
        fp2 = self.smiles_to_fingerprint(smiles2)
        
        if not fp1 or not fp2:
            return 0.0
        
        intersection = len(fp1.intersection(fp2))
        union = len(fp1.union(fp2))
        
        if union == 0:
            return 0.0
        
        return round(intersection / union, 3)
    
    def calculate_all_similarities(self, generated_drugs, reference_drugs):
        """
        Calculate similarity matrix between all generated and reference drugs
        
        Returns:
            dict: Similarity matrix and best matches
        """
        print(f"\n{'='*70}")
        print("CALCULATING MOLECULAR SIMILARITIES")
        print(f"{'='*70}")
        print(f"Generated drugs: {len(generated_drugs)}")
        print(f"Reference drugs: {len(reference_drugs)}")
        print(f"{'='*70}\n")
        
        similarity_matrix = []
        best_matches = []
        
        for i, gen_drug in enumerate(generated_drugs):
            row = []
            best_sim = 0
            best_match = None
            
            for j, ref_drug in enumerate(reference_drugs):
                # Get reference SMILES - handle different key names
                ref_smiles = None
                if 'smiles' in ref_drug:
                    ref_smiles = ref_drug['smiles']
                elif 'smiles_nirmatrelvir' in ref_drug:
                    ref_smiles = ref_drug['smiles_nirmatrelvir']  # Use primary component
                
                if not ref_smiles or ref_smiles == 'PROTEIN_STRUCTURE_NOT_AVAILABLE':
                    row.append(0.0)  # Add placeholder for skipped drugs
                    continue  # Skip drugs without valid SMILES
                
                # Calculate Tanimoto similarity
                sim = self.tanimoto_similarity(gen_drug['smiles'], ref_smiles)
                row.append(sim)
                
                # Track best match
                if sim > best_sim:
                    best_sim = sim
                    best_match = {
                        'generated_id': gen_drug['id'],
                        'reference_name': ref_drug['name'],
                        'similarity': sim,
                        'generated_smiles': gen_drug['smiles'][:50] + '...',
                        'reference_smiles': ref_smiles[:50] + '...' if len(ref_smiles) > 50 else ref_smiles
                    }
            
            similarity_matrix.append(row)
            
            # Handle case where no valid reference drug was found
            if best_match is None:
                best_match = {
                    'generated_id': gen_drug['id'],
                    'reference_name': 'N/A',
                    'similarity': 0.0,
                    'generated_smiles': gen_drug['smiles'][:50] + '...',
                    'reference_smiles': 'N/A'
                }
            best_matches.append(best_match)
            
            if i < 5:  # Show first 5
                print(f"{i+1}. {gen_drug['id']}")
                print(f"   Best match: {best_match['reference_name']} (Similarity: {best_match['similarity']})")
                print()
        
        # Convert to numpy array for easier manipulation
        sim_matrix = np.array(similarity_matrix)
        
        return {
            'similarity_matrix': similarity_matrix,
            'best_matches': best_matches,
            'avg_similarity': round(np.mean([m['similarity'] for m in best_matches]), 3),
            'max_similarity': round(max([m['similarity'] for m in best_matches]), 3),
            'min_similarity': round(min([m['similarity'] for m in best_matches]), 3),
            'high_similarity_count': sum(1 for m in best_matches if m['similarity'] >= self.similarity_threshold),
            'medium_similarity_count': sum(1 for m in best_matches if 0.5 <= m['similarity'] < self.similarity_threshold),
            'low_similarity_count': sum(1 for m in best_matches if m['similarity'] < 0.5)
        }
    
    def compare_properties(self, generated_drugs, reference_drugs):
        """
        Compare molecular properties between generated and reference drugs
        """
        print(f"\n{'='*70}")
        print("COMPARING MOLECULAR PROPERTIES")
        print(f"{'='*70}\n")
        
        # Calculate property statistics for generated drugs
        gen_stats = {
            'avg_mw': round(np.mean([d['molecular_weight'] for d in generated_drugs]), 1),
            'std_mw': round(np.std([d['molecular_weight'] for d in generated_drugs]), 1),
            'avg_qed': round(np.mean([d['qed'] for d in generated_drugs]), 3),
            'std_qed': round(np.std([d['qed'] for d in generated_drugs]), 3),
            'validity': round(sum(1 for d in generated_drugs if d['valid']) / len(generated_drugs), 3)
        }
        
        # Calculate property statistics for reference drugs
        ref_stats = {
            'avg_mw': round(np.mean([d['mw'] for d in reference_drugs if d['mw'] < 10000]), 1),
            'avg_qed': round(np.mean([d['qed_score'] for d in reference_drugs]), 3),
            'validity': 1.0  # All FDA drugs are valid
        }
        
        # Compare
        print(f"Generated Drugs:")
        print(f"  Average MW: {gen_stats['avg_mw']:.1f} ± {gen_stats['std_mw']:.1f} Da")
        print(f"  Average QED: {gen_stats['avg_qed']:.3f} ± {gen_stats['std_qed']:.3f}")
        print(f"  Validity: {gen_stats['validity']*100:.1f}%")
        print()
        print(f"FDA Reference Drugs:")
        print(f"  Average MW: {ref_stats['avg_mw']:.1f} Da")
        print(f"  Average QED: {ref_stats['avg_qed']:.3f}")
        print(f"  Validity: {ref_stats['validity']*100:.1f}%")
        print()
        
        # Property match scores
        mw_match = 1 - abs(gen_stats['avg_mw'] - ref_stats['avg_mw']) / max(gen_stats['avg_mw'], ref_stats['avg_mw'])
        qed_match = 1 - abs(gen_stats['avg_qed'] - ref_stats['avg_qed'])
        
        return {
            'generated_stats': gen_stats,
            'reference_stats': ref_stats,
            'property_match': {
                'mw_match': round(mw_match, 3),
                'qed_match': round(qed_match, 3),
                'overall': round((mw_match + qed_match + gen_stats['validity']) / 3, 3)
            }
        }
    
    def analyze_target_overlap(self, generated_drugs, reference_drugs):
        """
        Analyze overlap in biological targets
        """
        print(f"\n{'='*70}")
        print("ANALYZING BIOLOGICAL TARGET OVERLAP")
        print(f"{'='*70}\n")
        
        # Collect all targets from reference drugs
        ref_targets = set()
        for drug in reference_drugs:
            if 'primary_target' in drug and drug['primary_target']:
                ref_targets.add(drug['primary_target'])
            if 'secondary_targets' in drug:
                ref_targets.update(drug['secondary_targets'])
        
        # Collect targets from generated drugs
        gen_targets = Counter()
        for drug in generated_drugs:
            for target in drug['predicted_targets']:
                gen_targets[target] += 1
        
        # Calculate overlap
        overlap = set(gen_targets.keys()).intersection(ref_targets)
        coverage = len(overlap) / len(ref_targets) if ref_targets else 0
        
        print(f"Reference targets: {ref_targets}")
        print(f"Generated targets: {dict(gen_targets)}")
        print(f"Target overlap: {overlap}")
        print(f"Coverage: {coverage*100:.1f}%")
        print()
        
        return {
            'reference_targets': list(ref_targets),
            'generated_targets': dict(gen_targets),
            'overlap': list(overlap),
            'coverage': round(coverage, 3),
            'target_match_score': round(coverage, 3)
        }


def main():
    """Run molecular similarity analysis"""
    
    # Load generated drugs
    with open('models/empirical_test/results/generated_drugs.json', 'r') as f:
        gen_data = json.load(f)
    generated_drugs = gen_data['candidates']
    
    # Load reference drugs
    with open('models/empirical_test/data/fda_approved_drugs.json', 'r') as f:
        ref_data = json.load(f)
    reference_drugs = ref_data['reference_drugs']['drugs']
    
    # Initialize calculator
    calc = MolecularSimilarityCalculator()
    
    # Calculate similarities
    similarity_results = calc.calculate_all_similarities(generated_drugs, reference_drugs)
    
    # Compare properties
    property_results = calc.compare_properties(generated_drugs, reference_drugs)
    
    # Analyze target overlap
    target_results = calc.analyze_target_overlap(generated_drugs, reference_drugs)
    
    # Compile full comparison report
    comparison_report = {
        'test_info': {
            'test_name': 'COVID-19 Molecular Comparison',
            'generated_count': len(generated_drugs),
            'reference_count': len(reference_drugs),
            'similarity_threshold': calc.similarity_threshold
        },
        'similarity_analysis': similarity_results,
        'property_comparison': property_results,
        'target_analysis': target_results,
        'summary': {
            'avg_similarity': similarity_results['avg_similarity'],
            'high_similarity_drugs': similarity_results['high_similarity_count'],
            'property_match_score': property_results['property_match']['overall'],
            'target_coverage': target_results['coverage'],
            'overall_chemical_accuracy': round(
                (similarity_results['avg_similarity'] + 
                 property_results['property_match']['overall'] + 
                 target_results['coverage']) / 3, 3
            )
        }
    }
    
    # Save comparison report
    with open('models/empirical_test/results/comparison_report.json', 'w') as f:
        json.dump(comparison_report, f, indent=2)
    
    print("="*70)
    print("COMPARISON COMPLETE")
    print("="*70)
    print(f"[OK] Results saved to: models/empirical_test/results/comparison_report.json")
    print(f"\nOverall Chemical Accuracy: {comparison_report['summary']['overall_chemical_accuracy']:.1%}")
    print(f"High Similarity Drugs: {similarity_results['high_similarity_count']}/{len(generated_drugs)}")
    print(f"Target Coverage: {target_results['coverage']:.1%}")
    print("="*70)
    
    return comparison_report


if __name__ == "__main__":
    results = main()
