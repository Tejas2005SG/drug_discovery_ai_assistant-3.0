"""
Custom Molecular VAE - Built from scratch
Generates novel drug molecules as SMILES strings
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class SMILESEncoder:
    """Custom SMILES tokenizer and encoder"""
    
    def __init__(self):
        # SMILES vocabulary
        self.vocab = [
            '<PAD>', '<START>', '<END>', '<UNK>',
            'C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I',
            'c', 'n', 'o', 's', 'p',
            '=', '#', '(', ')', '[', ']',
            '@', '@@', '+', '-', 'H', 'h',
            '1', '2', '3', '4', '5', '6', '7', '8', '9',
            '/', '\\', '%', '.', ':'
        ]
        self.char_to_idx = {c: i for i, c in enumerate(self.vocab)}
        self.idx_to_char = {i: c for i, c in enumerate(self.vocab)}
        self.vocab_size = len(self.vocab)
        self.max_len = 100
    
    def encode(self, smiles):
        """SMILES string to indices"""
        indices = [self.char_to_idx['<START>']]
        for char in smiles:
            if char in self.char_to_idx:
                indices.append(self.char_to_idx[char])
            else:
                indices.append(self.char_to_idx['<UNK>'])
        indices.append(self.char_to_idx['<END>'])
        
        # Pad
        while len(indices) < self.max_len:
            indices.append(self.char_to_idx['<PAD>'])
        indices = indices[:self.max_len]
        
        return torch.tensor(indices, dtype=torch.long)
    
    def decode(self, indices):
        """Indices to SMILES string"""
        chars = []
        for idx in indices:
            if idx == self.char_to_idx['<END>']:
                break
            if idx not in [self.char_to_idx['<PAD>'], self.char_to_idx['<START>']]:
                chars.append(self.idx_to_char.get(idx.item(), '?'))
        return ''.join(chars)


class MolecularEncoder(nn.Module):
    """Encodes SMILES to latent space"""
    
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256, latent_dim=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2, batch_first=True, bidirectional=True)
        self.fc_mu = nn.Linear(hidden_dim * 2, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim * 2, latent_dim)
    
    def forward(self, x):
        x = self.embedding(x)
        _, (h, _) = self.lstm(x)
        h = torch.cat([h[-2], h[-1]], dim=-1)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar


class MolecularDecoder(nn.Module):
    """Decodes latent vector to SMILES"""
    
    def __init__(self, latent_dim, hidden_dim=256, vocab_size=45):
        super().__init__()
        self.latent_to_hidden = nn.Linear(latent_dim, hidden_dim)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, num_layers=2, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, z, max_len=100):
        batch_size = z.size(0)
        h = self.latent_to_hidden(z).unsqueeze(1).repeat(1, max_len, 1)
        out, _ = self.lstm(h)
        logits = self.fc(out)
        return logits


class MolecularVAE(nn.Module):
    """
    Complete VAE for molecular generation
    Built from scratch
    """
    
    def __init__(self, vocab_size=45, latent_dim=128):
        super().__init__()
        self.encoder = MolecularEncoder(vocab_size, latent_dim=latent_dim)
        self.decoder = MolecularDecoder(latent_dim, vocab_size=vocab_size)
        self.latent_dim = latent_dim
    
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def forward(self, x):
        mu, logvar = self.encoder(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decoder(z, max_len=x.size(1))
        return recon, mu, logvar
    
    def generate(self, num_samples=10, device='cpu'):
        """Generate new molecules"""
        self.eval()
        with torch.no_grad():
            z = torch.randn(num_samples, self.latent_dim).to(device)
            logits = self.decoder(z, max_len=100)
            samples = torch.argmax(logits, dim=-1)
        return samples
    
    def loss_function(self, recon, target, mu, logvar):
        """VAE loss"""
        recon_loss = F.cross_entropy(recon.view(-1, recon.size(-1)), target.view(-1), ignore_index=0)
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / target.size(0)
        return recon_loss + 0.1 * kl_loss


if __name__ == "__main__":
    # Test
    encoder = SMILESEncoder()
    test_smiles = "CC(C)Cc1ccc(cc1)C(C)C(=O)O"
    encoded = encoder.encode(test_smiles)
    print(f"Encoded shape: {encoded.shape}")
    print(f"Vocab size: {encoder.vocab_size}")
    
    vae = MolecularVAE(vocab_size=encoder.vocab_size, latent_dim=128)
    print(f"VAE parameters: {sum(p.numel() for p in vae.parameters()) / 1e6:.2f}M")
    
    # Test generation
    generated = vae.generate(num_samples=3)
    for i, seq in enumerate(generated):
        smiles = encoder.decode(seq)
        print(f"Generated {i+1}: {smiles}")
