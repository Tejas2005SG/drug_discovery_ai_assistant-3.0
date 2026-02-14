# TxGNN Visualization Guide

Complete guide for using TxGNN with Matplotlib visualizations and accuracy metrics.

## Installation

```bash
# Install required packages
pip install torch torch-geometric matplotlib seaborn numpy pandas scikit-learn networkx
```

Or use the requirements.txt:
```bash
pip install -r requirements.txt
```

## Quick Start (3 Ways)

### 1. Quick Demo (1 line)
```bash
cd models
python -c "import sys; sys.path.insert(0, '.'); from txgnn.tests.visualization_example import quick_visualization_example; quick_visualization_example()"
```

### 2. Full Visualization with All Metrics
```bash
cd models
python txgnn/tests/visualization_example.py
# Then select option 1
```

### 3. Interactive Python
```python
import sys
sys.path.insert(0, '.')

from txgnn.utils.predictor import TxGNNPredictor
from txgnn.utils.visualization import TxGNNVisualizer

# Initialize
predictor = TxGNNPredictor()
visualizer = TxGNNVisualizer(save_dir="my_results")

# Predict
symptoms = ['fever', 'cough', 'fatigue']
predictions = predictor.predict_drugs(symptoms, top_k=10)

# Calculate metrics
ground_truth = ['paxlovid', 'remdesivir', 'molnupiravir']
metrics = visualizer.calculate_metrics(predictions, ground_truth)

# Print metrics
visualizer.print_metrics_table(metrics, "My Test")

# Create visualization
visualizer.plot_top_predictions(
    predictions, 
    ground_truth,
    title="My Predictions",
    save_path="my_chart.png"
)
```

## Understanding the Metrics

### Precision@K
- **What**: Of the top K predictions, how many are actually effective
- **Example**: Precision@5 = 0.6 means 3 out of top 5 drugs are correct
- **Best for**: Ensuring high-confidence predictions are accurate

### Recall@K
- **What**: Of all effective drugs, how many are in top K predictions
- **Example**: Recall@10 = 0.5 means we found 50% of known treatments in top 10
- **Best for**: Finding as many effective drugs as possible

### MRR (Mean Reciprocal Rank)
- **What**: Average of 1/rank for the first correct prediction
- **Example**: MRR = 0.5 means first correct drug is at rank 2
- **Best for**: Overall ranking quality

### NDCG (Normalized Discounted Cumulative Gain)
- **What**: Measures ranking quality considering position
- **Higher scores** mean effective drugs appear higher in the list
- **Best for**: Overall quality of ranked list

### HitRate@K
- **What**: Binary - did we find ANY correct drug in top K?
- **Values**: 0 (no) or 1 (yes)
- **Best for**: Quick success check

## Available Visualizations

### 1. Top Predictions Chart
Shows drug scores with ground truth highlighted.
```python
visualizer.plot_top_predictions(
    predictions,
    ground_truth,
    title="Top Drug Predictions",
    top_k=15,
    save_path="predictions.png"
)
```
**Output**: Horizontal bar chart with:
- Green bars = Known effective treatments
- Red bars = Not in ground truth
- Score labels on each bar

### 2. Accuracy Metrics Comparison
Compares metrics across multiple test cases.
```python
test_cases = {
    'Mild': predictions_mild,
    'Moderate': predictions_mod,
    'Severe': predictions_sev
}

metrics_dict = {}
for case, preds in test_cases.items():
    metrics_dict[case] = visualizer.calculate_metrics(preds, ground_truth)

visualizer.plot_accuracy_metrics(
    metrics_dict,
    title="Accuracy Comparison",
    save_path="metrics.png"
)
```
**Output**: 4 subplots showing:
- Precision@K comparison (bars)
- Recall@K comparison (bars)
- F1 Score comparison (bars)
- Overall metrics heatmap

### 3. Symptom Importance Analysis
Shows which symptom combinations give best predictions.
```python
symptom_predictions = {
    'Fever+Cough': preds1,
    'Fever+Cough+Fatigue': preds2,
    'All Symptoms': preds3
}

visualizer.plot_symptom_importance(
    symptom_predictions,
    ground_truth,
    save_path="symptoms.png"
)
```
**Output**: 2 plots:
- Precision comparison by symptom set
- Radar chart of average metrics

## Complete Example

