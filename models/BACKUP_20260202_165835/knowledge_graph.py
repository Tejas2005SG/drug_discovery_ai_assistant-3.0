"""
Drug Repurposing Knowledge Graph (DRKG-based)
Symptom-driven drug discovery using knowledge graph embeddings
Optimized for CPU training (no GPU required)
"""

import numpy as np
import json
import pickle
from collections import defaultdict, Counter
from pathlib import Path
import random

class DrugRepurposingKnowledgeGraph:
    """
    Knowledge Graph for Symptom-Driven Drug Discovery
    
    Entities: Diseases, Symptoms, Drugs, Proteins, Side Effects
    Relations: has_symptom, treated_by, targets, has_side_effect
    """
    
    def __init__(self, drive_manager=None):
        """
        Initialize knowledge graph
        
        Args:
            drive_manager: GoogleDriveManager instance for storage
        """
        self.drive_manager = drive_manager
        
        # Entities
        self.diseases = {}  # disease_id -> {name, symptoms, drugs}
        self.symptoms = {}  # symptom_id -> name
        self.drugs = {}     # drug_id -> {name, smiles, targets, indications}
        self.proteins = {}  # protein_id -> name
        
        # Relations (stored as triples: head, relation, tail)
        self.triples = []  # [(head, relation, tail), ...]
        
        # Embeddings (will be computed)
        self.entity_embeddings = {}
        self.relation_embeddings = {}
        
        print("="*70)
        print("DRUG REPURPOSING KNOWLEDGE GRAPH")
        print("="*70)
        
    def build_from_data(self, disease_data, drug_data):
        """
        Build knowledge graph from curated data
        
        Args:
            disease_data: List of disease dicts with symptoms
            drug_data: List of drug dicts with targets
        """
        print("\n[BUILDING KNOWLEDGE GRAPH]")
        
        # Add diseases and symptoms
        for disease in disease_data:
            disease_id = f"DISEASE_{len(self.diseases)}"
            self.diseases[disease_id] = {
                'name': disease['name'],
                'symptoms': [],
                'drugs': []
            }
            
            # Add symptoms and relations
            for symptom_name in disease['symptoms']:
                symptom_id = self._get_or_create_symptom(symptom_name)
                self.triples.append((disease_id, 'has_symptom', symptom_id))
                self.diseases[disease_id]['symptoms'].append(symptom_id)
        
        # Add drugs and relations
        for drug in drug_data:
            drug_id = f"DRUG_{len(self.drugs)}"
            self.drugs[drug_id] = {
                'name': drug['name'],
                'smiles': drug.get('smiles', ''),
                'targets': [],
                'indications': drug.get('indications', [])
            }
            
            # Add protein targets
            for protein_name in drug.get('targets', []):
                protein_id = self._get_or_create_protein(protein_name)
                self.triples.append((drug_id, 'targets', protein_id))
                self.drugs[drug_id]['targets'].append(protein_id)
            
            # Add disease indications (treated_by relation)
            for indication in drug.get('indications', []):
                # Find disease by name
                for dis_id, dis_data in self.diseases.items():
                    if dis_data['name'].lower() == indication.lower():
                        self.triples.append((dis_id, 'treated_by', drug_id))
                        self.diseases[dis_id]['drugs'].append(drug_id)
                        break
        
        print(f"[OK] Added {len(self.diseases)} diseases")
        print(f"[OK] Added {len(self.symptoms)} symptoms")
        print(f"[OK] Added {len(self.drugs)} drugs")
        print(f"[OK] Added {len(self.proteins)} proteins")
        print(f"[OK] Created {len(self.triples)} triples")
        
    def _get_or_create_symptom(self, symptom_name):
        """Get existing symptom ID or create new one"""
        for sym_id, name in self.symptoms.items():
            if name.lower() == symptom_name.lower():
                return sym_id
        
        # Create new symptom
        sym_id = f"SYMPTOM_{len(self.symptoms)}"
        self.symptoms[sym_id] = symptom_name
        return sym_id
    
    def _get_or_create_protein(self, protein_name):
        """Get existing protein ID or create new one"""
        for prot_id, name in self.proteins.items():
            if name.lower() == protein_name.lower():
                return prot_id
        
        # Create new protein
        prot_id = f"PROTEIN_{len(self.proteins)}"
        self.proteins[prot_id] = protein_name
        return prot_id
    
    def train_embeddings_cpu(self, dim=100, epochs=500, lr=0.001, negative_samples=5):
        """
        Train knowledge graph embeddings using TransE
        CPU-friendly implementation (no GPU needed!)
        Fixed version with proper gradient clipping
        
        Args:
            dim: Embedding dimension (50-200)
            epochs: Training iterations (500-2000)
            lr: Learning rate (0.001-0.01)
            negative_samples: Number of negative samples per positive
        """
        print(f"\n[TRAINING KG EMBEDDINGS ON CPU]")
        print(f"  Dimension: {dim}")
        print(f"  Epochs: {epochs}")
        print(f"  Learning Rate: {lr}")
        print(f"  Negative Samples: {negative_samples}")
        
        # Initialize embeddings randomly with normalization
        all_entities = list(self.diseases.keys()) + list(self.symptoms.keys()) + \
                      list(self.drugs.keys()) + list(self.proteins.keys())
        all_relations = list(set([rel for _, rel, _ in self.triples]))
        
        # Initialize with small random values and normalize
        self.entity_embeddings = {}
        for e in all_entities:
            emb = np.random.randn(dim).astype(np.float32)
            emb = emb / (np.linalg.norm(emb) + 1e-8)  # Normalize
            self.entity_embeddings[e] = emb
            
        self.relation_embeddings = {}
        for r in all_relations:
            emb = np.random.randn(dim).astype(np.float32)
            emb = emb / (np.linalg.norm(emb) + 1e-8)  # Normalize
            self.relation_embeddings[r] = emb
        
        # Training loop
        print("\n[TRAINING PROGRESS]")
        for epoch in range(epochs):
            total_loss = 0
            
            # Sample random batch of triples
            batch_size = min(64, len(self.triples))
            batch = random.sample(self.triples, batch_size)
            
            for head, relation, tail in batch:
                # Get embeddings
                h_emb = self.entity_embeddings[head].copy()
                r_emb = self.relation_embeddings[relation].copy()
                t_emb = self.entity_embeddings[tail].copy()
                
                # Calculate positive score (L2 distance)
                pos_dist = h_emb + r_emb - t_emb
                pos_score = np.linalg.norm(pos_dist)
                
                # Generate negative sample
                if random.random() < 0.5:
                    # Corrupt head
                    neg_head = random.choice(all_entities)
                    neg_h_emb = self.entity_embeddings[neg_head].copy()
                    
                    neg_dist = neg_h_emb + r_emb - t_emb
                    neg_score = np.linalg.norm(neg_dist)
                    
                    # TransE loss: max(0, gamma + pos_score - neg_score)
                    gamma = 1.0
                    loss = max(0, gamma + pos_score - neg_score)
                    total_loss += loss
                    
                    # Update only if violation
                    if loss > 0:
                        # Normalize gradients
                        if pos_score > 0:
                            grad_pos = pos_dist / pos_score
                        else:
                            grad_pos = pos_dist
                            
                        if neg_score > 0:
                            grad_neg = neg_dist / neg_score
                        else:
                            grad_neg = neg_dist
                        
                        # Update with gradient clipping
                        grad_clip = 1.0
                        grad_pos = np.clip(grad_pos, -grad_clip, grad_clip)
                        grad_neg = np.clip(grad_neg, -grad_clip, grad_clip)
                        
                        # Apply updates
                        self.entity_embeddings[head] -= lr * grad_pos
                        self.entity_embeddings[neg_head] += lr * grad_neg
                        
                        # Renormalize to prevent explosion
                        self.entity_embeddings[head] = self._normalize(self.entity_embeddings[head])
                        self.entity_embeddings[neg_head] = self._normalize(self.entity_embeddings[neg_head])
                else:
                    # Corrupt tail
                    neg_tail = random.choice(all_entities)
                    neg_t_emb = self.entity_embeddings[neg_tail].copy()
                    
                    neg_dist = h_emb + r_emb - neg_t_emb
                    neg_score = np.linalg.norm(neg_dist)
                    
                    gamma = 1.0
                    loss = max(0, gamma + pos_score - neg_score)
                    total_loss += loss
                    
                    if loss > 0:
                        if pos_score > 0:
                            grad_pos = pos_dist / pos_score
                        else:
                            grad_pos = pos_dist
                            
                        if neg_score > 0:
                            grad_neg = neg_dist / neg_score
                        else:
                            grad_neg = neg_dist
                        
                        grad_clip = 1.0
                        grad_pos = np.clip(grad_pos, -grad_clip, grad_clip)
                        grad_neg = np.clip(grad_neg, -grad_clip, grad_clip)
                        
                        self.entity_embeddings[tail] -= lr * grad_pos
                        self.entity_embeddings[neg_tail] += lr * grad_neg
                        
                        self.entity_embeddings[tail] = self._normalize(self.entity_embeddings[tail])
                        self.entity_embeddings[neg_tail] = self._normalize(self.entity_embeddings[neg_tail])
            
            if epoch % 50 == 0:
                avg_loss = total_loss / len(batch)
                print(f"  Epoch {epoch:4d}/{epochs}: Loss = {avg_loss:.4f}")
        
        print("\n[OK] Training complete!")
    
    def _normalize(self, vec):
        """Normalize vector to unit length"""
        norm = np.linalg.norm(vec)
        if norm > 0:
            return vec / norm
        return vec
        
    def find_diseases_by_symptoms(self, symptom_names, top_k=5):
        """
        Find diseases matching symptom profile
        
        Args:
            symptom_names: List of symptom strings
            top_k: Number of top matches to return
            
        Returns:
            List of (disease_id, similarity_score) tuples
        """
        # First, find exact symptom matches
        matched_symptoms = []
        for sym_name in symptom_names:
            sym_name_lower = sym_name.lower()
            for sym_id, name in self.symptoms.items():
                if sym_name_lower in name.lower() or name.lower() in sym_name_lower:
                    matched_symptoms.append(sym_id)
        
        if not matched_symptoms:
            return []
        
        # Score diseases by number of matching symptoms
        disease_scores = {}
        for dis_id, dis_data in self.diseases.items():
            disease_symptoms = set(dis_data['symptoms'])
            matched_count = len(disease_symptoms.intersection(set(matched_symptoms)))
            
            if matched_count > 0:
                # Calculate score based on match ratio and embedding similarity
                match_ratio = matched_count / len(symptom_names)
                
                # Add embedding similarity if available
                emb_sim = 0.0
                if self.entity_embeddings and dis_id in self.entity_embeddings:
                    # Average symptom embedding
                    sym_embs = [self.entity_embeddings[s] for s in matched_symptoms if s in self.entity_embeddings]
                    if sym_embs:
                        query_emb = np.mean(sym_embs, axis=0)
                        query_emb = query_emb / (np.linalg.norm(query_emb) + 1e-8)
                        
                        dis_emb = self.entity_embeddings[dis_id]
                        dis_emb = dis_emb / (np.linalg.norm(dis_emb) + 1e-8)
                        
                        emb_sim = np.dot(query_emb, dis_emb)
                        # Convert to 0-1 range
                        emb_sim = (emb_sim + 1) / 2
                
                # Combined score: 70% symptom match, 30% embedding similarity
                combined_score = 0.7 * match_ratio + 0.3 * emb_sim
                disease_scores[dis_id] = combined_score
        
        # Sort by score
        sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_diseases[:top_k]
    
    def get_drugs_for_disease(self, disease_id, top_k=5):
        """Get drugs that treat a specific disease"""
        if disease_id not in self.diseases:
            return []
        
        drug_ids = self.diseases[disease_id]['drugs']
        
        # Score drugs by embedding similarity to disease
        scored_drugs = []
        for drug_id in drug_ids:
            if drug_id in self.entity_embeddings and disease_id in self.entity_embeddings:
                drug_emb = self.entity_embeddings[drug_id]
                dis_emb = self.entity_embeddings[disease_id]
                
                sim = np.dot(drug_emb, dis_emb) / (np.linalg.norm(drug_emb) * np.linalg.norm(dis_emb) + 1e-8)
                scored_drugs.append((drug_id, float(sim)))
        
        scored_drugs.sort(key=lambda x: x[1], reverse=True)
        return scored_drugs[:top_k]
    
    def save_to_drive(self, filename='knowledge_graph.pkl'):
        """Save knowledge graph to Google Drive"""
        if self.drive_manager:
            data = {
                'diseases': self.diseases,
                'symptoms': self.symptoms,
                'drugs': self.drugs,
                'proteins': self.proteins,
                'triples': self.triples,
                'entity_embeddings': self.entity_embeddings,
                'relation_embeddings': self.relation_embeddings
            }
            self.drive_manager.save_dataset(data, filename, format='pkl')
    
    def load_from_drive(self, filename='knowledge_graph.pkl'):
        """Load knowledge graph from Google Drive"""
        if self.drive_manager:
            data = self.drive_manager.load_dataset(filename, format='pkl')
            if data:
                self.diseases = data['diseases']
                self.symptoms = data['symptoms']
                self.drugs = data['drugs']
                self.proteins = data['proteins']
                self.triples = data['triples']
                self.entity_embeddings = data['entity_embeddings']
                self.relation_embeddings = data['relation_embeddings']
                print("[OK] Knowledge graph loaded from Google Drive")
                return True
        return False
    
    def get_statistics(self):
        """Get knowledge graph statistics"""
        return {
            'num_diseases': len(self.diseases),
            'num_symptoms': len(self.symptoms),
            'num_drugs': len(self.drugs),
            'num_proteins': len(self.proteins),
            'num_triples': len(self.triples),
            'has_embeddings': len(self.entity_embeddings) > 0
        }


