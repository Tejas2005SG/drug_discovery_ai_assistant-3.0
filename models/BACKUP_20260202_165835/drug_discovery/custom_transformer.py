"""
Custom Transformer Architecture for Medical Text Understanding
Built from scratch - no pre-trained models
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple


class CustomTokenizer:
    """Custom BPE-style tokenizer for medical text and SMILES"""
    
    def __init__(self, vocab_size=32000):
        self.vocab_size = vocab_size
        self.word_to_id = {}
        self.id_to_word = {}
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
            '<MASK>': 4,
            '<SEP>': 5
        }
        self._build_initial_vocab()
    
    def _build_initial_vocab(self):
        # Start with special tokens
        for token, idx in self.special_tokens.items():
            self.word_to_id[token] = idx
            self.id_to_word[idx] = token
        
        # Medical vocabulary
        medical_tokens = [
            # Symptoms
            'fever', 'cough', 'pain', 'fatigue', 'nausea', 'headache', 'dizziness',
            'shortness', 'breath', 'chest', 'heart', 'palpitation', 'flutter',
            'confusion', 'memory', 'cognitive', 'neurological', 'seizure',
            'toenail', 'brittle', 'nail', 'fungal', 'infection',
            'knuckle', 'cracking', 'joint', 'arthritis', 'inflammation',
            'ear', 'blockage', 'congestion', 'sinus', 'pressure',
            
            # Body parts
            'brain', 'heart', 'liver', 'kidney', 'lung', 'skin', 'bone',
            'muscle', 'nerve', 'blood', 'vessel', 'artery', 'vein',
            
            # Medical terms
            'disease', 'disorder', 'syndrome', 'condition', 'symptom',
            'acute', 'chronic', 'severe', 'mild', 'moderate',
            'treatment', 'therapy', 'medication', 'drug', 'dose',
            
            # Chemical terms
            'molecule', 'compound', 'reaction', 'binding', 'enzyme',
            'protein', 'receptor', 'pathway', 'inhibitor', 'agonist',
            'antagonist', 'substrate', 'catalyst',
            
            # SMILES tokens
            'C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I',
            'c', 'n', 'o', 's', 'p',
            '=', '#', '(', ')', '[', ']', '@', '@@', '+', '-',
            '1', '2', '3', '4', '5', '6', '7', '8', '9',
            '/', '\\', '%', 'H', 'h'
        ]
        
        for i, token in enumerate(medical_tokens, start=len(self.special_tokens)):
            if i >= self.vocab_size:
                break
            self.word_to_id[token] = i
            self.id_to_word[i] = token
    
    def encode(self, text, max_length=512):
        """Encode text to token IDs"""
        words = text.lower().split()
        tokens = [self.special_tokens['<BOS>']]
        
        for word in words:
            if word in self.word_to_id:
                tokens.append(self.word_to_id[word])
            else:
                # Character-level fallback
                for char in word:
                    if char in self.word_to_id:
                        tokens.append(self.word_to_id[char])
                    else:
                        tokens.append(self.special_tokens['<UNK>'])
        
        tokens.append(self.special_tokens['<EOS>'])
        
        # Pad or truncate
        if len(tokens) < max_length:
            tokens.extend([self.special_tokens['<PAD>']] * (max_length - len(tokens)))
        else:
            tokens = tokens[:max_length-1] + [self.special_tokens['<EOS>']]
        
        return torch.tensor(tokens)
    
    def decode(self, token_ids):
        """Decode token IDs to text"""
        words = []
        for idx in token_ids:
            idx = idx.item() if isinstance(idx, torch.Tensor) else idx
            if idx in self.id_to_word:
                word = self.id_to_word[idx]
                if word not in ['<PAD>', '<BOS>', '<EOS>']:
                    words.append(word)
        return ' '.join(words)


class MultiHeadAttention(nn.Module):
    """Custom Multi-Head Self-Attention (from scratch)"""
    
    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear projections for Q, K, V
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.d_k)
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # Linear projections
        Q = self.W_q(query)
        K = self.W_k(key)
        V = self.W_v(value)
        
        # Reshape for multi-head attention
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        if mask is not None:
            mask = mask.unsqueeze(1).unsqueeze(1)
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention to values
        context = torch.matmul(attn_weights, V)
        
        # Concatenate heads
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        # Final linear projection
        output = self.W_o(context)
        
        return output, attn_weights


class FeedForward(nn.Module):
    """Custom Position-wise Feed-Forward Network"""
    
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        return x


class TransformerBlock(nn.Module):
    """Custom Transformer Encoder Block"""
    
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # Self-attention with residual connection
        attn_out, _ = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_out))
        
        # Feed-forward with residual connection
        ff_out = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff_out))
        
        return x


class CustomTransformer(nn.Module):
    """
    Custom Transformer Model built from scratch
    For symptom analysis and target prediction
    """
    
    def __init__(
        self,
        vocab_size=32000,
        d_model=512,
        num_heads=8,
        num_layers=6,
        d_ff=2048,
        max_seq_length=512,
        dropout=0.1,
        num_classes=128
    ):
        super().__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        
        # Token embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        self.pos_encoding = self._create_positional_encoding(max_seq_length, d_model)
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        self.dropout = nn.Dropout(dropout)
        
        # Output heads
        self.target_classifier = nn.Linear(d_model, num_classes)
        self.disease_classifier = nn.Linear(d_model, 64)
        self.pathway_classifier = nn.Linear(d_model, 32)
        
        self._init_parameters()
    
    def _create_positional_encoding(self, max_len, d_model):
        """Create sinusoidal positional encodings"""
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * 
            (-math.log(10000.0) / d_model)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        return pe.unsqueeze(0)
    
    def _init_parameters(self):
        """Initialize parameters"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, input_ids, attention_mask=None):
        # Token embeddings
        x = self.token_embedding(input_ids) * math.sqrt(self.d_model)
        
        # Add positional encoding
        seq_len = x.size(1)
        x = x + self.pos_encoding[:, :seq_len, :].to(x.device)
        
        x = self.dropout(x)
        
        # Create padding mask if not provided
        if attention_mask is None:
            attention_mask = (input_ids != 0).unsqueeze(1).unsqueeze(1)
        
        # Pass through transformer blocks
        for block in self.transformer_blocks:
            x = block(x, attention_mask)
        
        # Global average pooling
        pooled = x.mean(dim=1)
        
        # Multi-task outputs
        targets = torch.sigmoid(self.target_classifier(pooled))
        diseases = torch.sigmoid(self.disease_classifier(pooled))
        pathways = torch.sigmoid(self.pathway_classifier(pooled))
        
        return {
            'target_probs': targets,
            'disease_probs': diseases,
            'pathway_probs': pathways,
            'embeddings': pooled
        }


