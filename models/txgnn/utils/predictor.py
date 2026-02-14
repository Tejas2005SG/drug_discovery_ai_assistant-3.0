"""
TxGNN Predictor: Main interface for drug candidate prediction from symptoms.
"""

import torch
import torch.nn.functional as F
from typing import List, Dict, Tuple, Optional
import sys
import os
# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from txgnn.models.txgnn import SimpleTxGNN
from txgnn.data.knowledge_graph import PrimeKG, create_medical_knowledge_base
from txgnn.utils.trainer import TxGNNTrainer


class TxGNNPredictor:
    """
    Main interface for TxGNN drug repurposing predictions.
    
    Usage:
        predictor = TxGNNPredictor()
        symptoms = ['fever', 'cough', 'fatigue']
        predictions = predictor.predict_drugs(symptoms, top_k=10)
    """
    
    def __init__(self, knowledge_graph: Optional[PrimeKG] = None, model_path: Optional[str] = None):
        """
        Initialize the predictor.
        
        Args:
            knowledge_graph: Pre-loaded PrimeKG instance (or None to create default)
            model_path: Path to saved model weights (or None for random init)
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Load or create knowledge graph
        if knowledge_graph is None:
            print("Creating medical knowledge base...")
            self.kg = create_medical_knowledge_base()
        else:
            self.kg = knowledge_graph
        
        print(f"Knowledge graph: {self.kg.num_nodes} nodes, {self.kg.num_edges} edges")
        
        # Initialize model
        self.model = SimpleTxGNN(
            num_nodes=self.kg.num_nodes,
            hidden_dim=64,
            num_layers=2,
            dropout=0.3
        ).to(self.device)
        
        # Load weights if provided
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print(f"Loaded model weights from {model_path}")
        else:
            print("Initialized model with random weights (not trained)")
        
        self.model.eval()
    
    def train(self, num_epochs: int = 100, batch_size: int = 32) -> dict:
        """
        Train the TxGNN model on the knowledge graph.
        
        Args:
            num_epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history dictionary
        """
        trainer = TxGNNTrainer(
            knowledge_graph=self.kg,
            hidden_dim=64,
            num_layers=2,
            learning_rate=0.01,
            weight_decay=1e-5
        )
        
        history = trainer.train(num_epochs=num_epochs, batch_size=batch_size, eval_every=10)
        
        self.model.load_state_dict(trainer.model.state_dict())
        self.model.eval()
        
        return history
    
    def predict_drugs(
        self, 
        symptoms: List[str], 
        top_k: int = 10,
        verbose: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Predict drug candidates from a list of symptoms.
        
        Args:
            symptoms: List of symptom names (e.g., ['fever', 'cough'])
            top_k: Number of top predictions to return
            verbose: Whether to print progress
            
        Returns:
            List of (drug_name, confidence_score) tuples, sorted by score
        """
        if verbose:
            print(f"\nPredicting drugs for symptoms: {symptoms}")
        
        # Get symptom node IDs
        symptom_ids = []
        for symptom in symptoms:
            node_id = self.kg.get_node_id(symptom)
            if node_id is not None:
                symptom_ids.append(node_id)
            elif verbose:
                print(f"  Warning: Symptom '{symptom}' not found in knowledge graph")
        
        if not symptom_ids:
            if verbose:
                print("  No valid symptoms found!")
            return []
        
        if verbose:
            print(f"  Found {len(symptom_ids)} symptom nodes in graph")
        
        # Convert to tensors
        symptom_tensor = torch.tensor(symptom_ids, dtype=torch.long, device=self.device)
        drug_tensor = torch.tensor(self.kg.drug_node_ids, dtype=torch.long, device=self.device)
        edge_index = self.kg.edge_index.to(self.device)
        x = torch.arange(self.kg.num_nodes, device=self.device)
        
        # Run prediction
        with torch.no_grad():
            scores = self.model(x, edge_index, symptom_tensor, drug_tensor)
        
        # Get top-k predictions
        scores_cpu = scores.cpu()
        top_scores, top_indices = torch.topk(scores_cpu, min(top_k, len(scores_cpu)))
        
        results = []
        for idx, score in zip(top_indices, top_scores):
            drug_id = self.kg.drug_node_ids[idx.item()]
            drug_name = self.kg.get_node_name(drug_id)
            results.append((drug_name, score.item()))
        
        if verbose:
            print(f"\nTop {len(results)} predicted drug candidates:")
            print("-" * 50)
            for i, (drug, score) in enumerate(results, 1):
                bar = "=" * int(score * 20)
                print(f"{i:2d}. {drug:25s} | {score:.3f} | {bar}")
            print("-" * 50)
        
        return results
    
    def get_symptom_suggestions(self, partial_symptom: str) -> List[str]:
        """Get symptom suggestions based on partial input."""
        partial = partial_symptom.lower()
        suggestions = []
        
        for node_id, node_data in self.kg.nodes.items():
            if node_data['type'] == 'symptom':
                name = node_data['name']
                if partial in name.lower():
                    suggestions.append(name)
        
        return suggestions
    
    def explain_prediction(
        self, 
        drug_name: str, 
        symptoms: List[str]
    ) -> Dict:
        """
        Explain why a drug was predicted for given symptoms.
        Shows the path: symptoms -> disease -> protein -> drug
        """
        drug_id = self.kg.get_node_id(drug_name)
        symptom_ids = [self.kg.get_node_id(s) for s in symptoms if self.kg.get_node_id(s)]
        
        explanation = {
            'drug': drug_name,
            'symptoms': symptoms,
            'paths': []
        }
        
        # Find paths through the graph (simplified)
        for edge in self.kg.edges:
            src, dst, rel = edge
            if dst == drug_id and rel == 3:  # drug_protein relation
                protein = self.kg.get_node_name(src)
                explanation['paths'].append({
                    'type': 'drug_targets',
                    'protein': protein
                })
        
        return explanation


def demo_prediction():
    """Run a demo prediction with example symptoms."""
    print("=" * 60)
    print("TxGNN Drug Repurposing Prediction Demo")
    print("=" * 60)
    
    # Initialize predictor
    predictor = TxGNNPredictor()
    
    # Example symptoms for respiratory infection
    symptoms = ['fever', 'cough', 'fatigue', 'shortness_of_breath']
    
    # Get predictions
    predictions = predictor.predict_drugs(symptoms, top_k=10)
    
    return predictions


if __name__ == "__main__":
    demo_prediction()