# Example usage
if __name__ == "__main__":
    # Sample data for testing
    disease_data = [
        {
            'name': 'COVID-19',
            'symptoms': ['fever', 'cough', 'shortness of breath', 'fatigue']
        },
        {
            'name': 'Multiple Sclerosis',
            'symptoms': ['neural inflammation', 'tremors', 'fatigue', 'muscle weakness']
        },
        {
            'name': 'Influenza',
            'symptoms': ['fever', 'cough', 'muscle pain', 'chills']
        }
    ]
    
    drug_data = [
        {
            'name': 'Paxlovid',
            'smiles': 'CC(C)(C)NC(=O)C1CC2(CCN(C(=O)C(C(C)(C)C)NC(=O)C(F)(F)F)CC2)CN1C(=O)O',
            'targets': ['3CL_protease'],
            'indications': ['COVID-19']
        },
        {
            'name': 'Ocrevus',
            'smiles': 'CC[C@H]1C[C@@H]2C[C@H]3C4=C(CCN3C2=O)C(=O)C5=C4C=CC=C5O1',
            'targets': ['CD20'],
            'indications': ['Multiple Sclerosis']
        },
        {
            'name': 'Ibuprofen',
            'smiles': 'CC(C)Cc1ccc(cc1)C(C)C(=O)O',
            'targets': ['COX-1', 'COX-2'],
            'indications': ['Influenza', 'Multiple Sclerosis']
        }
    ]
    
    # Create and build knowledge graph
    kg = DrugRepurposingKnowledgeGraph()
    kg.build_from_data(disease_data, drug_data)
    
    # Train embeddings (CPU only!)
    kg.train_embeddings_cpu(dim=50, epochs=500, lr=0.01)
    
    # Test query
    print("\n[TEST QUERY]")
    test_symptoms = ['fever', 'cough']
    matched_diseases = kg.find_diseases_by_symptoms(test_symptoms, top_k=3)
    
    print(f"\nSymptoms: {test_symptoms}")
    print("Matched diseases:")
    for dis_id, score in matched_diseases:
        dis_name = kg.diseases[dis_id]['name']
        print(f"  - {dis_name} (score: {score:.3f})")
        
        # Get drugs for this disease
        drugs = kg.get_drugs_for_disease(dis_id, top_k=2)
        for drug_id, drug_score in drugs:
            drug_name = kg.drugs[drug_id]['name']
            print(f"      -> {drug_name} (relevance: {drug_score:.3f})")