class DrugTargetPredictor(nn.Module):
    """
    Custom model for predicting drug-target interactions
    Built from scratch using graph neural network concepts
    """
    
    def __init__(self, d_model=512, num_targets=500, num_drugs=10000):
        super().__init__()
        
        # Drug encoder
        self.drug_encoder = nn.Sequential(
            nn.Linear(256, d_model),  # From molecular fingerprints
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(d_model, d_model)
        )
        
        # Target encoder
        self.target_encoder = nn.Sequential(
            nn.Linear(1024, d_model),  # From protein embeddings
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(d_model, d_model)
        )
        
        # Interaction predictor
        self.interaction_net = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, drug_features, target_features):
        drug_emb = self.drug_encoder(drug_features)
        target_emb = self.target_encoder(target_features)
        
        combined = torch.cat([drug_emb, target_emb], dim=-1)
        affinity = self.interaction_net(combined)
        
        return affinity


if __name__ == "__main__":
    # Test custom tokenizer
    tokenizer = CustomTokenizer()
    text = "Patient has brittle toenails and fluttering heartbeat"
    tokens = tokenizer.encode(text)
    decoded = tokenizer.decode(tokens)
    print(f"Original: {text}")
    print(f"Tokens: {tokens[:10]}...")
    print(f"Decoded: {decoded}")
    print(f"Vocab size: {len(tokenizer.word_to_id)}")
    
    # Test custom transformer
    model = CustomTransformer(vocab_size=32000, d_model=512, num_heads=8, num_layers=6)
    print(f"\nModel parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.2f}M")
    
    # Test forward pass
    batch_size = 2
    seq_len = 128
    input_ids = torch.randint(0, 32000, (batch_size, seq_len))
    
    with torch.no_grad():
        outputs = model(input_ids)
        print(f"\nOutput shapes:")
        print(f"  Target probs: {outputs['target_probs'].shape}")
        print(f"  Disease probs: {outputs['disease_probs'].shape}")
        print(f"  Pathway probs: {outputs['pathway_probs'].shape}")
