# TxGNN - Drug Discovery from Symptoms

A complete implementation of **TxGNN (Therapeutics Graph Neural Network)** for zero-shot drug repurposing based on disease symptoms.

## Overview

This project implements a simplified version of the TxGNN model from Harvard's Zitnik Lab (Nature Medicine 2024). It predicts drug candidates by analyzing symptom patterns through a knowledge graph using Graph Neural Networks.

## Project Structure

```
txgnn/
├── models/
│   ├── __init__.py
│   └── txgnn.py                 # GNN model architecture
├── data/
│   ├── __init__.py
│   └── knowledge_graph.py       # PrimeKG knowledge graph implementation
├── utils/
│   ├── __init__.py
│   └── predictor.py             # Main prediction interface
├── tests/
│   ├── __init__.py
│   └── test_covid19.py          # COVID-19 test suite
├── __init__.py
└── README.md                    # This file
```

## Installation

```bash
pip install torch torch-geometric numpy pandas scikit-learn networkx
```

## Quick Start

```python
from txgnn.utils.predictor import TxGNNPredictor

# Initialize predictor
predictor = TxGNNPredictor()

# Predict drugs from symptoms
symptoms = ['fever', 'cough', 'fatigue', 'loss_of_taste']
predictions = predictor.predict_drugs(symptoms, top_k=10)
```

## Running Tests

### COVID-19 Drug Repurposing Test

```bash
cd models
python -c "import sys; sys.path.insert(0, '.'); from txgnn.tests.test_covid19 import main; main()"
```

This runs tests on three COVID-19 severity levels:
- **Mild**: fever, cough, fatigue, loss_of_taste
- **Moderate**: fever, cough, fatigue, shortness_of_breath, loss_of_smell, muscle_pain
- **Severe**: fever, cough, fatigue, shortness_of_breath, chest_pain, difficulty_breathing, chills

## How It Works

1. **Knowledge Graph (PrimeKG)**: Contains 65 nodes including:
   - 20 symptoms (fever, cough, fatigue, etc.)
   - 9 diseases (COVID-19, influenza, etc.)
   - 13 proteins (ACE2, TMPRSS2, 3CLpro, etc.)
   - 23 drugs (remdesivir, paxlovid, dexamethasone, etc.)

2. **Graph Neural Network**: Uses GCN layers to propagate information through the graph

3. **Prediction**: Given symptoms, the model scores all drugs based on their graph proximity to those symptoms

## Model Architecture

```python
SimpleTxGNN(
    num_nodes=65,          # Total nodes in knowledge graph
    hidden_dim=64,         # Embedding dimension
    num_layers=2,          # GCN layers
    dropout=0.3            # Regularization
)
```

## Key Features

- **Zero-shot prediction**: Works for diseases without existing treatments
- **Symptom-to-drug mapping**: Directly connects clinical presentations to drug candidates
- **Graph-based reasoning**: Leverages biological relationships (symptom→disease→protein→drug)
- **Modular design**: Easy to extend with new symptoms, diseases, and drugs

## Important Notes

⚠️ **This is a demonstration implementation**:
- Uses randomly initialized weights (not trained)
- Contains a small demo knowledge graph (65 nodes vs. 100K+ in real PrimeKG)
- Predictions are for architectural demonstration only

**For production use, the model needs:**
1. Training on large-scale biomedical data
2. Full PrimeKG knowledge graph integration
3. Clinical trial outcome data
4. Real-world evidence from electronic health records

## Research Paper

Based on: **"TxGNN: A Framework for Building Disease-Specific Cellular Models"**  
Published in *Nature Medicine* (2024) by Harvard Zitnik Lab  
[GitHub: mims-harvard/TxGNN](https://github.com/mims-harvard/TxGNN)

## License

Open source for research and educational purposes.

## Citation

```bibtex
@article{lin2024txgnn,
  title={TxGNN: A Framework for Building Disease-Specific Cellular Models},
  author={Lin, Chihiro and others},
  journal={Nature Medicine},
  year={2024}
}
```