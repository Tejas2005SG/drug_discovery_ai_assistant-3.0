# NOVO-1 Drug Discovery AI v3.0
## Hackathon Ready - 66% Accuracy on COVID-19

---

## Quick Start

### Run Drug Discovery
```bash
python run_discovery.py
```

### Run COVID-19 Accuracy Test
```bash
python 04_TESTING/covid_empirical_test_v3.py
```
**Expected Accuracy: 66-67%**

---

## Project Structure

```
models/
├── 01_CORE_SYSTEM/          # Core AI modules (8 files)
│   ├── novo1_enhanced_system.py      # Main system
│   ├── knowledge_graph.py            # TransE embeddings
│   ├── protein_database.py           # 76 proteins
│   ├── admet_predictor.py            # ADMET predictions
│   └── google_drive_manager.py       # Cloud storage
├── 02_DATASETS/             # Dataset management
├── 03_TRAINING/             # Training scripts
├── 04_TESTING/              # Test suites (12 files)
│   └── covid_empirical_test_v3.py    # Main COVID test
├── 05_RESULTS/              # Training & test outputs
├── 06_VISUALIZATION/        # Charts & graphs
├── 07_DOCUMENTATION/        # Documentation
├── 08_ARCHIVE/              # Backup files
├── run_discovery.py         # Main entry point
└── requirements.txt         # Dependencies
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Accuracy** | 66% on COVID-19 |
| **Dataset** | 158 FDA-approved drugs |
| **Training Time** | 8 minutes (CPU) |
| **Candidates** | 3-7 per query |
| **Validity Rate** | 100% |

---

## Key Features

- Knowledge Graph with TransE embeddings
- ADMET property predictions
- Protein target identification
- RDKit molecular analysis
- CPU-optimized (no GPU needed)
- Professional accuracy reports

---

## System Requirements

- Python 3.8+
- RDKit
- NumPy, Matplotlib, Pandas
- 8GB RAM minimum
- See requirements.txt

---

## Hackathon Submission

This project demonstrates AI-driven drug discovery with:
- **66% accuracy** validated against FDA-approved drugs
- **Real clinical relevance** for COVID-19 treatment
- **Novel drug candidate generation** for any symptoms
- **Comprehensive ADMET analysis**

**Datasets:** D:/Datasets/ (01_chembl_core_drugs.json + 02_neurological_drugs_100.json)

---

## Contact

For questions or issues, please refer to IMPLEMENTATION_GUIDE.md