```python
import sys
sys.path.insert(0, '.')

from txgnn.utils.predictor import TxGNNPredictor
from txgnn.utils.visualization import TxGNNVisualizer

# Initialize
predictor = TxGNNPredictor()
visualizer = TxGNNVisualizer(save_dir="results")

# Define test cases
test_cases = {
    'Mild COVID': ['fever', 'cough', 'fatigue'],
    'Severe COVID': ['fever', 'cough', 'fatigue', 'shortness_of_breath']
}

# Ground truth drugs
ground_truth = ['paxlovid', 'remdesivir', 'molnupiravir', 'dexamethasone']

# Run tests and collect results
all_predictions = {}
all_metrics = {}

for name, symptoms in test_cases.items():
    # Get predictions
    preds = predictor.predict_drugs(symptoms, top_k=15, verbose=False)
    all_predictions[name] = preds
    
    # Calculate metrics
    metrics = visualizer.calculate_metrics(preds, ground_truth)
    all_metrics[name] = metrics
    
    # Print table
    visualizer.print_metrics_table(metrics, name)

# Create visualizations
visualizer.plot_accuracy_metrics(all_metrics, save_path="comparison.png")

for name, preds in all_predictions.items():
    visualizer.plot_top_predictions(
        preds, 
        ground_truth,
        title=f"{name} Predictions",
        save_path=f"{name.lower().replace(' ', '_')}.png"
    )

# Generate JSON report
report = visualizer.create_report(
    all_predictions,
    ground_truth,
    report_path="full_report.json"
)

print("\nAll visualizations saved to 'results/' directory!")
```

## Output Files

After running, you'll find in `results/` (or your chosen directory):

```
results/
├── accuracy_comparison.png      # Metrics comparison chart
├── predictions_covid-19_*.png   # Individual prediction charts
├── symptom_importance.png       # Symptom analysis
└── covid19_accuracy_report.json # Full metrics report
```

## Interpreting Results

### Good Performance Indicators:
- **Precision@5 > 0.6**: At least 3 of top 5 are correct
- **Recall@10 > 0.5**: Found 50% of known treatments in top 10
- **MRR > 0.3**: First correct prediction in top 3
- **NDCG > 0.5**: Good overall ranking quality

### What to Check:
1. Are known drugs appearing in top predictions?
2. Do more symptoms improve accuracy?
3. Which symptoms give best results?

## Customizing Visualizations

### Change Plot Style
```python
import matplotlib.pyplot as plt

# Change colors
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#FF6B6B', '#4ECDC4', '#45B7D1'])

# Change size
plt.rcParams['figure.figsize'] = (16, 10)
```

### Change Save Location
```python
visualizer = TxGNNVisualizer(save_dir="my_custom_folder")
```

### Change K Values for Metrics
```python
metrics = visualizer.calculate_metrics(
    predictions, 
    ground_truth, 
    k_values=[3, 5, 10, 20]  # Custom K values
)
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'txgnn'"
**Solution**: Make sure you're running from the `models/` directory and have added the path:
```python
import sys
sys.path.insert(0, '.')
```

### Issue: Plots not displaying
**Solution**: Add `plt.show()` at the end of your script or use `save_path` parameter.

### Issue: Low accuracy scores
**Note**: The demo model uses random weights (not trained). Real accuracy requires training on PrimeKG (100K+ nodes).

## Available Symptoms

```python
fever, cough, fatigue, shortness_of_breath, headache, muscle_pain, 
sore_throat, loss_of_taste, loss_of_smell, nausea, diarrhea, 
chest_pain, chills, runny_nose, sneezing, body_aches, congestion, 
difficulty_breathing, wheezing, tight_chest
```

## Available Drugs in Knowledge Graph

```python
remdesivir, molnupiravir, paxlovid, favipiravir, dexamethasone, 
prednisone, ibuprofen, acetaminophen, azithromycin, amoxicillin, 
doxycycline, heparin, warfarin, ivermectin, hydroxychloroquine, 
chloroquine, colchicine, baricitinib, tocilizumab, dextromethorphan, 
guaifenesin, loratadine, diphenhydramine
```

## Next Steps

1. **Try different symptom combinations** - See which give best predictions
2. **Add your own drugs** - Extend the knowledge graph
3. **Train the model** - Use real data for accurate predictions
4. **Compare with other models** - See how TxGNN performs vs others

## Citation

Based on: **"TxGNN: A Framework for Building Disease-Specific Cellular Models"**  
Published in *Nature Medicine* (2024) by Harvard Zitnik Lab