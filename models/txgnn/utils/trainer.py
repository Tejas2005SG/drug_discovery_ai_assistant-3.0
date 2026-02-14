"""
TxGNN Trainer: Training pipeline for drug repurposing model.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple, Dict
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from txgnn.models.txgnn import SimpleTxGNN
from txgnn.data.knowledge_graph import PrimeKG, create_medical_knowledge_base


class DrugSymptomDataset(Dataset):
    """Dataset for drug-symptom pairs with labels."""
    
    def __init__(self, kg: PrimeKG, num_negative_samples: int = 5):
        self.kg = kg
        self.num_negative_samples = num_negative_samples
        
        # Create positive pairs (drugs that treat diseases with symptoms)
        self.positive_pairs = []
        drug_to_diseases = {}
        disease_to_symptoms = {}
        
        for edge in kg.edges:
            src, dst, rel = edge
            src_data = kg.nodes[src]
            dst_data = kg.nodes[dst]
            rel_name = [k for k, v in kg.relation_types.items() if v == rel][0]
            
            # Build drug -> disease mapping (drug treats disease)
            if src_data['type'] == 'drug' and rel_name == 'drug_disease':
                if src not in drug_to_diseases:
                    drug_to_diseases[src] = []
                drug_to_diseases[src].append(dst)
            
            # Build disease -> symptom mapping (symptom associated with disease)
            if src_data['type'] == 'symptom' and dst_data['type'] == 'disease':
                if dst not in disease_to_symptoms:
                    disease_to_symptoms[dst] = []
                disease_to_symptoms[dst].append(src)
        
        # Create positive drug-symptom pairs via disease associations
        for drug_id, diseases in drug_to_diseases.items():
            for disease_id in diseases:
                if disease_id in disease_to_symptoms:
                    for symptom_id in disease_to_symptoms[disease_id]:
                        self.positive_pairs.append((drug_id, symptom_id, 1.0))
        
        # Generate negative pairs
        self.negative_pairs = []
        drug_ids = [n for n, d in kg.nodes.items() if d['type'] == 'drug']
        symptom_ids = [n for n, d in kg.nodes.items() if d['type'] == 'symptom']
        
        for drug_id in drug_ids:
            for symptom_id in symptom_ids:
                is_negative = True
                for src, dst, rel in kg.edges:
                    if (src == drug_id and dst == symptom_id) or (dst == drug_id and src == symptom_id):
                        is_negative = False
                        break
                if is_negative:
                    self.negative_pairs.append((drug_id, symptom_id, 0.0))
        
        # Combine and shuffle
        self.all_pairs = self.positive_pairs + self.negative_pairs
        np.random.shuffle(self.all_pairs)
        
        print(f"Created dataset: {len(self.positive_pairs)} positive, {len(self.negative_pairs)} negative pairs")
    
    def __len__(self):
        return len(self.all_pairs)
    
    def __getitem__(self, idx):
        drug_id, symptom_id, label = self.all_pairs[idx]
        return int(drug_id), int(symptom_id), float(label)


class TxGNNTrainer:
    """Trainer for TxGNN model."""
    
    def __init__(
        self,
        kg: PrimeKG = None,
        hidden_dim: int = 64,
        num_layers: int = 2,
        dropout: float = 0.3,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-5,
        device: str = None
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if device is None else torch.device(device)
        
        if kg is None:
            print("Creating knowledge base...")
            self.kg = create_medical_knowledge_base()
        else:
            self.kg = kg
        
        print(f"Knowledge graph: {self.kg.num_nodes} nodes, {self.kg.num_edges} edges")
        
        # Initialize model
        self.model = SimpleTxGNN(
            num_nodes=self.kg.num_nodes,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout
        ).to(self.device)
        
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # Create dataset
        self.dataset = DrugSymptomDataset(self.kg)
        
    def train_epoch(self, dataloader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for drug_ids, symptom_ids, labels in dataloader:
            drug_ids = drug_ids.to(self.device)
            symptom_ids = symptom_ids.to(self.device)
            labels = labels.to(self.device).float()  # Convert to float
            
            self.optimizer.zero_grad()
            
            # Forward pass
            scores = self.model(
                torch.arange(self.kg.num_nodes, device=self.device),
                self.kg.edge_index.to(self.device),
                symptom_ids,
                drug_ids
            )
            
            loss = self.criterion(scores, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        return total_loss / num_batches
    
    def evaluate(self, dataloader: DataLoader) -> Dict[str, float]:
        """Evaluate model on dataset."""
        self.model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for drug_ids, symptom_ids, labels in dataloader:
                drug_ids = drug_ids.to(self.device)
                symptom_ids = symptom_ids.to(self.device)
                labels = labels.to(self.device).float()  # Convert to float
                
                scores = self.model(
                    torch.arange(self.kg.num_nodes, device=self.device),
                    self.kg.edge_index.to(self.device),
                    symptom_ids,
                    drug_ids
                )
                
                preds = (scores > 0.5).float()
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        
        # Calculate metrics
        accuracy = np.mean(all_preds == all_labels)
        precision = np.mean(all_preds[all_labels == 1] == 1) if np.sum(all_labels == 1) > 0 else 0
        recall = np.mean(all_preds[all_labels == 1] == 1) if np.sum(all_labels == 1) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def train(self, num_epochs: int = 100, batch_size: int = 32, eval_every: int = 10) -> Dict:
        """Train the model for specified epochs."""
        print(f"\n{'='*60}")
        print("STARTING TxGNN TRAINING")
        print(f"{'='*60}")
        print(f"Device: {self.device}")
        print(f"Epochs: {num_epochs}")
        print(f"Batch size: {batch_size}")
        print(f"{'='*60}\n")
        
        # Create dataloader
        dataloader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
        )
        
        history = {'loss': [], 'accuracy': [], 'precision': [], 'recall': [], 'f1': []}
        best_f1 = 0.0
        
        for epoch in range(num_epochs):
            # Train
            loss = self.train_epoch(dataloader)
            
            # Evaluate
            if (epoch + 1) % eval_every == 0 or epoch == 0:
                metrics = self.evaluate(dataloader)
                metrics['loss'] = loss
                
                for key in history:
                    history[key].append(metrics[key])
                
                print(f"Epoch {epoch+1:3d}/{num_epochs} | Loss: {loss:.4f} | "
                      f"Acc: {metrics['accuracy']:.3f} | Prec: {metrics['precision']:.3f} | "
                      f"Rec: {metrics['recall']:.3f} | F1: {metrics['f1']:.3f}")
                
                # Save best model
                if metrics['f1'] > best_f1:
                    best_f1 = metrics['f1']
                    self.save_model('best_model.pt')
                    print(f"  -> New best model saved! (F1: {best_f1:.3f})")
        
        # Final evaluation
        final_metrics = self.evaluate(dataloader)
        print(f"\n{'='*60}")
        print("TRAINING COMPLETE")
        print(f"{'='*60}")
        print(f"Final Accuracy: {final_metrics['accuracy']:.4f}")
        print(f"Final Precision: {final_metrics['precision']:.4f}")
        print(f"Final Recall: {final_metrics['recall']:.4f}")
        print(f"Final F1 Score: {final_metrics['f1']:.4f}")
        
        return history
    
    def save_model(self, path: str):
        """Save model weights."""
        save_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        torch.save(self.model.state_dict(), save_path)
        print(f"Model saved to: {save_path}")
    
    def load_model(self, path: str):
        """Load model weights."""
        load_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', path)
        self.model.load_state_dict(torch.load(load_path, map_location=self.device))
        print(f"Model loaded from: {load_path}")


def quick_train_example():
    """Run a quick training example."""
    print("=" * 60)
    print("TxGNN Quick Training Example")
    print("=" * 60)
    
    trainer = TxGNNTrainer(
        hidden_dim=64,
        num_layers=2,
        learning_rate=0.01,
        weight_decay=1e-5
    )
    
    # Train for 50 epochs
    history = trainer.train(num_epochs=50, batch_size=16, eval_every=10)
    
    return history


if __name__ == "__main__":
    quick_train_example()
