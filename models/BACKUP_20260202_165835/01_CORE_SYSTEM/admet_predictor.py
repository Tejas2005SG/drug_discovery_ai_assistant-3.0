"""
ADMET Prediction Module for Drug Discovery
Predicts Absorption, Distribution, Metabolism, Excretion, and Toxicity properties
Uses RDKit-based molecular descriptors and QSAR models
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ADMETProperties:
    """Container for ADMET properties"""
    # Absorption
    caco2_permeability: float  # nm/s, intestinal absorption proxy
    hia: float  # Human Intestinal Absorption (%)
    mdck_permeability: float  # MDCK cell permeability
    
    # Distribution
    bbb_permeability: float  # Blood-Brain Barrier permeability (logBB)
    ppb: float  # Plasma Protein Binding (%)
    vdss: float  # Volume of Distribution at steady state (L/kg)
    
    # Metabolism
    cyp1a2_inhibition: float  # Probability of CYP1A2 inhibition
    cyp2c9_inhibition: float  # Probability of CYP2C9 inhibition
    cyp2c19_inhibition: float  # Probability of CYP2C19 inhibition
    cyp2d6_inhibition: float  # Probability of CYP2D6 inhibition
    cyp3a4_inhibition: float  # Probability of CYP3A4 inhibition
    
    # Excretion
    clearance: float  # Total clearance (mL/min/kg)
    half_life: float  # Elimination half-life (h)
    
    # Toxicity
    ames_toxicity: float  # Probability of Ames test positive (mutagenicity)
    hepatotoxicity: float  # Probability of liver toxicity
    skin_sensitization: float  # Probability of skin sensitization
    hERG_inhibition: float  # hERG channel inhibition (cardiotoxicity risk)
    ld50: float  # Median lethal dose (mg/kg, rat oral)
    
    # Overall scores
    bioavailability: float  # Oral bioavailability (%)
    druglikeness_score: float  # Overall drug-likeness (0-1)
    toxicity_risk: str  # Overall toxicity risk level
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'absorption': {
                'caco2_permeability_nm_s': round(self.caco2_permeability, 3),
                'human_intestinal_absorption_pct': round(self.hia, 1),
                'mdck_permeability': round(self.mdck_permeability, 3),
                'oral_bioavailability_pct': round(self.bioavailability, 1)
            },
            'distribution': {
                'blood_brain_barrier_logbb': round(self.bbb_permeability, 3),
                'plasma_protein_binding_pct': round(self.ppb, 1),
                'volume_distribution_l_kg': round(self.vdss, 2)
            },
            'metabolism': {
                'cyp1a2_inhibition_prob': round(self.cyp1a2_inhibition, 3),
                'cyp2c9_inhibition_prob': round(self.cyp2c9_inhibition, 3),
                'cyp2c19_inhibition_prob': round(self.cyp2c19_inhibition, 3),
                'cyp2d6_inhibition_prob': round(self.cyp2d6_inhibition, 3),
                'cyp3a4_inhibition_prob': round(self.cyp3a4_inhibition, 3),
                'cyp_interaction_risk': self._calculate_cyp_risk()
            },
            'excretion': {
                'clearance_ml_min_kg': round(self.clearance, 2),
                'half_life_hours': round(self.half_life, 2)
            },
            'toxicity': {
                'ames_mutagenicity_prob': round(self.ames_toxicity, 3),
                'hepatotoxicity_prob': round(self.hepatotoxicity, 3),
                'skin_sensitization_prob': round(self.skin_sensitization, 3),
                'hERG_cardiotoxicity_prob': round(self.hERG_inhibition, 3),
                'ld50_rat_oral_mg_kg': round(self.ld50, 1),
                'overall_toxicity_risk': self.toxicity_risk
            },
            'overall': {
                'drug_likeness_score': round(self.druglikeness_score, 3),
                'admet_composite_score': round(self._calculate_composite_score(), 3)
            }
        }
    
    def _calculate_cyp_risk(self) -> str:
        """Calculate overall CYP interaction risk"""
        inhibitions = [
            self.cyp1a2_inhibition, self.cyp2c9_inhibition,
            self.cyp2c19_inhibition, self.cyp2d6_inhibition,
            self.cyp3a4_inhibition
        ]
        avg_inhibition = np.mean(inhibitions)
        
        if avg_inhibition > 0.7:
            return "HIGH"
        elif avg_inhibition > 0.4:
            return "MODERATE"
        else:
            return "LOW"
    
    def _calculate_composite_score(self) -> float:
        """Calculate composite ADMET score"""
        # Weight factors
        w_absorption = 0.20
        w_distribution = 0.15
        w_metabolism = 0.20
        w_excretion = 0.15
        w_toxicity = 0.30
        
        # Normalize each component (0-1 scale)
        absorption_score = self.bioavailability / 100.0
        
        distribution_score = 1.0 - abs(self.bbb_permeability) / 3.0  # Prefer moderate BBB
        distribution_score = max(0, min(1, distribution_score))
        
        metabolism_score = 1.0 - np.mean([
            self.cyp1a2_inhibition, self.cyp2c9_inhibition,
            self.cyp2c19_inhibition, self.cyp2d6_inhibition,
            self.cyp3a4_inhibition
        ])
        
        excretion_score = 1.0 if 2 < self.half_life < 40 else 0.5
        
        toxicity_score = 1.0 - np.mean([
            self.ames_toxicity, self.hepatotoxicity,
            self.skin_sensitization, self.hERG_inhibition
        ])
        
        composite = (w_absorption * absorption_score +
                    w_distribution * distribution_score +
                    w_metabolism * metabolism_score +
                    w_excretion * excretion_score +
                    w_toxicity * toxicity_score)
        
        return composite


class ADMETPredictor:
    """
    ADMET property predictor using molecular descriptors
    Uses QSAR models and molecular property calculations
    """
    
    def __init__(self):
        self.use_rdkit = self._check_rdkit()
        self._load_qsar_models()
        
    def _check_rdkit(self) -> bool:
        """Check if RDKit is available"""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Crippen, Lipinski
            return True
        except ImportError:
            print("[WARNING] RDKit not available - using simplified ADMET predictions")
            return False
    
    def _load_qsar_models(self):
        """Load pre-trained QSAR model parameters"""
        # These are simplified model coefficients
        # In production, load actual trained models
        
        self.model_params = {
            'caco2': {
                'mw_coeff': -0.01,
                'logp_coeff': 0.5,
                'hbd_coeff': -0.3,
                'hba_coeff': -0.2,
                'intercept': 5.0
            },
            'bbb': {
                'mw_coeff': -0.005,
                'logp_coeff': 0.3,
                'psa_coeff': -0.01,
                'intercept': -0.5
            },
            'hia': {
                'psa_coeff': -0.5,
                'hbd_coeff': -5.0,
                'logp_coeff': 5.0,
                'intercept': 90.0
            },
            'clearance': {
                'mw_coeff': 0.01,
                'logp_coeff': 0.3,
                'rotb_coeff': 0.1,
                'intercept': 5.0
            }
        }
    
    def predict_admet(self, smiles: str, mol_properties: Dict = None) -> ADMETProperties:
        """
        Predict ADMET properties for a molecule
        
        Args:
            smiles: SMILES string
            mol_properties: Pre-calculated molecular properties (optional)
            
        Returns:
            ADMETProperties object with all predictions
        """
        if mol_properties is None:
            mol_properties = self._calculate_molecular_descriptors(smiles)
        
        # Calculate each ADMET property
        absorption = self._predict_absorption(mol_properties)
        distribution = self._predict_distribution(mol_properties)
        metabolism = self._predict_metabolism(mol_properties)
        excretion = self._predict_excretion(mol_properties)
        toxicity = self._predict_toxicity(mol_properties)
        
        # Calculate overall drug-likeness
        druglikeness = self._calculate_druglikeness(mol_properties, absorption, distribution, metabolism, excretion, toxicity)
        
        return ADMETProperties(
            caco2_permeability=absorption['caco2'],
            hia=absorption['hia'],
            mdck_permeability=absorption['mdck'],
            bbb_permeability=distribution['bbb'],
            ppb=distribution['ppb'],
            vdss=distribution['vdss'],
            cyp1a2_inhibition=metabolism['cyp1a2'],
            cyp2c9_inhibition=metabolism['cyp2c9'],
            cyp2c19_inhibition=metabolism['cyp2c19'],
            cyp2d6_inhibition=metabolism['cyp2d6'],
            cyp3a4_inhibition=metabolism['cyp3a4'],
            clearance=excretion['clearance'],
            half_life=excretion['half_life'],
            ames_toxicity=toxicity['ames'],
            hepatotoxicity=toxicity['hepatotoxicity'],
            skin_sensitization=toxicity['skin_sensitization'],
            hERG_inhibition=toxicity['hERG'],
            ld50=toxicity['ld50'],
            bioavailability=absorption['bioavailability'],
            druglikeness_score=druglikeness['score'],
            toxicity_risk=toxicity['risk']
        )
    
    def _calculate_molecular_descriptors(self, smiles: str) -> Dict:
        """Calculate molecular descriptors using RDKit or simplified method"""
        if self.use_rdkit:
            return self._calculate_with_rdkit(smiles)
        else:
            return self._calculate_simple(smiles)
    
    def _calculate_with_rdkit(self, smiles: str) -> Dict:
        """Calculate comprehensive descriptors with RDKit"""
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return self._get_default_descriptors()
        
        # Calculate all major descriptors
        descriptors = {
            'mw': Descriptors.MolWt(mol),
            'logp': Crippen.MolLogP(mol),
            'tpsa': rdMolDescriptors.CalcTPSA(mol),
            'hbd': Lipinski.NumHDonors(mol),
            'hba': Lipinski.NumHAcceptors(mol),
            'rotb': Lipinski.NumRotatableBonds(mol),
            'rings': Lipinski.RingCount(mol),
            'aromatic_rings': Lipinski.NumAromaticRings(mol),
            'heavy_atoms': Lipinski.HeavyAtomCount(mol),
            'formal_charge': Chem.GetFormalCharge(mol),
            'mr': Crippen.MolMR(mol),  # Molar refractivity
            'fraction_sp3': Lipinski.FractionCSP3(mol),
            'num_het_atoms': Lipinski.NumHeteroatoms(mol),
            'mol_volume': Descriptors.MolSurf(mol) if hasattr(Descriptors, 'MolSurf') else 0,
            'qed': self._calculate_qed(mol)
        }
        
        return descriptors
    
    def _calculate_simple(self, smiles: str) -> Dict:
        """Calculate simplified descriptors without RDKit"""
        # Basic atom counting
        carbons = smiles.count('C') - smiles.count('c')
        oxygens = smiles.count('O') - smiles.count('o')
        nitrogens = smiles.count('N') - smiles.count('n')
        sulfurs = smiles.count('S') - smiles.count('s')
        halogens = smiles.count('F') + smiles.count('Cl') + smiles.count('Br') + smiles.count('I')
        
        # Estimate molecular weight
        mw = (carbons * 12.01 + oxygens * 16.00 + nitrogens * 14.01 + 
              sulfurs * 32.06 + halogens * 19.00)
        
        # Estimate logP (very rough)
        logp = carbons * 0.5 - oxygens * 0.7 - nitrogens * 0.3
        
        # Estimate PSA
        psa = oxygens * 20 + nitrogens * 23
        
        return {
            'mw': mw,
            'logp': logp,
            'tpsa': psa,
            'hbd': smiles.count('H') if 'H' in smiles else 0,
            'hba': oxygens + nitrogens,
            'rotb': smiles.count('CC') + smiles.count('C(=O)'),
            'rings': smiles.count('1') + smiles.count('2'),
            'aromatic_rings': smiles.count('c'),
            'heavy_atoms': carbons + oxygens + nitrogens + sulfurs + halogens,
            'formal_charge': 0,
            'mr': mw * 0.1,
            'fraction_sp3': 0.5,
            'num_het_atoms': oxygens + nitrogens + sulfurs + halogens,
            'mol_volume': mw * 0.7,
            'qed': 0.5
        }
    
    def _get_default_descriptors(self) -> Dict:
        """Return default descriptors for invalid molecules"""
        return {
            'mw': 300.0, 'logp': 2.0, 'tpsa': 60.0,
            'hbd': 1, 'hba': 3, 'rotb': 4,
            'rings': 2, 'aromatic_rings': 1,
            'heavy_atoms': 20, 'formal_charge': 0,
            'mr': 80.0, 'fraction_sp3': 0.4,
            'num_het_atoms': 5, 'mol_volume': 300.0,
            'qed': 0.5
        }
    
    def _calculate_qed(self, mol) -> float:
        """Calculate QED (drug-likeness) score"""
        try:
            from rdkit.Chem import QED
            return QED.qed(mol)
        except:
            return 0.5
    
    def _predict_absorption(self, props: Dict) -> Dict:
        """Predict absorption properties"""
        # Caco2 permeability (nm/s)
        caco2 = (self.model_params['caco2']['intercept'] +
                 self.model_params['caco2']['mw_coeff'] * props['mw'] +
                 self.model_params['caco2']['logp_coeff'] * props['logp'] +
                 self.model_params['caco2']['hbd_coeff'] * props['hbd'] +
                 self.model_params['caco2']['hba_coeff'] * props['hba'])
        caco2 = max(0.1, min(100, caco2))  # Clip to reasonable range
        
        # Human Intestinal Absorption (%)
        hia = (self.model_params['hia']['intercept'] +
               self.model_params['hia']['psa_coeff'] * props['tpsa'] / 100 +
               self.model_params['hia']['hbd_coeff'] * props['hbd'] +
               self.model_params['hia']['logp_coeff'] * props['logp'])
        hia = max(0, min(100, hia))
        
        # MDCK permeability (correlated with Caco2)
        mdck = caco2 * 0.7
        
        # Bioavailability calculation (simplified)
        bioavailability = self._calculate_bioavailability(props, hia)
        
        return {
            'caco2': caco2,
            'hia': hia,
            'mdck': mdck,
            'bioavailability': bioavailability
        }
    
    def _predict_distribution(self, props: Dict) -> Dict:
        """Predict distribution properties"""
        # Blood-Brain Barrier permeability (logBB)
        bbb = (self.model_params['bbb']['intercept'] +
               self.model_params['bbb']['mw_coeff'] * props['mw'] +
               self.model_params['bbb']['logp_coeff'] * props['logp'] +
               self.model_params['bbb']['psa_coeff'] * props['tpsa'])
        bbb = max(-3, min(2, bbb))  # Clip to reasonable range
        
        # Plasma Protein Binding (%) - based on lipophilicity
        ppb = 20 + props['logp'] * 15 + props['mw'] * 0.05
        ppb = max(0, min(99, ppb))
        
        # Volume of Distribution (L/kg) - empirical model
        vdss = 0.3 + props['logp'] * 0.2 + props['mw'] * 0.001
        vdss = max(0.1, min(10, vdss))
        
        return {
            'bbb': bbb,
            'ppb': ppb,
            'vdss': vdss
        }
    
    def _predict_metabolism(self, props: Dict) -> Dict:
        """Predict metabolic properties (CYP inhibition probabilities)"""
        # CYP inhibition is correlated with molecular size and lipophilicity
        base_inhibition = 0.3 + props['logp'] * 0.05 - props['tpsa'] * 0.002
        
        # Each CYP has slightly different characteristics
        metabolism = {
            'cyp1a2': self._sigmoid(base_inhibition + 0.1 + props['aromatic_rings'] * 0.05),
            'cyp2c9': self._sigmoid(base_inhibition + props['logp'] * 0.05),
            'cyp2c19': self._sigmoid(base_inhibition + 0.05),
            'cyp2d6': self._sigmoid(base_inhibition - 0.1 + props['hbd'] * 0.02),
            'cyp3a4': self._sigmoid(base_inhibition + 0.15 + props['mw'] * 0.001)
        }
        
        return metabolism
    
    def _predict_excretion(self, props: Dict) -> Dict:
        """Predict excretion properties"""
        # Clearance (mL/min/kg)
        clearance = (self.model_params['clearance']['intercept'] +
                    self.model_params['clearance']['mw_coeff'] * props['mw'] +
                    self.model_params['clearance']['logp_coeff'] * props['logp'] +
                    self.model_params['clearance']['rotb_coeff'] * props['rotb'])
        clearance = max(0.5, min(50, clearance))
        
        # Half-life (hours) - inversely related to clearance
        # Assuming typical volume of distribution
        vd_typical = 1.0  # L/kg
        half_life = 0.693 * vd_typical / (clearance / 1000 * 60 / 1000)
        half_life = max(0.5, min(100, half_life))
        
        return {
            'clearance': clearance,
            'half_life': half_life
        }
    
    def _predict_toxicity(self, props: Dict) -> Dict:
        """Predict toxicity properties"""
        # Ames mutagenicity (based on structural alerts)
        ames_base = 0.1
        if props['aromatic_rings'] > 2:
            ames_base += 0.15
        if props['nitrogens'] > 3 and props['aromatic_rings'] > 1:
            ames_base += 0.1
        ames = self._sigmoid(ames_base)
        
        # Hepatotoxicity
        hep_base = 0.2 + props['mw'] * 0.0005 + props['logp'] * 0.03
        hepatotoxicity = self._sigmoid(hep_base)
        
        # Skin sensitization (based on reactivity)
        skin_base = 0.15 + props['num_het_atoms'] * 0.01
        skin_sensitization = self._sigmoid(skin_base)
        
        # hERG inhibition (cardiotoxicity)
        # Correlated with logP and basicity
        herg_base = -1.0 + props['logp'] * 0.3 - props['tpsa'] * 0.005 + props['hbd'] * 0.1
        hERG = self._sigmoid(herg_base)
        
        # LD50 (mg/kg, rat oral) - inversely related to toxicity
        # Lower LD50 = more toxic
        ld50 = 1000 - props['mw'] * 0.5 - props['logp'] * 50
        ld50 = max(10, min(5000, ld50))
        
        # Overall toxicity risk
        avg_toxicity = np.mean([ames, hepatotoxicity, skin_sensitization, hERG])
        if avg_toxicity > 0.6:
            risk = "HIGH"
        elif avg_toxicity > 0.3:
            risk = "MODERATE"
        else:
            risk = "LOW"
        
        return {
            'ames': ames,
            'hepatotoxicity': hepatotoxicity,
            'skin_sensitization': skin_sensitization,
            'hERG': hERG,
            'ld50': ld50,
            'risk': risk
        }
    
    def _calculate_bioavailability(self, props: Dict, hia: float) -> float:
        """Calculate oral bioavailability"""
        # Simplified model: bioavailability = HIA * (1 - first-pass)
        # First-pass is affected by CYP metabolism
        first_pass = 0.1 + props['logp'] * 0.05
        
        bioavailability = hia * (1 - first_pass)
        return max(0, min(100, bioavailability))
    
    def _calculate_druglikeness(self, props: Dict, absorption: Dict, 
                               distribution: Dict, metabolism: Dict,
                               excretion: Dict, toxicity: Dict) -> Dict:
        """Calculate overall drug-likeness score"""
        
        # Lipinski's Rule of Five violations
        violations = 0
        if props['mw'] > 500:
            violations += 1
        if props['logp'] > 5:
            violations += 1
        if props['hbd'] > 5:
            violations += 1
        if props['hba'] > 10:
            violations += 1
        
        # QED contribution
        qed_score = props.get('qed', 0.5)
        
        # Bioavailability contribution
        bioavail_score = absorption['bioavailability'] / 100
        
        # Toxicity penalty
        toxicity_penalty = np.mean([
            toxicity['ames'], toxicity['hepatotoxicity'],
            toxicity['hERG']
        ])
        
        # Calculate final score
        score = (0.3 * qed_score + 
                0.3 * bioavail_score + 
                0.2 * (1 - violations / 4) + 
                0.2 * (1 - toxicity_penalty))
        
        return {
            'score': max(0, min(1, score)),
            'lipinski_violations': violations,
            'is_druglike': violations <= 1 and score > 0.5
        }
    
    def _sigmoid(self, x: float) -> float:
        """Apply sigmoid function to get probability"""
        return 1 / (1 + np.exp(-x))
    
    def predict_batch(self, smiles_list: List[str]) -> List[ADMETProperties]:
        """Predict ADMET for multiple molecules"""
        return [self.predict_admet(smiles) for smiles in smiles_list]
    
    def get_admet_summary(self, admet: ADMETProperties) -> str:
        """Get human-readable summary of ADMET properties"""
        data = admet.to_dict()
        
        summary = []
        summary.append("="*70)
        summary.append("ADMET PREDICTION SUMMARY")
        summary.append("="*70)
        
        # Absorption
        summary.append("\n[ABSORPTION]")
        summary.append(f"  Oral Bioavailability: {data['absorption']['oral_bioavailability_pct']}%")
        summary.append(f"  Intestinal Absorption: {data['absorption']['human_intestinal_absorption_pct']}%")
        summary.append(f"  Caco2 Permeability: {data['absorption']['caco2_permeability_nm_s']} nm/s")
        
        # Distribution
        summary.append("\n[DISTRIBUTION]")
        summary.append(f"  Blood-Brain Barrier: {data['distribution']['blood_brain_barrier_logbb']:.3f} (logBB)")
        if data['distribution']['blood_brain_barrier_logbb'] > 0.3:
            summary.append(f"    -> Can cross BBB (CNS active)")
        elif data['distribution']['blood_brain_barrier_logbb'] < -1.0:
            summary.append(f"    -> Poor BBB penetration (peripheral)")
        else:
            summary.append(f"    -> Moderate BBB penetration")
        
        summary.append(f"  Plasma Protein Binding: {data['distribution']['plasma_protein_binding_pct']}%")
        
        # Metabolism
        summary.append("\n[METABOLISM - CYP450 Interactions]")
        cyp_data = data['metabolism']
        for cyp, prob in [
            ('CYP1A2', cyp_data['cyp1a2_inhibition_prob']),
            ('CYP2C9', cyp_data['cyp2c9_inhibition_prob']),
            ('CYP2C19', cyp_data['cyp2c19_inhibition_prob']),
            ('CYP2D6', cyp_data['cyp2d6_inhibition_prob']),
            ('CYP3A4', cyp_data['cyp3a4_inhibition_prob'])
        ]:
            status = "HIGH" if prob > 0.7 else "MOD" if prob > 0.4 else "LOW"
            summary.append(f"  {cyp} Inhibition: {prob:.1%} ({status})")
        summary.append(f"  Overall CYP Risk: {cyp_data['cyp_interaction_risk']}")
        
        # Excretion
        summary.append("\n[EXCRETION]")
        summary.append(f"  Half-life: {data['excretion']['half_life_hours']} hours")
        summary.append(f"  Clearance: {data['excretion']['clearance_ml_min_kg']} mL/min/kg")
        
        # Toxicity
        summary.append("\n[TOXICITY RISK]")
        tox = data['toxicity']
        summary.append(f"  Mutagenicity (Ames): {tox['ames_mutagenicity_prob']:.1%}")
        summary.append(f"  Hepatotoxicity: {tox['hepatotoxicity_prob']:.1%}")
        summary.append(f"  Cardiotoxicity (hERG): {tox['hERG_cardiotoxicity_prob']:.1%}")
        summary.append(f"  Skin Sensitization: {tox['skin_sensitization_prob']:.1%}")
        summary.append(f"  LD50 (rat oral): {tox['ld50_rat_oral_mg_kg']} mg/kg")
        summary.append(f"  OVERALL RISK: {tox['overall_toxicity_risk']}")
        
        # Overall
        summary.append("\n[OVERALL ASSESSMENT]")
        summary.append(f"  Drug-likeness Score: {data['overall']['drug_likeness_score']:.3f}")
        summary.append(f"  ADMET Composite Score: {data['overall']['admet_composite_score']:.3f}")
        
        if data['overall']['admet_composite_score'] > 0.7:
            summary.append(f"  STATUS: EXCELLENT candidate")
        elif data['overall']['admet_composite_score'] > 0.5:
            summary.append(f"  STATUS: GOOD candidate with minor concerns")
        else:
            summary.append(f"  STATUS: NEEDS OPTIMIZATION")
        
        summary.append("="*70)
        
        return "\n".join(summary)


# Example usage
if __name__ == "__main__":
    # Test ADMET predictor
    predictor = ADMETPredictor()
    
    # Test molecules
    test_smiles = [
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # Ibuprofen
        "CC(C)(C)NC(=O)C1CC2(CCN(C(=O)C(C(C)(C)C)NC(=O)C(F)(F)F)CC2)CN1C(=O)O",  # Paxlovid-like
        "c1ccc2c(c1)c(CC(=O)O)c(C)n2C(=O)c3ccccc3"  # Complex molecule
    ]
    
    print("ADMET PREDICTION EXAMPLES")
    print("="*70)
    
    for i, smiles in enumerate(test_smiles, 1):
        print(f"\n\nTEST MOLECULE {i}")
        print(f"SMILES: {smiles[:50]}...")
        
        admet = predictor.predict_admet(smiles)
        summary = predictor.get_admet_summary(admet)
        print(summary)
    
    print("\n[OK] ADMET prediction module ready!")
