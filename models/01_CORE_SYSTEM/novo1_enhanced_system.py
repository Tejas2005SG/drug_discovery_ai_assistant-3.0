"""
NOVO-1 Pro Drug Discovery System - ENHANCED VERSION v3.0
Complete implementation with:
- Target Protein Information (First & Last)
- Comprehensive ADMET Predictions
- All Chemical Properties
- Detailed Protein Metadata

Uses Knowledge Graph + Smart Molecular Generation
Optimized for CPU training, Google Drive storage
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import sys
from datetime import datetime

# Import custom modules
from knowledge_graph import DrugRepurposingKnowledgeGraph
from google_drive_manager import GoogleDriveManager
from protein_database import ProteinDatabase
from admet_predictor import ADMETPredictor, ADMETProperties

class EnhancedMolecularProcessor:
    """Enhanced molecular processor with all chemical properties"""
    
    def __init__(self):
        self.use_rdkit = self._check_rdkit()
        
    def _check_rdkit(self):
        """Check if RDKit is available"""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, QED, Crippen, Lipinski, rdMolDescriptors, GraphDescriptors
            print("[OK] RDKit available - using full chemistry toolkit with all descriptors")
            return True
        except ImportError:
            print("[WARNING] RDKit not available - using simplified calculations")
            return False
    
    def calculate_all_properties(self, smiles: str) -> Dict:
        """Calculate ALL molecular and chemical properties"""
        if self.use_rdkit:
            return self._calculate_comprehensive_with_rdkit(smiles)
        else:
            return self._calculate_simple(smiles)
    
    def _calculate_comprehensive_with_rdkit(self, smiles: str) -> Dict:
        """Calculate comprehensive properties using RDKit"""
        from rdkit import Chem
        from rdkit.Chem import Descriptors, QED, Crippen, Lipinski, rdMolDescriptors, GraphDescriptors, Fragments, AllChem
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {'valid': False, 'error': 'Invalid SMILES'}
        
        # Basic molecular properties
        basic_props = {
            'valid': True,
            'smiles': smiles,
            'molecular_formula': rdMolDescriptors.CalcMolFormula(mol),
            'molecular_weight': float(Descriptors.MolWt(mol)),
            'exact_mass': float(rdMolDescriptors.CalcExactMolWt(mol)),
            'qed': float(QED.qed(mol)),
        }
        
        # Calculate values once
        hbd_count = int(Lipinski.NumHDonors(mol))
        hba_count = int(Lipinski.NumHAcceptors(mol))
        
        # Count atoms by element for ADMET
        nitrogen_count = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 7)
        
        # Physicochemical properties (flattened for ADMET compatibility)
        physicochemical = {
            'mw': float(Descriptors.MolWt(mol)),  # Molecular weight (for ADMET)
            'nitrogens': nitrogen_count,  # For ADMET toxicity prediction
            'molecular_weight': float(Descriptors.MolWt(mol)),  # Full name
            'logp': float(Crippen.MolLogP(mol)),
            'tpsa': float(rdMolDescriptors.CalcTPSA(mol)),
            'molar_refractivity': float(Crippen.MolMR(mol)),
            'fraction_csp3': float(Lipinski.FractionCSP3(mol)),
            'num_heavy_atoms': int(Lipinski.HeavyAtomCount(mol)),
            'num_atoms': int(mol.GetNumAtoms()),
            'num_bonds': int(mol.GetNumBonds()),
            # ADMET-compatible aliases
            'hbd': hbd_count,
            'hba': hba_count,
        }
        
        # Hydrogen bonding (detailed)
        h_bonding = {
            'num_hbd': hbd_count,
            'num_hba': hba_count,
            'hbd_hba_sum': hbd_count + hba_count,
        }
        
        # Structural properties
        rings_count = int(Lipinski.RingCount(mol))
        aromatic_rings_count = int(Lipinski.NumAromaticRings(mol))
        rotatable_bonds_count = int(Lipinski.NumRotatableBonds(mol))
        
        structural = {
            'num_rotatable_bonds': rotatable_bonds_count,
            'num_rings': rings_count,
            'num_aromatic_rings': aromatic_rings_count,
            'num_aliphatic_rings': int(Lipinski.NumAliphaticRings(mol)),
            'num_saturated_rings': int(Lipinski.NumSaturatedRings(mol)),
            'num_heterocycles': int(Lipinski.NumHeterocycles(mol)),
            'num_aromatic_heterocycles': int(Lipinski.NumAromaticHeterocycles(mol)),
            'num_aliphatic_heterocycles': int(Lipinski.NumAliphaticHeterocycles(mol)),
            # ADMET-compatible aliases
            'aromatic_rings': aromatic_rings_count,
            'rings': rings_count,
            'rotb': rotatable_bonds_count,
        }
        
        # Functional group counts
        functional_groups = {
            'num_aliphatic_carbocycles': int(Lipinski.NumAliphaticCarbocycles(mol)),
            'num_aromatic_carbocycles': int(Lipinski.NumAromaticCarbocycles(mol)),
            'num_saturated_carbocycles': int(Lipinski.NumSaturatedCarbocycles(mol)),
            'num_amide_bonds': int(Lipinski.NumAmideBonds(mol)),
            'num_het_atoms': int(Lipinski.NumHeteroatoms(mol)),
        }
        
        # Lipinski's Rule of Five
        mw = basic_props['molecular_weight']
        lipinski = {
            'mw_violation': mw > 500,
            'logp_violation': physicochemical['logp'] > 5,
            'hbd_violation': h_bonding['num_hbd'] > 5,
            'hba_violation': h_bonding['num_hba'] > 10,
            'num_violations': sum([
                mw > 500,
                physicochemical['logp'] > 5,
                h_bonding['num_hbd'] > 5,
                h_bonding['num_hba'] > 10
            ]),
            'passes_lipinski': sum([
                mw > 500,
                physicochemical['logp'] > 5,
                h_bonding['num_hbd'] > 5,
                h_bonding['num_hba'] > 10
            ]) <= 1
        }
        
        # Topological descriptors
        topological = {
            'balaban_j': float(GraphDescriptors.BalabanJ(mol)) if hasattr(GraphDescriptors, 'BalabanJ') else 0.0,
            'bertz_ct': float(GraphDescriptors.BertzCT(mol)) if hasattr(GraphDescriptors, 'BertzCT') else 0.0,
            'hall_kier_alpha': float(GraphDescriptors.HallKierAlpha(mol)) if hasattr(GraphDescriptors, 'HallKierAlpha') else 0.0,
            'kappa1': float(GraphDescriptors.Kappa1(mol)) if hasattr(GraphDescriptors, 'Kappa1') else 0.0,
            'kappa2': float(GraphDescriptors.Kappa2(mol)) if hasattr(GraphDescriptors, 'Kappa2') else 0.0,
            'kappa3': float(GraphDescriptors.Kappa3(mol)) if hasattr(GraphDescriptors, 'Kappa3') else 0.0,
        }
        
        # Morgan fingerprint
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        fingerprint = {
            'morgan_fp_2048': np.array(fp, dtype=np.int32).tolist(),
            'fingerprint_density': float(np.sum(fp) / 2048),
        }
        
        # Constitutional descriptors
        constitutional = {
            'formal_charge': int(Chem.GetFormalCharge(mol)),
            'num_radical_electrons': int(Descriptors.NumRadicalElectrons(mol)),
            'num_valence_electrons': int(Descriptors.NumValenceElectrons(mol)),
        }
        
        # Electrotopological state
        try:
            estate = {
                'max_estate': float(Descriptors.MaxEStateIndex(mol)),
                'min_estate': float(Descriptors.MinEStateIndex(mol)),
                'max_abs_estate': float(Descriptors.MaxAbsEStateIndex(mol)),
                'min_abs_estate': float(Descriptors.MinAbsEStateIndex(mol)),
            }
        except:
            estate = {'max_estate': 0.0, 'min_estate': 0.0, 'max_abs_estate': 0.0, 'min_abs_estate': 0.0}
        
        # Molecular complexity
        complexity = {
            'mol_complexity': float(Descriptors.MolLogP(mol)) * structural['num_rings'],
            'stereo_centers': int(Descriptors.NumStereocenters(mol)) if hasattr(Descriptors, 'NumStereocenters') else 0,
        }
        
        return {
            **basic_props,
            'physicochemical': physicochemical,
            'hydrogen_bonding': h_bonding,
            'structural': structural,
            'functional_groups': functional_groups,
            'lipinski_rules': lipinski,
            'topological': topological,
            'fingerprint': fingerprint,
            'constitutional': constitutional,
            'electrotopological': estate,
            'complexity': complexity
        }
    
    def _calculate_simple(self, smiles: str) -> Dict:
        """Simplified property calculation without RDKit"""
        # Count atoms
        carbons = smiles.count('C') - smiles.count('c')
        oxygens = smiles.count('O') - smiles.count('o')
        nitrogens = smiles.count('N') - smiles.count('n')
        sulfurs = smiles.count('S') - smiles.count('s')
        halogens = smiles.count('F') + smiles.count('Cl') + smiles.count('Br') + smiles.count('I')
        
        # Basic validity
        valid = len(smiles) >= 5 and carbons >= 1
        valid = valid and smiles.count('(') == smiles.count(')')
        
        # Estimate MW
        mw = carbons * 12.01 + oxygens * 16.00 + nitrogens * 14.01 + sulfurs * 32.06 + halogens * 19.00
        
        return {
            'valid': valid,
            'smiles': smiles,
            'molecular_weight': mw,
            'qed': min(0.9, 0.4 + carbons * 0.02),
            'physicochemical': {'logp': 0.0, 'tpsa': 40.0},
            'hydrogen_bonding': {'num_hbd': 0, 'num_hba': 0},
            'structural': {'num_rotatable_bonds': 0, 'num_rings': 0},
            'lipinski_rules': {'num_violations': 0, 'passes_lipinski': True},
            'fingerprint': {'morgan_fp_2048': None}
        }


class EnhancedDrugGenerator:
    """Enhanced drug generator with protein targeting and ADMET predictions"""
    
    def __init__(self, knowledge_graph: DrugRepurposingKnowledgeGraph, protein_db: ProteinDatabase):
        self.kg = knowledge_graph
        self.protein_db = protein_db
        self.mol_processor = EnhancedMolecularProcessor()
        self.admet_predictor = ADMETPredictor()
        
        # Bioisosteric replacements
        self.bioisosteres = {
            'COOH': ['CONH2', 'tetrazole', 'SO2NH2'],
            'phenyl': ['cyclohexyl', 'pyridine', 'thiophene'],
            'amide': ['sulfonamide', 'urea', 'carbamate'],
            'methyl': ['ethyl', 'isopropyl', 'CF3'],
        }
    
    def identify_target_proteins(self, symptoms: List[str], top_k: int = 5) -> Dict:
        """
        FIRST STEP: Identify target proteins based on symptoms
        
        Returns:
            Dictionary with matched diseases and their associated proteins
        """
        print(f"\n{'='*70}")
        print("STEP 1: TARGET PROTEIN IDENTIFICATION")
        print(f"{'='*70}")
        print(f"\nInput Symptoms: {symptoms}")
        
        # Find matching diseases
        matched_diseases = self.kg.find_diseases_by_symptoms(symptoms, top_k=3)
        
        if not matched_diseases:
            print("[WARNING] No matching diseases found in knowledge graph")
            print("[INFO] Creating synthetic target proteins for novel symptom pattern...")
            
            # Create synthetic target proteins based on symptom categories
            synthetic_targets = []
            symptom_categories = {
                'inflammation': ['Cyclooxygenase', 'Interleukin receptors', 'TNF-alpha'],
                'pain': ['Opioid receptors', 'COX-2', 'TRPV1'],
                'fever': ['Prostaglandin E2 receptors', 'IL-1 beta'],
                'infection': ['Beta-lactamases', 'DNA gyrase', 'Reverse transcriptase'],
                'cancer': ['EGFR', 'VEGFR', 'BCR-ABL', 'HER2'],
                'cardiovascular': ['ACE', 'Beta-adrenergic receptors', 'Calcium channels'],
                'neurological': ['GABA receptors', 'Dopamine receptors', 'Serotonin receptors'],
                'metabolic': ['PPAR-gamma', 'DPP-4', 'SGLT2'],
                'autoimmune': ['TNF-alpha', 'IL-6 receptor', 'B-cell receptors'],
                'respiratory': ['Beta-2 agonists', 'Muscarinic receptors', 'Leukotriene receptors']
            }
            
            # Analyze symptoms for keywords
            detected_categories = set()
            for symptom in symptoms:
                symptom_lower = symptom.lower()
                for category, proteins in symptom_categories.items():
                    if any(keyword in symptom_lower for keyword in category.split()):
                        detected_categories.add(category)
            
            # If no categories detected, use universal targets
            if not detected_categories:
                detected_categories = ['universal']
                print(f"[INFO] No specific categories detected. Using universal protein targets.")
            
            # Create synthetic target proteins
            for category in detected_categories:
                proteins = symptom_categories.get(category, ['Universal Drug Target'])
                for i, protein in enumerate(proteins):
                    synthetic_target = {
                        'protein_name': f"NOVEL_TARGET_{category.upper()}_{i+1}",
                        'info': {
                            'uniprot_id': f'SYNTH_{hash(protein) % 100000:05d}',
                            'gene_name': f'{protein.replace(" ", "_")}_GENE',
                            'full_name': f'Synthetic target for {protein}',
                            'protein_family': category.upper(),
                            'organism': 'Homo sapiens',
                            'function': f'Predicted role in {category} pathways',
                            'pathways': [f'{category}_signaling', 'cellular_response'],
                            'therapeutic_area': category.capitalize(),
                            'disease_relevance': symptoms[:3],
                            'druggability': 'Medium',
                            'clinical_significance': 'Novel target for unexplored symptom pattern',
                            'literature_count': 0,
                            'known_inhibitors': []
                        },
                        'associated_diseases': ['Novel Condition'],
                        'source_drugs': [],
                        'relevance_score': 0.7
                    }
                    synthetic_targets.append(synthetic_target)
            
            print(f"[OK] Created {len(synthetic_targets)} synthetic target proteins for categories: {', '.join(detected_categories)}")
            
            # Return with synthetic targets
            return {
                'target_proteins': synthetic_targets[:top_k],
                'matched_diseases': [{
                    'disease': 'Novel/Unmatched Condition',
                    'match_score': 0.5,
                    'associated_proteins': [t['protein_name'] for t in synthetic_targets[:5]]
                }],
                'total_proteins_found': len(synthetic_targets),
                'is_novel_symptom_pattern': True
            }
        
        # Collect all proteins from matched diseases
        target_proteins = {}
        disease_info = []
        
        print("\n[Matched Diseases & Associated Proteins]")
        for dis_id, score in matched_diseases:
            dis_name = self.kg.diseases[dis_id]['name']
            disease_proteins = set()
            
            # Get drugs for this disease
            drugs = self.kg.get_drugs_for_disease(dis_id, top_k=5)
            
            for drug_id, drug_score in drugs:
                drug_data = self.kg.drugs[drug_id]
                for protein_id in drug_data['targets']:
                    protein_name = self.kg.proteins.get(protein_id, protein_id)
                    disease_proteins.add(protein_name)
                    
                    # Get detailed protein info
                    protein_info = self.protein_db.get_protein_info(protein_name)
                    if protein_name not in target_proteins:
                        target_proteins[protein_name] = {
                            'protein_name': protein_name,
                            'info': protein_info,
                            'associated_diseases': [dis_name],
                            'source_drugs': [drug_data['name']],
                            'relevance_score': score * drug_score
                        }
                    else:
                        if dis_name not in target_proteins[protein_name]['associated_diseases']:
                            target_proteins[protein_name]['associated_diseases'].append(dis_name)
                        if drug_data['name'] not in target_proteins[protein_name]['source_drugs']:
                            target_proteins[protein_name]['source_drugs'].append(drug_data['name'])
                        target_proteins[protein_name]['relevance_score'] += score * drug_score
            
            disease_info.append({
                'disease': dis_name,
                'match_score': score,
                'associated_proteins': list(disease_proteins)
            })
            
            print(f"\n  Disease: {dis_name} (Match Score: {score:.3f})")
            print(f"    Associated Proteins ({len(disease_proteins)}):")
            for prot in list(disease_proteins)[:5]:
                prot_info = self.protein_db.get_protein_info(prot)
                print(f"      * {prot}")
                print(f"        UniProt: {prot_info.get('uniprot_id', 'N/A')}")
                print(f"        Family: {prot_info.get('protein_family', 'N/A')}")
                print(f"        Druggability: {prot_info.get('druggability', 'Unknown')}")
        
        # Sort target proteins by relevance score
        sorted_targets = sorted(
            target_proteins.values(),
            key=lambda x: x['relevance_score'],
            reverse=True
        )[:top_k]
        
        print(f"\n{'='*70}")
        print("PRIORITY TARGET PROTEINS (Ranked by Relevance)")
        print(f"{'='*70}")
        
        for i, target in enumerate(sorted_targets, 1):
            info = target['info']
            print(f"\n{i}. {target['protein_name']}")
            print(f"   UniProt ID: {info.get('uniprot_id', 'N/A')}")
            print(f"   Gene: {info.get('gene_name', 'N/A')}")
            print(f"   Full Name: {info.get('full_name', 'N/A')}")
            print(f"   Protein Family: {info.get('protein_family', 'N/A')}")
            print(f"   Organism: {info.get('organism', 'N/A')}")
            print(f"   Function: {info.get('function', 'N/A')[:80]}...")
            print(f"   Pathways: {', '.join(info.get('pathways', [])[:3])}")
            print(f"   Therapeutic Area: {info.get('therapeutic_area', 'N/A')}")
            print(f"   Disease Relevance: {', '.join(info.get('disease_relevance', [])[:3])}")
            print(f"   Druggability: {info.get('druggability', 'Unknown')}")
            print(f"   Clinical Significance: {info.get('clinical_significance', 'N/A')[:80]}...")
            print(f"   Literature Count: {info.get('literature_count', 0)}")
            print(f"   Known Inhibitors: {', '.join(info.get('known_inhibitors', [])[:5])}")
            print(f"   Relevance Score: {target['relevance_score']:.3f}")
        
        return {
            'target_proteins': sorted_targets,
            'matched_diseases': disease_info,
            'total_proteins_found': len(target_proteins)
        }
    
    def generate_candidates(self, symptoms: List[str], n_candidates: int = 10) -> Dict:
        """
        SECOND STEP: Generate drug candidates targeting the identified proteins
        
        Returns:
            Dictionary with target proteins and generated candidates
        """
        # Step 1: Identify target proteins
        target_data = self.identify_target_proteins(symptoms)
        
        print(f"\n{'='*70}")
        print("STEP 2: DRUG CANDIDATE GENERATION")
        print(f"{'='*70}")
        print(f"\nGenerating {n_candidates} candidates targeting {len(target_data['target_proteins'])} proteins...")
        
        # Get source drugs for generation
        source_drugs = []
        for target in target_data['target_proteins']:
            for drug_name in target['source_drugs'][:2]:
                # Find drug in knowledge graph
                for drug_id, drug_data in self.kg.drugs.items():
                    if drug_data['name'] == drug_name:
                        source_drugs.append({
                            'drug_id': drug_id,
                            'name': drug_data['name'],
                            'smiles': drug_data['smiles'],
                            'targets': drug_data['targets'],
                            'score': target['relevance_score']
                        })
                        break
        
        if not source_drugs:
            print("[INFO] No source drugs from matched diseases. Using universal fallback...")
            print(f"[INFO] Knowledge graph contains {len(self.kg.drugs)} total drugs")
            
            # Get all available drugs with valid SMILES
            available_drugs = []
            invalid_count = 0
            
            for drug_id, drug_data in self.kg.drugs.items():
                smiles = drug_data.get('smiles', '')
                # Only check for valid SMILES string (minimum length, not empty)
                if smiles and len(smiles) > 5:
                    available_drugs.append({
                        'drug_id': drug_id,
                        'name': drug_data.get('name', drug_id),
                        'smiles': smiles,
                        'targets': drug_data.get('targets', ['Universal_Target']),
                        'score': 0.5  # Default score for fallback drugs
                    })
                else:
                    invalid_count += 1
            
            print(f"[INFO] Found {len(available_drugs)} drugs with valid SMILES ({invalid_count} drugs had invalid/missing SMILES)")
            
            # Take up to 10 random drugs for diversity
            if available_drugs:
                import random
                # Use more drugs if available for better diversity
                n_fallback = min(10, len(available_drugs))
                source_drugs = random.sample(available_drugs, n_fallback)
                print(f"[OK] Selected {len(source_drugs)} fallback drugs for candidate generation")
                print(f"[INFO] Fallback drugs: {', '.join([d['name'] for d in source_drugs[:5]])}{'...' if len(source_drugs) > 5 else ''}")
            else:
                print("[ERROR] No valid drugs available in database. Cannot generate candidates.")
                print("[SUGGESTION] Please check that drug data was loaded correctly into the knowledge graph.")
                return {**target_data, 'candidates': [], 'error': 'No valid drugs available'}
        
        # Generate candidates
        candidates = []
        for i in range(n_candidates):
            # Pick source drugs
            n_sources = min(3, len(source_drugs))
            selected_sources = np.random.choice(source_drugs, n_sources, replace=False)
            
            # Generate candidate
            candidate = self._create_candidate(selected_sources, i)
            
            # Calculate comprehensive properties
            all_props = self.mol_processor.calculate_all_properties(candidate['smiles'])
            
            if all_props['valid']:
                # Merge all property sub-dicts for ADMET prediction
                merged_props = {
                    **all_props['physicochemical'],
                    **all_props['structural'],
                    **all_props['functional_groups'],
                    **all_props['hydrogen_bonding']
                }
                
                # Predict ADMET properties
                admet = self.admet_predictor.predict_admet(candidate['smiles'], merged_props)
                
                # Predict targets
                predicted_targets = self._predict_targets(candidate, selected_sources)
                
                # Calculate confidence score
                confidence = self._calculate_enhanced_score(all_props, admet, predicted_targets)
                
                candidates.append({
                    'id': f"NOVO_{len(candidates)+1:03d}",
                    'smiles': candidate['smiles'],
                    'molecular_formula': all_props.get('molecular_formula', 'Unknown'),
                    'all_properties': all_props,
                    'admet_properties': admet.to_dict(),
                    'predicted_targets': predicted_targets,
                    'target_proteins': [self.kg.proteins.get(t, t) for t in predicted_targets],
                    'source_drugs': [s['name'] for s in candidate['sources']],
                    'generation_method': candidate['method'],
                    'confidence_score': confidence,
                    'drug_likeness': all_props.get('qed', 0),
                    'passes_lipinski': all_props.get('lipinski_rules', {}).get('passes_lipinski', False)
                })
        
        # Sort by confidence
        candidates.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        print(f"\n[OK] Generated {len(candidates)} valid candidates")
        
        return {
            **target_data,
            'candidates': candidates,
            'generation_timestamp': datetime.now().isoformat()
        }
    
    def _create_candidate(self, source_drugs: List[Dict], seed: int) -> Dict:
        """Create a new drug candidate from source drugs"""
        np.random.seed(seed)
        
        # Select primary scaffold
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
            new_smiles = self._swap_functional_groups(scaffold)
        elif method == 'ring_modification':
            new_smiles = self._modify_rings(scaffold)
        elif method == 'side_chain_extension':
            new_smiles = self._extend_side_chain(scaffold)
        else:
            new_smiles = self._combine_pharmacophores(source_drugs)
        
        return {
            'smiles': new_smiles,
            'sources': source_drugs,
            'method': method
        }
    
    def _swap_functional_groups(self, smiles: str) -> str:
        """Swap functional groups using bioisosteric replacements"""
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
        if 'c1ccccc1' in smiles:
            heterocycles = ['c1ccncc1', 'c1cncnc1', 'c1ccsc1']
            replacement = np.random.choice(heterocycles)
            smiles = smiles.replace('c1ccccc1', replacement, 1)
        return smiles
    
    def _extend_side_chain(self, smiles: str) -> str:
        """Extend side chains"""
        extensions = ['C(=O)N', 'CC(C)C', 'CN', 'CC(=O)O']
        extension = np.random.choice(extensions)
        
        if np.random.random() > 0.5:
            return smiles + extension
        else:
            return extension + smiles
    
    def _combine_pharmacophores(self, source_drugs: List[Dict]) -> str:
        """Combine pharmacophores from multiple drugs"""
        fragments = []
        for drug in source_drugs:
            smiles = drug['smiles']
            if len(smiles) > 10:
                start = len(smiles) // 4
                end = 3 * len(smiles) // 4
                fragment = smiles[start:end]
                fragments.append(fragment)
        
        n_fragments = min(len(fragments), np.random.randint(2, 4))
        selected = np.random.choice(fragments, n_fragments, replace=False)
        
        return ''.join(selected)
    
    def _predict_targets(self, candidate: Dict, source_drugs: List[Dict]) -> List[str]:
        """Predict protein targets for candidate"""
        all_targets = []
        for drug in source_drugs:
            all_targets.extend(drug['targets'])
        return list(set(all_targets)) if all_targets else ['Unknown']
    
    def _calculate_enhanced_score(self, props: Dict, admet: ADMETProperties, targets: List[str]) -> float:
        """Calculate enhanced confidence score"""
        score = 0.0
        
        # QED contribution
        qed = props.get('qed', 0)
        score += min(qed, 0.8) * 0.25
        
        # Molecular weight
        mw = props.get('molecular_weight', 0)
        if 150 <= mw <= 500:
            score += 0.15
        
        # ADMET composite score
        admet_data = admet.to_dict()
        score += admet_data['overall']['admet_composite_score'] * 0.35
        
        # Drug-likeness
        if props.get('lipinski_rules', {}).get('passes_lipinski', False):
            score += 0.15
        
        # Number of targets
        score += min(len(targets) * 0.02, 0.10)
        
        return min(score, 1.0)


class EnhancedNOVO1System:
    """Enhanced NOVO-1 System with protein-first-last workflow"""
    
    def __init__(self, use_google_drive=False, drive_path=None):
        print("="*70)
        print("NOVO-1 DRUG DISCOVERY SYSTEM v3.0 - ENHANCED")
        print("Target Proteins + ADMET + All Chemical Properties")
        print("="*70)
        
        # Initialize managers
        self.drive_manager = None
        if use_google_drive and drive_path:
            self.drive_manager = GoogleDriveManager(drive_path)
        
        # Initialize components
        self.knowledge_graph = DrugRepurposingKnowledgeGraph(self.drive_manager)
        self.protein_db = ProteinDatabase()
        self.drug_generator = None
        
        print(f"[OK] System initialized with {len(self.protein_db.proteins)} proteins in database")
    
    def build_knowledge_graph(self, disease_data: List[Dict], drug_data: List[Dict]):
        """Build knowledge graph from data"""
        print("\n[BUILDING KNOWLEDGE GRAPH]")
        self.knowledge_graph.build_from_data(disease_data, drug_data)
        
        # Train embeddings
        print("\n[TRAINING EMBEDDINGS]")
        self.knowledge_graph.train_embeddings_cpu(
            dim=100,
            epochs=1000,
            lr=0.01,
            negative_samples=5
        )
        
        # Initialize drug generator
        self.drug_generator = EnhancedDrugGenerator(self.knowledge_graph, self.protein_db)
        
        # Save to Google Drive if available
        if self.drive_manager:
            self.knowledge_graph.save_to_drive('enhanced_kg_v3.pkl')
        
        print("\n[OK] Knowledge graph built and ready")
    
    def generate_drugs(self, symptoms: List[str], n_candidates: int = 10) -> Dict:
        """
        Complete workflow: Target Proteins -> Drug Candidates -> Target Proteins Summary
        """
        if self.drug_generator is None:
            raise ValueError("Knowledge graph not built. Call build_knowledge_graph() first.")
        
        print(f"\n{'#'*70}")
        print(f"STARTING COMPLETE DRUG DISCOVERY WORKFLOW")
        print(f"Symptoms: {symptoms}")
        print(f"{'#'*70}")
        
        # Generate candidates (includes target protein identification)
        results = self.drug_generator.generate_candidates(symptoms, n_candidates)
        
        # STEP 3: Final Target Protein Summary
        self._display_final_target_summary(results['target_proteins'])
        
        # Save results to Google Drive
        if self.drive_manager:
            self.drive_manager.save_results(results, f"enhanced_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        return results
    
    def _display_final_target_summary(self, target_proteins: List[Dict]):
        """Display final target protein summary (LAST)"""
        print(f"\n{'='*70}")
        print("STEP 3: FINAL TARGET PROTEIN SUMMARY")
        print(f"{'='*70}")
        print(f"\nAll {len(target_proteins)} Target Proteins for Generated Candidates:")
        print("-" * 70)
        
        for i, target in enumerate(target_proteins, 1):
            info = target['info']
            print(f"\n{i}. {target['protein_name']} [{info.get('uniprot_id', 'N/A')}]")
            print(f"   Gene: {info.get('gene_name', 'N/A')} | Family: {info.get('protein_family', 'N/A')}")
            print(f"   Druggability: {info.get('druggability', 'Unknown')} | Literature: {info.get('literature_count', 0)} papers")
            print(f"   Known Inhibitors ({len(info.get('known_inhibitors', []))}): {', '.join(info.get('known_inhibitors', [])[:5])}")
        
        print(f"\n{'='*70}")
    
    def display_candidates(self, results: Dict, top_n: int = 5):
        """Display generated drug candidates with full details"""
        candidates = results['candidates']
        
        print(f"\n{'='*70}")
        print(f"GENERATED DRUG CANDIDATES (Top {min(top_n, len(candidates))})")
        print(f"{'='*70}")
        
        for i, cand in enumerate(candidates[:top_n], 1):
            print(f"\n{'='*70}")
            print(f"CANDIDATE {i}: {cand['id']}")
            print(f"{'='*70}")
            
            # Basic info
            print(f"\n[BASIC INFORMATION]")
            print(f"  SMILES: {cand['smiles']}")
            print(f"  Molecular Formula: {cand['molecular_formula']}")
            print(f"  Generation Method: {cand['generation_method']}")
            print(f"  Confidence Score: {cand['confidence_score']:.1%}")
            print(f"  Drug-likeness (QED): {cand['drug_likeness']:.3f}")
            print(f"  Passes Lipinski Rules: {cand['passes_lipinski']}")
            
            # Chemical properties
            props = cand['all_properties']
            print(f"\n[MOLECULAR PROPERTIES]")
            print(f"  Molecular Weight: {props['physicochemical']['molecular_weight']:.2f} Da")
            print(f"  LogP: {props['physicochemical']['logp']:.2f}")
            print(f"  TPSA: {props['physicochemical']['tpsa']:.2f} Å²")
            print(f"  HBD: {props['hydrogen_bonding']['num_hbd']} | HBA: {props['hydrogen_bonding']['num_hba']}")
            print(f"  Rotatable Bonds: {props['structural']['num_rotatable_bonds']}")
            print(f"  Rings: {props['structural']['num_rings']} (Aromatic: {props['structural']['num_aromatic_rings']})")
            
            # Lipinski
            lipinski = props['lipinski_rules']
            print(f"\n[LIPINSKI RULE OF FIVE]")
            print(f"  Violations: {lipinski['num_violations']}/4")
            if lipinski['mw_violation']:
                print(f"    ⚠ MW > 500 Da")
            if lipinski['logp_violation']:
                print(f"    ⚠ LogP > 5")
            if lipinski['hbd_violation']:
                print(f"    ⚠ HBD > 5")
            if lipinski['hba_violation']:
                print(f"    ⚠ HBA > 10")
            
            # ADMET
            admet = cand['admet_properties']
            print(f"\n[ADMET PREDICTIONS]")
            print(f"  Absorption:")
            print(f"    * Oral Bioavailability: {admet['absorption']['oral_bioavailability_pct']:.1f}%")
            print(f"    * Intestinal Absorption: {admet['absorption']['human_intestinal_absorption_pct']:.1f}%")
            print(f"    * Caco2 Permeability: {admet['absorption']['caco2_permeability_nm_s']:.2f} nm/s")
            
            print(f"\n  Distribution:")
            print(f"    * BBB Penetration (logBB): {admet['distribution']['blood_brain_barrier_logbb']:.3f}")
            print(f"    * Plasma Protein Binding: {admet['distribution']['plasma_protein_binding_pct']:.1f}%")
            print(f"    * Volume of Distribution: {admet['distribution']['volume_distribution_l_kg']:.2f} L/kg")
            
            print(f"\n  Metabolism (CYP450 Inhibition):")
            cyp = admet['metabolism']
            for enzyme, prob in [
                ('CYP1A2', cyp['cyp1a2_inhibition_prob']),
                ('CYP2C9', cyp['cyp2c9_inhibition_prob']),
                ('CYP2C19', cyp['cyp2c19_inhibition_prob']),
                ('CYP2D6', cyp['cyp2d6_inhibition_prob']),
                ('CYP3A4', cyp['cyp3a4_inhibition_prob'])
            ]:
                status = "HIGH" if prob > 0.7 else "MOD" if prob > 0.4 else "LOW"
                print(f"    * {enzyme}: {prob:.1%} ({status})")
            print(f"    * Overall CYP Risk: {cyp['cyp_interaction_risk']}")
            
            print(f"\n  Excretion:")
            print(f"    * Clearance: {admet['excretion']['clearance_ml_min_kg']:.2f} mL/min/kg")
            print(f"    * Half-life: {admet['excretion']['half_life_hours']:.2f} hours")
            
            print(f"\n  Toxicity:")
            tox = admet['toxicity']
            print(f"    * Mutagenicity (Ames): {tox['ames_mutagenicity_prob']:.1%}")
            print(f"    * Hepatotoxicity: {tox['hepatotoxicity_prob']:.1%}")
            print(f"    * Cardiotoxicity (hERG): {tox['hERG_cardiotoxicity_prob']:.1%}")
            print(f"    * Skin Sensitization: {tox['skin_sensitization_prob']:.1%}")
            print(f"    * LD50 (rat oral): {tox['ld50_rat_oral_mg_kg']:.1f} mg/kg")
            print(f"    * Overall Risk: {tox['overall_toxicity_risk']}")
            
            print(f"\n  Overall Assessment:")
            print(f"    * Drug-likeness: {admet['overall']['drug_likeness_score']:.3f}")
            print(f"    * ADMET Score: {admet['overall']['admet_composite_score']:.3f}")
            
            # Target proteins
            print(f"\n[TARGET PROTEINS]")
            for target in cand['target_proteins'][:5]:
                info = self.protein_db.get_protein_info(target)
                print(f"  * {target} [{info.get('uniprot_id', 'N/A')}] - {info.get('protein_family', 'N/A')}")
            
            # Source drugs
            print(f"\n[SOURCE DRUGS]")
            for drug in cand['source_drugs']:
                print(f"  * {drug}")
        
        print(f"\n{'='*70}")
        print(f"SUMMARY: {len(candidates)} candidates generated")
        print(f"  * Average Confidence: {np.mean([c['confidence_score'] for c in candidates]):.1%}")
        print(f"  * Average QED: {np.mean([c['drug_likeness'] for c in candidates]):.3f}")
        print(f"  * Passes Lipinski: {sum([c['passes_lipinski'] for c in candidates])}/{len(candidates)}")
        print(f"{'='*70}\n")


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
            'name': 'Alzheimer Disease',
            'symptoms': ['memory loss', 'cognitive decline', 'neural inflammation']
        },
        {
            'name': 'Parkinson Disease',
            'symptoms': ['tremors', 'motor impairment', 'neural inflammation']
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
            'name': 'Donepezil',
            'smiles': 'COc1ccc2cc1C(=O)C(=C2)C(C)CC(=O)N3CCC4=CC=CC=C4C3',
            'targets': ['Acetylcholinesterase'],
            'indications': ['Alzheimer Disease']
        },
        {
            'name': 'Levodopa',
            'smiles': 'C1=CC(=C(C=C1CC(C(=O)O)N)O)O',
            'targets': ['Dopamine_Receptor_D2'],
            'indications': ['Parkinson Disease']
        }
    ]
    
    # Initialize enhanced system
    system = EnhancedNOVO1System(use_google_drive=False)
    
    # Build knowledge graph
    system.build_knowledge_graph(disease_data, drug_data)
    
    # Test 1: COVID-19 symptoms
    print("\n\n" + "#"*70)
    print("TEST 1: COVID-19 SYMPTOMS")
    print("#"*70)
    covid_symptoms = ['fever', 'cough', 'fatigue']
    covid_results = system.generate_drugs(covid_symptoms, n_candidates=5)
    system.display_candidates(covid_results, top_n=3)
    
    # Test 2: Complex neurological symptoms
    print("\n\n" + "#"*70)
    print("TEST 2: NEUROLOGICAL SYMPTOMS")
    print("#"*70)
    neuro_symptoms = ['tremors', 'neural inflammation', 'memory loss']
    neuro_results = system.generate_drugs(neuro_symptoms, n_candidates=5)
    system.display_candidates(neuro_results, top_n=3)
    
    print("\n\n[OK] Enhanced NOVO-1 System demonstration complete!")
