"""
TxGNN: Therapeutics Graph Neural Network for Drug Repurposing
Implementation based on the paper by Zitnik Lab (Nature Medicine 2024)

This model predicts drug candidates from disease symptoms using a knowledge graph
and graph neural networks.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data, Batch
import numpy as np
from typing import List, Dict, Tuple, Optional


class TxGNN(nn.Module):
    """
    TxGNN Model for zero-shot drug repurposing from symptoms.
    
    Architecture:
    - Input: Knowledge graph with symptoms, diseases, proteins, and drugs as nodes
    - GNN layers: Propagate information through the graph
    - Output: Drug candidate scores for given symptoms
    """
    
    def __init__(
        self,
        num_nodes: int,
        num_relations: int,
        hidden_dim: int = 128,
        num_layers: int = 3,
        dropout: float = 0.3,
        num_drug_candidates: int = 100
    ):
        super(TxGNN, self).__init__()
        
        self.num_nodes = num_nodes
        self.num_relations = num_relations
        self.hidden_dim = hidden_dim
        self.num_drug_candidates = num_drug_candidates
        
        # Node embedding layer
        self.node_embedding = nn.Embedding(num_nodes, hidden_dim)
        
        # Relation embedding (for different edge types)
        self.relation_embedding = nn.Embedding(num_relations, hidden_dim)
        
        # GCN layers
        self.convs = nn.ModuleList()
        for i in range(num_layers):
            in_channels = hidden_dim if i == 0 else hidden_dim
            self.convs.append(GCNConv(in_channels, hidden_dim))
        
        # Batch normalization layers
        self.batch_norms = nn.ModuleList()
        for _ in range(num_layers):
            self.batch_norms.append(nn.BatchNorm1d(hidden_dim))
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Prediction head for drug scores
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1)
        )
        
    def forward(
        self, 
        x: torch.Tensor, 
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
        symptom_nodes: torch.Tensor,
        candidate_drugs: torch.Tensor
    ) -> torch.Tensor:
        """
        Forward pass of TxGNN.
        
        Args:
            x: Node features (or indices if using embedding)
            edge_index: Graph connectivity [2, num_edges]
            edge_type: Edge relation types [num_edges]
            symptom_nodes: Indices of symptom nodes [num_symptoms]
            candidate_drugs: Indices of candidate drug nodes [num_candidates]
            
        Returns:
            scores: Drug candidate scores [num_candidates]
        """
        # Get node embeddings
        h = self.node_embedding(x)
        
        # Apply GCN layers
        for conv, bn in zip(self.convs, self.batch_norms):
            h = conv(h, edge_index)
            h = bn(h)
            h = F.relu(h)
            h = self.dropout(h)
        
        # Aggregate symptom node representations (mean pooling)
        symptom_repr = h[symptom_nodes].mean(dim=0)  # [hidden_dim]
        
        # Get drug representations
        drug_reprs = h[candidate_drugs]  # [num_candidates, hidden_dim]
        
        # Expand symptom representation for concatenation
        symptom_expanded = symptom_repr.unsqueeze(0).expand(drug_reprs.size(0), -1)
        
        # Concatenate symptom and drug representations
        combined = torch.cat([symptom_expanded, drug_reprs], dim=-1)  # [num_candidates, hidden_dim*2]
        
        # Predict scores
        scores = self.predictor(combined).squeeze(-1)  # [num_candidates]
        
        return torch.sigmoid(scores)
    
    def predict_from_symptoms(
        self,
        knowledge_graph: 'PrimeKG',
        symptom_ids: List[int],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Predict drug candidates from a list of symptom IDs.
        
        Args:
            knowledge_graph: The PrimeKG knowledge graph instance
            symptom_ids: List of symptom node IDs
            top_k: Number of top predictions to return
            
        Returns:
            List of (drug_name, score) tuples
        """
        self.eval()
        with torch.no_grad():
            # Get all drug nodes as candidates
            candidate_drugs = torch.tensor(
                knowledge_graph.drug_node_ids, 
                dtype=torch.long
            )
            
            # Convert symptom IDs to tensor
            symptom_nodes = torch.tensor(symptom_ids, dtype=torch.long)
            
            # Get graph data
            edge_index = knowledge_graph.edge_index
            edge_type = knowledge_graph.edge_type
            x = torch.arange(self.num_nodes)
            
            # Forward pass
            scores = self.forward(x, edge_index, edge_type, symptom_nodes, candidate_drugs)
            
            # Get top-k predictions
            top_scores, top_indices = torch.topk(scores, min(top_k, len(scores)))
            
            # Map back to drug names
            results = []
            for idx, score in zip(top_indices, top_scores):
                drug_id = candidate_drugs[idx].item()
                drug_name = knowledge_graph.get_node_name(drug_id)
                results.append((drug_name, score.item()))
            
            return results


class SimpleTxGNN(nn.Module):
    """
    Simplified TxGNN for quick prototyping and testing.
    Uses a basic GCN architecture without relation-specific embeddings.
    """
    
    def __init__(
        self,
        num_nodes: int,
        hidden_dim: int = 64,
        num_layers: int = 2,
        dropout: float = 0.3
    ):
        super(SimpleTxGNN, self).__init__()
        
        self.node_embedding = nn.Embedding(num_nodes, hidden_dim)
        
        self.convs = nn.ModuleList()
        for i in range(num_layers):
            in_ch = hidden_dim if i == 0 else hidden_dim
            self.convs.append(GCNConv(in_ch, hidden_dim))
        
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x, edge_index, symptom_nodes, drug_nodes):
        h = self.node_embedding(x)
        
        for conv in self.convs:
            h = F.relu(conv(h, edge_index))
        
        # Aggregate symptom info
        symptom_repr = h[symptom_nodes].mean(dim=0)
        symptom_expanded = symptom_repr.unsqueeze(0).expand(len(drug_nodes), -1)
        
        # Drug representations
        drug_reprs = h[drug_nodes]
        
        # Combine and predict
        combined = torch.cat([symptom_expanded, drug_reprs], dim=-1)
        scores = self.predictor(combined).squeeze(-1)
        
        return scores