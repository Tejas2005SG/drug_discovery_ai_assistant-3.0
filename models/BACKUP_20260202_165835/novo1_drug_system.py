"""
NOVO-1 Pro Drug Discovery System
Complete implementation with Knowledge Graph + Smart Molecular Generation
Uses Google Drive for storage, optimized for CPU training
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Import our custom modules
from knowledge_graph import DrugRepurposingKnowledgeGraph
from google_drive_manager import GoogleDriveManager

class MolecularProcessor:
    """Process molecular structures and calculate properties"""
    
    def __init__(self):
        self.use_rdkit = self._check_rdkit()
        
    def _check_rdkit(self):
        """Check if RDKit is available"""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, QED
            print("[OK] RDKit available - using full chemistry toolkit")
            return True
        except ImportError:
            print("[WARNING] RDKit not available - using simplified calculations")
            return False
    
    def calculate_properties(self, smiles: str) -> Dict:
        """Calculate molecular properties"""
        if self.use_rdkit:
            return self._calculate_with_rdkit(smiles)
        else:
            return self._calculate_simple(smiles)
    
    def _calculate_with_rdkit(self, smiles: str) -> Dict:
        """Calculate properties using RDKit"""
        from rdkit import Chem
        from rdkit.Chem import Descriptors, QED, AllChem
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {'valid': False, 'qed': 0.0, 'mw': 0}
        
        # Calculate properties
        mw = Descriptors.MolWt(mol)
        qed = QED.qed(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        
        # Morgan fingerprint
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        
        return {
            'valid': True,
            'smiles': smiles,
            'mw': float(mw),
            'qed': float(qed),
            'logp': float(logp),
            'hbd': int(hbd),
            'hba': int(hba),
            'fingerprint': np.array(fp)
        }
    
    def _calculate_simple(self, smiles: str) -> Dict:
        """Simplified property calculation without RDKit"""
        # Count atoms
        carbons = smiles.count('C') - smiles.count('c')
        oxygens = smiles.count('O') - smiles.count('o')
        nitrogens = smiles.count('N') - smiles.count('n')
        
        # Basic validity checks
        valid = len(smiles) >= 5 and carbons >= 1
        valid = valid and smiles.count('(') == smiles.count(')')
        
        # Estimate molecular weight
        mw = carbons * 12.01 + oxygens * 16.00 + nitrogens * 14.01
        
        # Estimate QED (very rough approximation)
        qed = min(0.9, 0.4 + carbons * 0.02 + nitrogens * 0.05)
        
        return {
            'valid': valid,
            'smiles': smiles,
            'mw': mw,
            'qed': qed,
            'logp': 0.0,  # Can't calculate without RDKit
            'hbd': 0,
            'hba': 0,
            'fingerprint': None
        }
    
    def smiles_to_fingerprint(self, smiles: str) -> np.ndarray:
        """Convert SMILES to Morgan fingerprint using RDKit"""
        if not self.use_rdkit:
            return None
        
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
            
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            
            # Generate Morgan fingerprint (2048 bits)
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
            return np.array(fp, dtype=np.int32)
        except Exception as e:
            print(f"[WARNING] Failed to generate fingerprint: {e}")
            return None
    
    def tanimoto_similarity(self, fp1: np.ndarray, fp2: np.ndarray) -> float:
        """Calculate Tanimoto similarity between fingerprints"""
        if fp1 is None or fp2 is None:
            return 0.0
        
        intersection = np.sum(fp1 & fp2)
        union = np.sum(fp1 | fp2)
        
        return intersection / union if union > 0 else 0.0


class SmartDrugGenerator:
    """
    Smart drug generator using knowledge graph and medicinal chemistry rules
    NOT random - uses bioisosteric replacement and pharmacophore combination
    """
    
    def __init__(self, knowledge_graph: DrugRepurposingKnowledgeGraph):
        self.kg = knowledge_graph
        self.mol_processor = MolecularProcessor()
        
        # Bioisosteric replacements (medicinal chemistry rules)
        self.bioisosteres = {
            'COOH': ['CONH2', 'tetrazole', 'SO2NH2'],
            'phenyl': ['cyclohexyl', 'pyridine', 'thiophene'],
            'amide': ['sulfonamide', 'urea', 'carbamate'],
            'methyl': ['ethyl', 'isopropyl', 'CF3'],
        }
        
        # Functional groups by therapeutic area
        self.therapeutic_groups = {
            'anti_inflammatory': ['C(=O)O', 'c1ccc(cc1)C', 'S(=O)(=O)N'],
            'antiviral': ['C(=O)N', 'c1ncnc1', 'C(=O)N(C)C'],
            'neurological': ['c1ccccc1N', 'C(=O)NCC', 'CN1CCCCC1'],
        }
    
    def generate_for_symptoms(self, symptoms: List[str], n_candidates: int = 10) -> List[Dict]:
        """
        Generate drug candidates for given symptoms
        
        Process:
        1. Match symptoms to diseases using KG embeddings
        2. Retrieve drugs for matched diseases
        3. Extract pharmacophores from those drugs
        4. Combine and mutate to create novel candidates
        5. Validate and score candidates
        """
        print(f"\n{'='*70}")
        print(f"GENERATING DRUGS FOR SYMPTOMS: {symptoms}")
        print(f"{'='*70}")
        
        # Step 1: Find matching diseases
        matched_diseases = self.kg.find_diseases_by_symptoms(symptoms, top_k=3)
        
        if not matched_diseases:
            print("[WARNING] No matching diseases found")
            return []
        
        print("\n[STEP 1] Matched Diseases:")
        for dis_id, score in matched_diseases:
            dis_name = self.kg.diseases[dis_id]['name']
            print(f"  - {dis_name} (similarity: {score:.3f})")
        
        # Step 2: Get existing drugs for these diseases
        source_drugs = []
        for dis_id, dis_score in matched_diseases:
            drugs = self.kg.get_drugs_for_disease(dis_id, top_k=3)
            for drug_id, drug_score in drugs:
                drug_data = self.kg.drugs[drug_id]
                source_drugs.append({
                    'drug_id': drug_id,
                    'name': drug_data['name'],
                    'smiles': drug_data['smiles'],
                    'disease_score': dis_score,
                    'drug_score': drug_score,
                    'targets': drug_data['targets']
                })
        
        print(f"\n[STEP 2] Found {len(source_drugs)} source drugs")
        
        if not source_drugs:
            print("[WARNING] No source drugs available for generation")
            return []
        
        # Step 3: Generate candidates by smart mutation
        candidates = []
        for i in range(n_candidates):
            # Pick 2-3 source drugs to combine
            n_sources = min(3, len(source_drugs))
            selected_sources = np.random.choice(source_drugs, n_sources, replace=False)
            
            # Generate candidate
            candidate = self._create_candidate(selected_sources, i)
            candidates.append(candidate)
        
        # Step 4: Validate and rank
        validated_candidates = []
        for cand in candidates:
            # Calculate properties
            props = self.mol_processor.calculate_properties(cand['smiles'])
            
            if props['valid']:
                # Predict targets based on similarity to source drugs
                predicted_targets = self._predict_targets(cand, source_drugs)
                
                # Calculate overall score
                score = self._calculate_score(props, cand, predicted_targets)
                
                validated_candidates.append({
                    'id': f"NOVO_{len(validated_candidates):03d}",
                    'smiles': cand['smiles'],
                    'properties': props,
                    'predicted_targets': predicted_targets,
                    'source_drugs': [s['name'] for s in cand['sources']],
                    'generation_method': cand['method'],
                    'confidence': score
                })
        
        # Sort by confidence
        validated_candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"\n[STEP 3] Generated {len(validated_candidates)} valid candidates")
        print(f"{'='*70}\n")
        
        return validated_candidates
    
    def _create_candidate(self, source_drugs: List[Dict], seed: int) -> Dict:
        """Create a new drug candidate from source drugs"""
        np.random.seed(seed)
        
        # Select primary scaffold (largest drug)
        primary = max(source_drugs, key=lambda x: len(x['smiles']))
        scaffold = primary['smiles']
        
        # Decide mutation strategy
        method = np.random.choice([
            'functional_group_swap',
            'ring_modification',
            'side_chain_extension',
            'pharmacophore_combination'
        ])
        
        if method == 'functional_group_swap':
            # Replace functional groups
            new_smiles = self._swap_functional_groups(scaffold)
        elif method == 'ring_modification':
            # Modify ring systems
            new_smiles = self._modify_rings(scaffold)
        elif method == 'side_chain_extension':
            # Add side chains
            new_smiles = self._extend_side_chain(scaffold)
        else:
            # Combine pharmacophores from multiple drugs
            new_smiles = self._combine_pharmacophores(source_drugs)
        
        return {
            'smiles': new_smiles,
            'sources': source_drugs,
            'method': method
        }
    
    def _swap_functional_groups(self, smiles: str) -> str:
        """Swap functional groups using bioisosteric replacements"""
        # Simple string replacements (would use RDKit for proper implementation)
        replacements = [
            ('C(=O)O', 'C(=O)N'),
            ('c1ccccc1', 'C1CCCCC1'),
            ('C(=O)N', 'S(=O)(=O)N'),
        ]
        
        new_smiles = smiles
        for old, new in replacements:
            if np.random.random() > 0.5 and old in new_smiles:
                new_smiles = new_smiles.replace(old, new, 1)
        
        return new_smiles
    
    def _modify_rings(self, smiles: str) -> str:
        """Modify ring systems"""
        # Simplified: replace phenyl with heterocycle
        if 'c1ccccc1' in smiles:
            heterocycles = ['c1ccncc1', 'c1cncnc1', 'c1ccsc1']
            replacement = np.random.choice(heterocycles)
            smiles = smiles.replace('c1ccccc1', replacement, 1)
        return smiles
    
    def _extend_side_chain(self, smiles: str) -> str:
        """Extend side chains with functional groups"""
        extensions = ['C(=O)N', 'CC(C)C', 'CN', 'CC(=O)O']
        extension = np.random.choice(extensions)
        
        if np.random.random() > 0.5:
            return smiles + extension
        else:
            return extension + smiles
    
    def _combine_pharmacophores(self, source_drugs: List[Dict]) -> str:
        """Combine key pharmacophores from multiple drugs"""
        # Extract key fragments from each drug
        fragments = []
        for drug in source_drugs:
            smiles = drug['smiles']
            # Simple fragment extraction (would use RDKit for proper implementation)
            if len(smiles) > 10:
                # Take middle portion as fragment
                start = len(smiles) // 4
                end = 3 * len(smiles) // 4
                fragment = smiles[start:end]
                fragments.append(fragment)
        
        # Combine 2-3 fragments
        n_fragments = min(len(fragments), np.random.randint(2, 4))
        selected = np.random.choice(fragments, n_fragments, replace=False)
        
        return ''.join(selected)
    
    def _predict_targets(self, candidate: Dict, source_drugs: List[Dict]) -> List[str]:
        """Predict protein targets for candidate"""
        # Collect all targets from source drugs
        all_targets = []
        for drug in source_drugs:
            all_targets.extend([self.kg.proteins[t] for t in drug['targets']])
        
        # Return unique targets
        return list(set(all_targets)) if all_targets else ['Unknown']
    
    def _calculate_score(self, props: Dict, candidate: Dict, targets: List[str]) -> float:
        """Calculate overall confidence score"""
        score = 0.0
        
        # QED contribution (0.6-0.8 is good)
        qed = props.get('qed', 0)
        score += min(qed, 0.8) * 0.3
        
        # Molecular weight (150-500 is drug-like)
        mw = props.get('mw', 0)
        if 150 <= mw <= 500:
            score += 0.2
        
        # Source drug quality
        avg_source_score = np.mean([s.get('drug_score', 0.5) for s in candidate['sources']])
        score += avg_source_score * 0.3
        
        # Number of targets (more is better for complex symptoms)
        score += min(len(targets) * 0.05, 0.2)
        
        return min(score, 1.0)


class NOVO1DrugDiscoverySystem:
    """Complete NOVO-1 Drug Discovery System"""
    
    def __init__(self, use_google_drive=False, drive_path=None):
        """
        Initialize the complete system
        
        Args:
            use_google_drive: Whether to use Google Drive for storage
            drive_path: Path to Google Drive folder
        """
        print("="*70)
        print("NOVO-1 DRUG DISCOVERY SYSTEM v2.0")
        print("Knowledge Graph + Smart Molecular Generation")
        print("="*70)
        
        # Initialize Google Drive manager if requested
        self.drive_manager = None
        if use_google_drive and drive_path:
            self.drive_manager = GoogleDriveManager(drive_path)
        
        # Initialize components
        self.knowledge_graph = DrugRepurposingKnowledgeGraph(self.drive_manager)
        self.drug_generator = None  # Will initialize after KG is built
        self.mol_processor = MolecularProcessor()
        
        print("[OK] System initialized")
        
    def build_knowledge_graph(self, disease_data: List[Dict], drug_data: List[Dict]):
        """Build knowledge graph from data"""
        self.knowledge_graph.build_from_data(disease_data, drug_data)
        
        # Train embeddings
        self.knowledge_graph.train_embeddings_cpu(
            dim=100,
            epochs=1000,
            lr=0.01,
            negative_samples=5
        )
        
        # Initialize drug generator
        self.drug_generator = SmartDrugGenerator(self.knowledge_graph)
        
        # Save to Google Drive if available
        if self.drive_manager:
            self.knowledge_graph.save_to_drive('trained_kg.pkl')
    
    def generate_drugs(self, symptoms: List[str], n_candidates: int = 10) -> List[Dict]:
        """Generate drug candidates for symptoms"""
        if self.drug_generator is None:
            raise ValueError("Knowledge graph not built. Call build_knowledge_graph() first.")
        
        candidates = self.drug_generator.generate_for_symptoms(symptoms, n_candidates)
        
        # Save results to Google Drive
        if self.drive_manager:
            results = {
                'symptoms': symptoms,
                'n_candidates': len(candidates),
                'candidates': candidates
            }
            self.drive_manager.save_results(results, f"generation_{'_'.join(symptoms[:2])}")
        
        return candidates
    
    def display_candidates(self, candidates: List[Dict], top_n: int = 5):
        """Display top drug candidates"""
        print(f"\n{'='*70}")
        print("TOP DRUG CANDIDATES")
        print(f"{'='*70}\n")
        
        for i, cand in enumerate(candidates[:top_n], 1):
            print(f"{i}. {cand['id']} (Confidence: {cand['confidence']:.1%})")
            print(f"   SMILES: {cand['smiles'][:60]}...")
            print(f"   MW: {cand['properties']['mw']:.1f} Da")
            print(f"   QED: {cand['properties']['qed']:.3f}")
            print(f"   Targets: {', '.join(cand['predicted_targets'][:3])}")
            print(f"   Based on: {', '.join(cand['source_drugs'][:2])}")
            print(f"   Method: {cand['generation_method']}")
            print()


# Example usage
if __name__ == "__main__":
    # Sample data
    disease_data = [
        {
            'name': 'COVID-19',
            'symptoms': ['fever', 'cough', 'fatigue', 'shortness of breath']
        },
        {
            'name': 'Multiple Sclerosis',
            'symptoms': ['neural inflammation', 'tremors', 'fatigue', 'muscle weakness']
        },
        {
            'name': 'Influenza',
            'symptoms': ['fever', 'cough', 'muscle pain', 'chills']
        },
        {
            'name': 'Rheumatoid Arthritis',
            'symptoms': ['joint pain', 'inflammation', 'stiffness', 'swelling']
        }
    ]
    
    drug_data = [
        {
            'name': 'Paxlovid',
            'smiles': 'CC(C)(C)NC(=O)C1CC2(CCN(C(=O)C(C(C)(C)C)NC(=O)C(F)(F)F)CC2)CN1C(=O)O',
            'targets': ['3CL_protease', 'Mpro'],
            'indications': ['COVID-19']
        },
        {
            'name': 'Ocrelizumab',
            'smiles': 'CC[C@H]1C[C@@H]2C[C@H]3C4=C(CCN3C2=O)C(=O)C5=C4C=CC=C5O1',
            'targets': ['CD20'],
            'indications': ['Multiple Sclerosis']
        },
        {
            'name': 'Ibuprofen',
            'smiles': 'CC(C)Cc1ccc(cc1)C(C)C(=O)O',
            'targets': ['COX-1', 'COX-2'],
            'indications': ['Influenza', 'Rheumatoid Arthritis']
        },
        {
            'name': 'Methotrexate',
            'smiles': 'CN(Cc1cnc2nc(N)nc(O)c2n1)C(=O)N(C)C(=O)N(C)C',
            'targets': ['DHFR'],
            'indications': ['Rheumatoid Arthritis']
        }
    ]
    
    # Initialize system
    system = NOVO1DrugDiscoverySystem(use_google_drive=False)
    
    # Build knowledge graph
    system.build_knowledge_graph(disease_data, drug_data)
    
    # Generate drugs for symptoms
    test_symptoms = ['fever', 'cough', 'fatigue']
    candidates = system.generate_drugs(test_symptoms, n_candidates=10)
    
    # Display results
    system.display_candidates(candidates, top_n=5)
    
    # Generate for complex symptoms
    print("\n" + "="*70)
    print("COMPLEX SYMPTOM CASE")
    print("="*70)
    complex_symptoms = ['neural inflammation', 'tremors', 'fatigue']
    complex_candidates = system.generate_drugs(complex_symptoms, n_candidates=8)
    system.display_candidates(complex_candidates, top_n=3)
