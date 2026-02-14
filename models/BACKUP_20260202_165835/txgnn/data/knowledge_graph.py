"""
PrimeKG: Precision Medicine Knowledge Graph
Simplified implementation for TxGNN drug repurposing.

Contains:
- Symptoms (phenotypes)
- Diseases
- Proteins (genes)
- Drugs (chemicals)
- Relations between them
"""

import torch
import numpy as np
import json
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict


class PrimeKG:
    """
    Simplified PrimeKG knowledge graph for drug discovery.
    
    Node types:
    - symptom/phenotype
    - disease
    - protein/gene
    - drug
    
    Edge types (relations):
    - symptom_associated_with_disease
    - disease_associated_with_protein
    - protein_interacts_with_protein
    - drug_targets_protein
    - drug_treats_disease
    - drug_similar_to_drug
    """
    
    def __init__(self):
        # Node storage
        self.nodes: Dict[int, Dict] = {}  # node_id -> {name, type, attributes}
        self.node_name_to_id: Dict[str, int] = {}
        self.node_type_to_ids: Dict[str, List[int]] = defaultdict(list)
        
        # Edge storage
        self.edges: List[Tuple[int, int, int]] = []  # (source, target, relation_type)
        self.edge_index: torch.Tensor = None
        self.edge_type: torch.Tensor = None
        
        # Relation type mapping
        self.relation_types: Dict[str, int] = {
            'symptom_disease': 0,
            'disease_protein': 1,
            'protein_protein': 2,
            'drug_protein': 3,
            'drug_disease': 4,
            'drug_drug': 5
        }
        
        # Node ID counters
        self.next_node_id = 0
        
    def add_node(self, name: str, node_type: str, **attributes) -> int:
        """Add a node to the knowledge graph."""
        if name in self.node_name_to_id:
            return self.node_name_to_id[name]
        
        node_id = self.next_node_id
        self.next_node_id += 1
        
        self.nodes[node_id] = {
            'name': name,
            'type': node_type,
            'attributes': attributes
        }
        self.node_name_to_id[name] = node_id
        self.node_type_to_ids[node_type].append(node_id)
        
        return node_id
    
    def add_edge(self, source_name: str, target_name: str, relation: str):
        """Add an edge between two nodes."""
        if source_name not in self.node_name_to_id or target_name not in self.node_name_to_id:
            return
        
        source_id = self.node_name_to_id[source_name]
        target_id = self.node_name_to_id[target_name]
        relation_id = self.relation_types.get(relation, 0)
        
        self.edges.append((source_id, target_id, relation_id))
    
    def build_graph_tensors(self):
        """Convert edge list to PyTorch tensors."""
        if not self.edges:
            return
        
        edge_array = np.array(self.edges)
        source_nodes = edge_array[:, 0]
        target_nodes = edge_array[:, 1]
        relations = edge_array[:, 2]
        
        # Create edge_index [2, num_edges]
        self.edge_index = torch.tensor(
            np.stack([source_nodes, target_nodes]), 
            dtype=torch.long
        )
        
        # Create edge_type [num_edges]
        self.edge_type = torch.tensor(relations, dtype=torch.long)
    
    def get_node_id(self, name: str) -> Optional[int]:
        """Get node ID by name."""
        return self.node_name_to_id.get(name)
    
    def get_node_name(self, node_id: int) -> str:
        """Get node name by ID."""
        return self.nodes.get(node_id, {}).get('name', f'Node_{node_id}')
    
    def get_node_type(self, node_id: int) -> str:
        """Get node type by ID."""
        return self.nodes.get(node_id, {}).get('type', 'unknown')
    
    def get_nodes_by_type(self, node_type: str) -> List[int]:
        """Get all nodes of a specific type."""
        return self.node_type_to_ids[node_type]
    
    @property
    def num_nodes(self) -> int:
        return len(self.nodes)
    
    @property
    def num_edges(self) -> int:
        return len(self.edges)
    
    @property
    def num_relations(self) -> int:
        return len(self.relation_types)
    
    @property
    def drug_node_ids(self) -> List[int]:
        return self.node_type_to_ids['drug']
    
    @property
    def symptom_node_ids(self) -> List[int]:
        return self.node_type_to_ids['symptom']
    
    def save(self, filepath: str):
        """Save knowledge graph to JSON."""
        data = {
            'nodes': self.nodes,
            'edges': self.edges,
            'relation_types': self.relation_types,
            'node_name_to_id': self.node_name_to_id
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'PrimeKG':
        """Load knowledge graph from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        kg = cls()
        kg.nodes = {int(k): v for k, v in data['nodes'].items()}
        kg.edges = [tuple(e) for e in data['edges']]
        kg.relation_types = data['relation_types']
        kg.node_name_to_id = data['node_name_to_id']
        kg.node_type_to_ids = defaultdict(list)
        
        for node_id, node_data in kg.nodes.items():
            kg.node_type_to_ids[node_data['type']].append(node_id)
        
        kg.next_node_id = max(kg.nodes.keys()) + 1 if kg.nodes else 0
        kg.build_graph_tensors()
        
        return kg


def create_medical_knowledge_base() -> PrimeKG:
    """
    Create a simplified medical knowledge base with common drugs, diseases, 
    proteins, and symptoms. This is a demo dataset for testing.
    """
    kg = PrimeKG()
    
    # Add common symptoms (phenotypes)
    symptoms = [
        'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache',
        'muscle_pain', 'sore_throat', 'loss_of_taste', 'loss_of_smell',
        'nausea', 'diarrhea', 'chest_pain', 'chills', 'runny_nose',
        'sneezing', 'body_aches', 'congestion', 'difficulty_breathing',
        'wheezing', 'tight_chest'
    ]
    
    for symptom in symptoms:
        kg.add_node(symptom, 'symptom', category='phenotype')
    
    # Add diseases
    diseases = [
        'COVID-19', 'influenza', 'common_cold', 'pneumonia', 'bronchitis',
        'asthma', 'ARDS', 'SARS', 'MERS'
    ]
    
    for disease in diseases:
        kg.add_node(disease, 'disease', category='viral' if 'COVID' in disease or 'SARS' in disease or 'MERS' in disease or 'influenza' in disease else 'respiratory')
    
    # Add proteins (simplified - key targets for respiratory viruses)
    proteins = [
        'ACE2', 'TMPRSS2', '3CLpro', 'PLpro', 'RNA_polymerase',
        'spike_protein', 'M_protein', 'N_protein', 'IFN_gamma',
        'IL-6', 'TNF_alpha', 'IL-1_beta', 'NF_kappa_B'
    ]
    
    for protein in proteins:
        kg.add_node(protein, 'protein', category='viral' if protein in ['3CLpro', 'PLpro', 'RNA_polymerase', 'spike_protein', 'M_protein', 'N_protein'] else 'host')
    
    # Add drugs (known and repurposed)
    drugs = [
        # Antivirals
        'remdesivir', 'molnupiravir', 'paxlovid', 'favipiravir',
        # Anti-inflammatory
        'dexamethasone', 'prednisone', 'ibuprofen', 'acetaminophen',
        # Antibiotics (for secondary infections)
        'azithromycin', 'amoxicillin', 'doxycycline',
        # Anticoagulants
        'heparin', 'warfarin',
        # Other repurposed drugs
        'ivermectin', 'hydroxychloroquine', 'chloroquine',
        'colchicine', 'baricitinib', 'tocilizumab',
        # Symptomatic treatment
        'dextromethorphan', 'guaifenesin', 'loratadine', 'diphenhydramine'
    ]
    
    for drug in drugs:
        category = 'antiviral' if drug in ['remdesivir', 'molnupiravir', 'paxlovid', 'favipiravir'] else \
                   'anti_inflammatory' if drug in ['dexamethasone', 'prednisone', 'ibuprofen', 'acetaminophen'] else \
                   'antibiotic' if drug in ['azithromycin', 'amoxicillin', 'doxycycline'] else \
                   'anticoagulant' if drug in ['heparin', 'warfarin'] else \
                   'immunomodulator' if drug in ['baricitinib', 'tocilizumab', 'colchicine'] else \
                   'repurposed' if drug in ['ivermectin', 'hydroxychloroquine', 'chloroquine'] else \
                   'symptomatic'
        kg.add_node(drug, 'drug', category=category)
    
    # Create edges (relationships)
    # COVID-19 symptom associations
    covid_symptoms = ['fever', 'cough', 'fatigue', 'shortness_of_breath', 
                      'loss_of_taste', 'loss_of_smell', 'muscle_pain', 'headache',
                      'sore_throat', 'chills']
    
    for symptom in covid_symptoms:
        kg.add_edge(symptom, 'COVID-19', 'symptom_disease')
    
    # Influenza symptom associations
    flu_symptoms = ['fever', 'cough', 'fatigue', 'muscle_pain', 'headache',
                    'chills', 'runny_nose', 'sore_throat', 'body_aches']
    
    for symptom in flu_symptoms:
        kg.add_edge(symptom, 'influenza', 'symptom_disease')
    
    # Disease-protein associations (COVID-19)
    kg.add_edge('COVID-19', 'ACE2', 'disease_protein')
    kg.add_edge('COVID-19', 'TMPRSS2', 'disease_protein')
    kg.add_edge('COVID-19', '3CLpro', 'disease_protein')
    kg.add_edge('COVID-19', 'spike_protein', 'disease_protein')
    kg.add_edge('COVID-19', 'IL-6', 'disease_protein')
    
    # Disease-protein associations (Influenza)
    kg.add_edge('influenza', 'RNA_polymerase', 'disease_protein')
    kg.add_edge('influenza', 'IFN_gamma', 'disease_protein')
    
    # Protein-protein interactions
    kg.add_edge('ACE2', 'TMPRSS2', 'protein_protein')
    kg.add_edge('spike_protein', 'ACE2', 'protein_protein')
    kg.add_edge('IL-6', 'TNF_alpha', 'protein_protein')
    kg.add_edge('IL-6', 'IL-1_beta', 'protein_protein')
    
    # Drug-protein targets
    kg.add_edge('remdesivir', 'RNA_polymerase', 'drug_protein')
    kg.add_edge('paxlovid', '3CLpro', 'drug_protein')
    kg.add_edge('molnupiravir', 'RNA_polymerase', 'drug_protein')
    kg.add_edge('baricitinib', 'IL-6', 'drug_protein')
    kg.add_edge('tocilizumab', 'IL-6', 'drug_protein')
    kg.add_edge('dexamethasone', 'IL-6', 'drug_protein')
    kg.add_edge('hydroxychloroquine', 'ACE2', 'drug_protein')
    kg.add_edge('chloroquine', 'ACE2', 'drug_protein')
    kg.add_edge('azithromycin', 'IL-6', 'drug_protein')
    
    # Drug-disease treatments
    kg.add_edge('remdesivir', 'COVID-19', 'drug_disease')
    kg.add_edge('paxlovid', 'COVID-19', 'drug_disease')
    kg.add_edge('molnupiravir', 'COVID-19', 'drug_disease')
    kg.add_edge('dexamethasone', 'COVID-19', 'drug_disease')
    kg.add_edge('baricitinib', 'COVID-19', 'drug_disease')
    kg.add_edge('tocilizumab', 'COVID-19', 'drug_disease')
    
    # Build tensors
    kg.build_graph_tensors()
    
    return kg