"""
Drug Target Mapping System
Maps drugs to their protein targets based on disease and mechanism of action
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class DrugTargetMapper:
    """
    Maps drugs to their protein targets based on:
    - Drug name
    - Disease indication
    - Mechanism of action
    """
    
    def __init__(self):
        # Comprehensive drug to target mapping
        self.drug_targets = {
            # Multiple Sclerosis drugs
            "alemtuzumab": ["CD20", "CD52"],
            "lemtrada": ["CD20", "CD52"],
            "avonex": ["Interferon_receptor"],
            "interferon_beta_1a": ["Interferon_receptor"],
            "betaseron": ["Interferon_receptor"],
            "interferon_beta_1b": ["Interferon_receptor"],
            "copaxone": ["MHC_Class_II", "TCR"],
            "glatiramer_acetate": ["MHC_Class_II", "TCR"],
            "tysabri": ["Integrin_alpha4"],
            "natalizumab": ["Integrin_alpha4"],
            "gilenya": ["S1P_receptor"],
            "fingolimod": ["S1P_receptor"],
            "aubagio": ["DHODH"],
            "teriflunomide": ["DHODH"],
            "tecifidera": ["Nrf2", "HDAC"],
            "dimethyl_fumarate": ["Nrf2", "HDAC"],
            "ocrevus": ["CD20"],
            "ocrelizumab": ["CD20"],
            "kesimpta": ["CD20"],
            "ofatumumab": ["CD20"],
            "zeposia": ["S1P_receptor"],
            "ponesimod": ["S1P_receptor"],
            "mayzent": ["S1P_receptor"],
            "siponimod": ["S1P_receptor"],
            "vumerity": ["Nrf2", "HDAC"],
            "diroximel_fumarate": ["Nrf2", "HDAC"],
            "ponvory": ["S1P_receptor"],
            "pletal": ["PDE3"],
            
            # Parkinson's Disease drugs
            "levodopa": ["Dopamine_Receptor_D2", "Dopamine_Receptor_D1"],
            "l_dopa": ["Dopamine_Receptor_D2", "Dopamine_Receptor_D1"],
            "sinemet": ["Dopamine_Receptor_D2", "Dopamine_Receptor_D1"],
            "carbidopa": ["Aromatic_L_amino_acid_decarboxylase"],
            "entacapone": ["COMT"],
            "comtan": ["COMT"],
            "stalevo": ["Dopamine_Receptor_D2", "COMT"],
            "ropinirole": ["Dopamine_Receptor_D2"],
            "requip": ["Dopamine_Receptor_D2"],
            "pramipexole": ["Dopamine_Receptor_D2"],
            "mirapex": ["Dopamine_Receptor_D2"],
            "rotigotine": ["Dopamine_Receptor_D2"],
            "neupro": ["Dopamine_Receptor_D2"],
            "rasagiline": ["Monoamine_Oxidase_B"],
            "azilect": ["Monoamine_Oxidase_B"],
            "selegiline": ["Monoamine_Oxidase_B"],
            "eldepryl": ["Monoamine_Oxidase_B"],
            "safinamide": ["Monoamine_Oxidase_B"],
            "xadago": ["Monoamine_Oxidase_B"],
            "amantadine": ["NMDA_receptor", "Dopamine_transporter"],
            "symmetrel": ["NMDA_receptor", "Dopamine_transporter"],
            "trihexyphenidyl": ["Muscarinic_acetylcholine_receptor"],
            "artane": ["Muscarinic_acetylcholine_receptor"],
            "benztropine": ["Muscarinic_acetylcholine_receptor", "Dopamine_transporter"],
            "cogentin": ["Muscarinic_acetylcholine_receptor", "Dopamine_transporter"],
            "ropinirole": ["Dopamine_Receptor_D2"],
            
            # Epilepsy drugs
            "carbamazepine": ["Sodium_Channel"],
            "tegretol": ["Sodium_Channel"],
            "lamotrigine": ["Sodium_Channel", "Calcium_Channel"],
            "lamictal": ["Sodium_Channel", "Calcium_Channel"],
            "valproic_acid": ["GABA_transaminase", "HDAC"],
            "valproate": ["GABA_transaminase", "HDAC"],
            "depakote": ["GABA_transaminase", "HDAC"],
            "levetiracetam": ["SV2A"],
            "keppra": ["SV2A"],
            "topiramate": ["AMPA_receptor", "Carbonic_anhydrase"],
            "topamax": ["AMPA_receptor", "Carbonic_anhydrase"],
            "phenytoin": ["Sodium_Channel"],
            "dilantin": ["Sodium_Channel"],
            "gabapentin": ["Calcium_Channel_alpha2delta"],
            "neurontin": ["Calcium_Channel_alpha2delta"],
            "pregabalin": ["Calcium_Channel_alpha2delta"],
            "lyrica": ["Calcium_Channel_alpha2delta"],
            "oxcarbazepine": ["Sodium_Channel"],
            "trileptal": ["Sodium_Channel"],
            "zonisamide": ["Carbonic_anhydrase", "Sodium_Channel"],
            "zonegran": ["Carbonic_anhydrase", "Sodium_Channel"],
            "lacosamide": ["Sodium_Channel"],
            "vimpat": ["Sodium_Channel"],
            "vigabatrin": ["GABA_transaminase"],
            "sabril": ["GABA_transaminase"],
            "rufinamide": ["Sodium_Channel"],
            "banzel": ["Sodium_Channel"],
            "eslicarbazepine": ["Sodium_Channel"],
            "aptiom": ["Sodium_Channel"],
            "perampanel": ["AMPA_receptor"],
            "fycompa": ["AMPA_receptor"],
            "brivaracetam": ["SV2A"],
            "briviact": ["SV2A"],
            "ethosuximide": ["Calcium_Channel_T_type"],
            "zarontin": ["Calcium_Channel_T_type"],
            "felbamate": ["NMDA_receptor"],
            "felbatol": ["NMDA_receptor"],
            "tiagabine": ["GABA_transporter"],
            "gabitril": ["GABA_transporter"],
            "clobazam": ["GABA_Receptor"],
            "onfi": ["GABA_Receptor"],
            "clonazepam": ["GABA_Receptor"],
            "klonopin": ["GABA_Receptor"],
            "lorazepam": ["GABA_Receptor"],
            "ativan": ["GABA_Receptor"],
            "diazepam": ["GABA_Receptor"],
            "valium": ["GABA_Receptor"],
            "midazolam": ["GABA_Receptor"],
            "versed": ["GABA_Receptor"],
            "phenobarbital": ["GABA_Receptor"],
            "luminal": ["GABA_Receptor"],
            "primidone": ["GABA_Receptor"],
            "mysoline": ["GABA_Receptor"],
            "acetazolamide": ["Carbonic_anhydrase"],
            "diamox": ["Carbonic_anhydrase"],
            
            # Alzheimer's drugs
            "donepezil": ["Acetylcholinesterase"],
            "aricept": ["Acetylcholinesterase"],
            "rivastigmine": ["Acetylcholinesterase", "Butyrylcholinesterase"],
            "exelon": ["Acetylcholinesterase", "Butyrylcholinesterase"],
            "galantamine": ["Acetylcholinesterase"],
            "razadyne": ["Acetylcholinesterase"],
            "memantine": ["NMDA_receptor"],
            "namenda": ["NMDA_receptor"],
            "namzaric": ["Acetylcholinesterase", "NMDA_receptor"],
            
            # Migraine drugs
            "sumatriptan": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "imitrex": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "rizatriptan": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "maxalt": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "zolmitriptan": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "zomig": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "eletriptan": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "relpax": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "naratriptan": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "amerge": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "almotriptan": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "axert": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "frovatriptan": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "frova": ["Serotonin_Receptor_5HT1B", "Serotonin_Receptor_5HT1D"],
            "topiramate_migraine": ["AMPA_receptor", "Carbonic_anhydrase"],
            "propranolol": ["Beta_adrenergic_receptor"],
            "inderal": ["Beta_adrenergic_receptor"],
            "metoprolol": ["Beta_1_adrenergic_receptor"],
            "toprol": ["Beta_1_adrenergic_receptor"],
            "amitriptyline": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "elavil": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "venlafaxine": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "effexor": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "divalproex": ["GABA_transaminase", "HDAC"],
            "onabotulinumtoxina": ["SNAP_25"],
            "botox": ["SNAP_25"],
            "erenumab": ["CGRP_receptor"],
            "aimovig": ["CGRP_receptor"],
            "galcanezumab": ["CGRP_ligand"],
            "emgality": ["CGRP_ligand"],
            "fremanezumab": ["CGRP_ligand"],
            "ajovy": ["CGRP_ligand"],
            "eptinezumab": ["CGRP_ligand"],
            "vyepti": ["CGRP_ligand"],
            "ubrogepant": ["CGRP_receptor"],
            "ubrelvy": ["CGRP_receptor"],
            "rimegepant": ["CGRP_receptor"],
            "nurtec": ["CGRP_receptor"],
            "lasmiditan": ["Serotonin_Receptor_5HT1F"],
            "reyvow": ["Serotonin_Receptor_5HT1F"],
            
            # COVID-19 drugs
            "paxlovid": ["3CL_protease", "Mpro"],
            "nirmatrelvir": ["3CL_protease", "Mpro"],
            "ritonavir": ["CYP3A4"],
            "remdesivir": ["RNA_dependent_RNA_polymerase"],
            "veklury": ["RNA_dependent_RNA_polymerase"],
            "molnupiravir": ["RNA_dependent_RNA_polymerase"],
            "lagevrio": ["RNA_dependent_RNA_polymerase"],
            "baricitinib": ["JAK1", "JAK2"],
            "olumiant": ["JAK1", "JAK2"],
            "tocilizumab": ["Interleukin_6_Receptor"],
            "actemra": ["Interleukin_6_Receptor"],
            "sotrovimab": ["Spike_protein"],
            "evusheld": ["Spike_protein"],
            "bebtelovimab": ["Spike_protein"],
            "casirivimab": ["Spike_protein"],
            "imdevimab": ["Spike_protein"],
            "tixagevimab": ["Spike_protein"],
            "cilgavimab": ["Spike_protein"],
            
            # ALS drugs
            "riluzole": ["Glutamate_receptor", "Sodium_Channel"],
            "rilotek": ["Glutamate_receptor", "Sodium_Channel"],
            "edaravone": ["Free_radical_scavenger"],
            "radicava": ["Free_radical_scavenger"],
            "tofersen": ["SOD1_mRNA"],
            "qalsody": ["SOD1_mRNA"],
            
            # Tremor drugs
            "propranolol_tremor": ["Beta_adrenergic_receptor"],
            "primidone_tremor": ["GABA_Receptor"],
            "clonazepam_tremor": ["GABA_Receptor"],
            "alprazolam": ["GABA_Receptor"],
            "xanax": ["GABA_Receptor"],
            
            # Dystonia drugs
            "botulinum_toxin_a": ["SNAP_25"],
            "botulinum_toxin_b": ["SNAP_25"],
            "trihexyphenidyl_dystonia": ["Muscarinic_acetylcholine_receptor"],
            
            # Potassium channel modulators
            "dapagliflozin": ["SGLT2"],
            "farxiga": ["SGLT2"],
            "empagliflozin": ["SGLT2"],
            "jardiance": ["SGLT2"],
            "canagliflozin": ["SGLT2"],
            "invokana": ["SGLT2"],
            "4_aminopyridine": ["Potassium_Channel"],
            "dalfampridine": ["Potassium_Channel"],
            "ampyra": ["Potassium_Channel"],
            "fampridine": ["Potassium_Channel"],
            "retigabine": ["Potassium_Channel_KCNQ"],
            "ezogabine": ["Potassium_Channel_KCNQ"],
            "potiga": ["Potassium_Channel_KCNQ"],
            "flupirtine": ["Potassium_Channel_KCNQ"],
            "amiodarone": ["Potassium_Channel"],
            "cordarone": ["Potassium_Channel"],
            "sotalol": ["Potassium_Channel"],
            "betapace": ["Potassium_Channel"],
            "dofetilide": ["Potassium_Channel"],
            "tikosyn": ["Potassium_Channel"],
            "ibutilide": ["Potassium_Channel"],
            "corvert": ["Potassium_Channel"],
            
            # Neuropathic pain drugs
            "amitriptyline_pain": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "nortriptyline": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "pamelor": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "desipramine": ["Norepinephrine_transporter"],
            "norpramin": ["Norepinephrine_transporter"],
            "imipramine": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "tofranil": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "duloxetine": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "cymbalta": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "venlafaxine_pain": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "milnacipran": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "savella": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "levomilnacipran": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "fetzima": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "desvenlafaxine": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "pristiq": ["Serotonin_transporter", "Norepinephrine_transporter"],
            "carbamazepine_pain": ["Sodium_Channel"],
            "oxcarbazepine_pain": ["Sodium_Channel"],
            "lamotrigine_pain": ["Sodium_Channel", "Calcium_Channel"],
            "baclofen": ["GABA_B_receptor"],
            "lioresal": ["GABA_B_receptor"],
            "tizanidine": ["Alpha_2_adrenergic_receptor"],
            "zanaflex": ["Alpha_2_adrenergic_receptor"],
            "clonidine": ["Alpha_2_adrenergic_receptor"],
            "catapres": ["Alpha_2_adrenergic_receptor"],
            "tramadol": ["Mu_opioid_receptor", "Serotonin_transporter"],
            "ultram": ["Mu_opioid_receptor", "Serotonin_transporter"],
            "tapentadol": ["Mu_opioid_receptor", "Norepinephrine_transporter"],
            "nucynta": ["Mu_opioid_receptor", "Norepinephrine_transporter"],
            "capsaicin": ["TRPV1"],
            "qutenza": ["TRPV1"],
            "lido_ointment": ["Sodium_Channel"],
            "aspirin": ["COX-1", "COX-2"],
            "ibuprofen": ["COX-1", "COX-2"],
            "naproxen": ["COX-1", "COX-2"],
            "celecoxib": ["COX-2"],
            "gabapentin_pain": ["Calcium_Channel_alpha2delta"],
            "pregabalin_pain": ["Calcium_Channel_alpha2delta"],
            
            # Huntington's disease drugs
            "tetrabenazine": ["VMAT2"],
            "xenazine": ["VMAT2"],
            "deutetrabenazine": ["VMAT2"],
            "austedo": ["VMAT2"],
            "valbenazine": ["VMAT2"],
            "ingrezza": ["VMAT2"],
        }
        
        # Disease to target mapping for drugs without specific target info
        self.disease_targets = {
            "multiple sclerosis": ["CD20", "S1P_receptor", "Integrin_alpha4", "Interferon_receptor"],
            "parkinson disease": ["Dopamine_Receptor_D2", "Monoamine_Oxidase_B", "COMT"],
            "epilepsy": ["Sodium_Channel", "GABA_Receptor", "Calcium_Channel"],
            "alzheimer disease": ["Acetylcholinesterase", "NMDA_receptor"],
            "migraine": ["Serotonin_Receptor_5HT1B", "CGRP_receptor"],
            "als": ["Glutamate_receptor"],
            "huntington disease": ["VMAT2"],
            "covid-19": ["3CL_protease", "Spike_protein"],
            "potassium channelopathy": ["Potassium_Channel"],
            "neuropathic pain": ["Calcium_Channel_alpha2delta", "Sodium_Channel"],
        }
    
    def get_targets_for_drug(self, drug_name: str, disease: str = None, 
                             mechanism: str = None) -> List[str]:
        """
        Get protein targets for a drug
        
        Args:
            drug_name: Name of the drug
            disease: Disease indication (optional)
            mechanism: Mechanism of action (optional)
            
        Returns:
            List of protein target names
        """
        # Clean drug name
        drug_lower = drug_name.lower().replace(" ", "_").replace("-", "_")
        
        # First, try exact match
        if drug_lower in self.drug_targets:
            return self.drug_targets[drug_lower]
        
        # Try partial matches
        for known_drug, targets in self.drug_targets.items():
            if known_drug in drug_lower or drug_lower in known_drug:
                return targets
        
        # If no drug match, try disease-based targets
        if disease:
            disease_lower = disease.lower()
            for known_disease, targets in self.disease_targets.items():
                if known_disease in disease_lower or disease_lower in known_disease:
                    return targets
        
        # If still no match, try to parse mechanism of action
        if mechanism:
            mechanism_lower = mechanism.lower()
            targets = []
            
            if any(word in mechanism_lower for word in ["sodium channel", "voltage-gated"]):
                targets.append("Sodium_Channel")
            if any(word in mechanism_lower for word in ["gaba", "gabaergic"]):
                targets.append("GABA_Receptor")
            if any(word in mechanism_lower for word in ["dopamine", "dopaminergic"]):
                targets.append("Dopamine_Receptor_D2")
            if any(word in mechanism_lower for word in ["serotonin", "5-ht"]):
                targets.append("Serotonin_Receptor_5HT1B")
            if any(word in mechanism_lower for word in ["acetylcholine", "cholinergic"]):
                targets.append("Acetylcholinesterase")
            if any(word in mechanism_lower for word in ["calcium channel"]):
                targets.append("Calcium_Channel")
            if any(word in mechanism_lower for word in ["potassium channel"]):
                targets.append("Potassium_Channel")
            if any(word in mechanism_lower for word in ["mao-b", "monoamine oxidase"]):
                targets.append("Monoamine_Oxidase_B")
            if any(word in mechanism_lower for word in ["interferon"]):
                targets.append("Interferon_receptor")
            if any(word in mechanism_lower for word in ["cd20", "b-cell"]):
                targets.append("CD20")
            
            if targets:
                return targets
        
        # Default: return empty list (will be handled as "Unknown")
        return []
    
    def update_dataset_with_targets(self, input_file: str, output_file: str = None):
        """Update a dataset file with protein targets"""
        # Read dataset
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract drugs
        if isinstance(data, dict) and 'drugs' in data:
            drugs = data['drugs']
            metadata = data.get('metadata', {})
            disease = metadata.get('disease', '')
        elif isinstance(data, list):
            drugs = data
            disease = ''
        else:
            print(f"[ERROR] Unknown format in {input_file}")
            return
        
        # Update each drug with targets
        updated_count = 0
        for drug in drugs:
            drug_name = drug.get('name', drug.get('drug_name', ''))
            mechanism = drug.get('mechanism_of_action', '')
            
            if drug_name:
                targets = self.get_targets_for_drug(drug_name, disease, mechanism)
                if targets:
                    drug['targets'] = targets
                    updated_count += 1
        
        # Save updated dataset
        if output_file is None:
            output_file = input_file
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Updated {updated_count}/{len(drugs)} drugs in {output_file}")
        return data


def main():
    """Update all datasets with protein targets"""
    import os
    
    print("="*70)
    print("UPDATING DATASETS WITH PROTEIN TARGETS")
    print("="*70)
    
    mapper = DrugTargetMapper()
    
    # Find all dataset files
    dataset_path = Path("D:/Datasets")
    if not dataset_path.exists():
        print(f"[ERROR] D:/Datasets/ not found!")
        return
    
    dataset_files = list(dataset_path.glob("*.json"))
    
    total_updated = 0
    total_drugs = 0
    
    for file_path in dataset_files:
        if file_path.name == "DATASET_SUMMARY.json":
            continue
        
        print(f"\n[Processing] {file_path.name}")
        try:
            # Create backup first
            backup_path = file_path.with_suffix('.json.backup')
            if not backup_path.exists():
                import shutil
                shutil.copy(file_path, backup_path)
            
            # Update with targets
            data = mapper.update_dataset_with_targets(str(file_path))
            
            # Count updated drugs
            if isinstance(data, dict) and 'drugs' in data:
                total_drugs += len(data['drugs'])
                updated = sum(1 for d in data['drugs'] if 'targets' in d and d['targets'])
            elif isinstance(data, list):
                total_drugs += len(data)
                updated = sum(1 for d in data if 'targets' in d and d['targets'])
            
            total_updated += updated
            
        except Exception as e:
            print(f"[ERROR] Failed to process {file_path.name}: {e}")
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total drugs processed: {total_drugs}")
    print(f"Drugs with targets added: {total_updated}")
    print(f"Coverage: {total_updated/total_drugs*100:.1f}%")
    print(f"\n[OK] All datasets updated with protein targets!")
    print(f"Backups created with .backup extension")


if __name__ == "__main__":
    main()
