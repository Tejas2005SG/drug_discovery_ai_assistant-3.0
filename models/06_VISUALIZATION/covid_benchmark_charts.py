"""
Professional COVID-19 Empirical Test Benchmark
Simple and clean visualization
"""

import matplotlib.pyplot as plt
import numpy as np

# Set clean style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('COVID-19 Empirical Test Results - NOVO-1 Knowledge Graph Model', 
             fontsize=16, fontweight='bold', y=0.98)

# 1. Overall Accuracy Score (Gauge-style)
ax1 = axes[0, 0]
categories = ['Your Model', 'Random\nBaseline', 'Industry\nStandard']
scores = [62.1, 25, 75]
colors = ['#2ecc71', '#e74c3c', '#3498db']
bars = ax1.bar(categories, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Accuracy Score (%)', fontweight='bold')
ax1.set_title('Overall System Accuracy', fontweight='bold', pad=10)
ax1.set_ylim(0, 100)
ax1.axhline(y=60, color='orange', linestyle='--', alpha=0.7, label='Good Threshold')
ax1.legend()

# Add value labels
for bar, score in zip(bars, scores):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{score}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

# 2. Test Case Performance
ax2 = axes[0, 1]
test_cases = ['Severe\nCOVID', 'Mild\nCOVID', 'Cytokine\nStorm', 'Moderate\nCOVID', 'Long\nCOVID', 'COVID+\nFlu']
performance = [77.1, 66.9, 61.2, 60.5, 57.0, 49.8]
colors2 = ['#27ae60' if p >= 60 else '#f39c12' if p >= 50 else '#e74c3c' for p in performance]

bars2 = ax2.barh(test_cases, performance, color=colors2, alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Accuracy Score (%)', fontweight='bold')
ax2.set_title('Performance by Test Case', fontweight='bold', pad=10)
ax2.set_xlim(0, 100)
ax2.axvline(x=60, color='orange', linestyle='--', alpha=0.7)

# Add value labels
for bar, perf in zip(bars2, performance):
    width = bar.get_width()
    ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
             f'{perf}%', ha='left', va='center', fontweight='bold', fontsize=10)

# 3. Key Metrics Dashboard
ax3 = axes[1, 0]
ax3.axis('off')

metrics_text = """
KEY METRICS

Overall Accuracy:      62.1%  (GOOD)
Chemical Validity:     100%   (EXCELLENT)
Target Match Rate:     52.9%  (GOOD)
Avg QED Score:         0.47   (FAIR)
Avg Confidence:        36.5%  (FAIR)

Total Candidates:      42
Valid Molecules:       42/42
Test Cases:            6
FDA Reference Drugs:   12
"""

ax3.text(0.5, 0.5, metrics_text, transform=ax3.transAxes, fontsize=11,
         verticalalignment='center', horizontalalignment='center',
         bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3, pad=1),
         family='monospace', fontweight='bold')

# 4. Accuracy Breakdown Pie Chart
ax4 = axes[1, 1]
components = ['Target Match\n(30%)', 'Validity\n(25%)', 'QED Score\n(25%)', 'Confidence\n(20%)']
values = [52.9, 100, 47.4, 36.5]
colors4 = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']

# Normalize to show contribution to final 62.1%
weights = [0.30, 0.25, 0.25, 0.20]
weighted_scores = [v * w for v, w in zip(values, weights)]

wedges, texts, autotexts = ax4.pie(weighted_scores, labels=components, autopct='%1.1f%%',
                                     colors=colors4, startangle=90,
                                     textprops={'fontsize': 9, 'fontweight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(10)

ax4.set_title('Accuracy Components\n(Weighted Contribution)', fontweight='bold', pad=10)

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig('C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models/covid_benchmark_professional.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: covid_benchmark_professional.png')
plt.close()

# Create simple summary chart
fig2, ax = plt.subplots(figsize=(10, 6))

# Simple bar chart comparing test cases
test_names = ['Severe COVID-19', 'Mild COVID-19', 'Cytokine Storm', 
              'Moderate COVID-19', 'Long COVID', 'COVID + Influenza']
scores = [77.1, 66.9, 61.2, 60.5, 57.0, 49.8]

# Color based on performance
colors = ['#27ae60' if s >= 70 else '#2ecc71' if s >= 60 else '#f39c12' if s >= 50 else '#e74c3c' for s in scores]

bars = ax.bar(range(len(test_names)), scores, color=colors, alpha=0.85, 
              edgecolor='black', linewidth=2)

ax.set_xticks(range(len(test_names)))
ax.set_xticklabels(test_names, rotation=30, ha='right')
ax.set_ylabel('Accuracy Score (%)', fontweight='bold', fontsize=12)
ax.set_title('COVID-19 Empirical Test: Accuracy by Scenario\nFinal Score: 62.1% (100% Validity, 42 Candidates Generated)', 
             fontweight='bold', fontsize=13, pad=20)

ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3, axis='y')
ax.axhline(y=60, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Good Threshold (60%)')
ax.legend(fontsize=11)

# Add score labels
for i, (bar, score) in enumerate(zip(bars, scores)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
            f'{score}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('C:/Users/Tejas/Desktop/drugs_discovery_ai_assistant/models/covid_simple_benchmark.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: covid_simple_benchmark.png')
plt.close()

print("\nCharts created successfully!")
print("Files:")
print("  - covid_benchmark_professional.png (4-panel detailed)")
print("  - covid_simple_benchmark.png (single clean chart)")
