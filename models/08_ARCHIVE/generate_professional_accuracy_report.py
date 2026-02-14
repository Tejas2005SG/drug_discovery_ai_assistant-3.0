"""
Professional COVID-19 Accuracy Report Generator
Creates publication-quality accuracy visualization
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np

# Load the empirical test results
results_file = Path("05_RESULTS/test_results/covid_empirical_test_results.json")

with open(results_file, 'r') as f:
    results = json.load(f)

# Extract data
test_names = [r['test_name'] for r in results['per_test_results']]
accuracies = [r['overall_score'] * 100 for r in results['per_test_results']]
qed_scores = [r['avg_qed'] * 100 for r in results['per_test_results']]
confidence_scores = [r['avg_confidence'] * 100 for r in results['per_test_results']]
validity_rates = [r['validity'] * 100 for r in results['per_test_results']]

overall_accuracy = results['summary']['overall_score'] * 100
old_model_accuracy = 45.1

# Create professional figure
fig = plt.figure(figsize=(16, 10))
fig.suptitle('NOVO-1 Drug Discovery System - COVID-19 Empirical Test Results', 
             fontsize=18, fontweight='bold', y=0.98)

# Create grid layout
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# 1. Overall Accuracy Comparison (Top Left)
ax1 = fig.add_subplot(gs[0, 0])
models = ['Previous\nModel', 'NOVO-1 v3.0\n(Enhanced)']
accuracies_compare = [old_model_accuracy, overall_accuracy]
colors_compare = ['#e74c3c', '#27ae60']

bars = ax1.bar(models, accuracies_compare, color=colors_compare, width=0.6, edgecolor='black', linewidth=2)

# Add value labels on bars
for bar, acc in zip(bars, accuracies_compare):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=14)

ax1.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax1.set_title('Overall Accuracy Improvement', fontsize=14, fontweight='bold', pad=15)
ax1.set_ylim(0, 100)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Add improvement annotation
improvement = overall_accuracy - old_model_accuracy
ax1.annotate(f'+{improvement:.1f}%\nimprovement', 
            xy=(1, overall_accuracy), xytext=(1.3, overall_accuracy - 5),
            arrowprops=dict(arrowstyle='->', color='green', lw=2),
            fontsize=11, fontweight='bold', color='green',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8))

# 2. Test Scenario Performance (Top Right)
ax2 = fig.add_subplot(gs[0, 1])
colors_scenarios = ['#3498db', '#9b59b6', '#e67e22', '#1abc9c', '#f39c12', '#e74c3c']

bars2 = ax2.barh(test_names, accuracies, color=colors_scenarios, edgecolor='black', linewidth=1.5)

# Add value labels
for bar, acc in zip(bars2, accuracies):
    width = bar.get_width()
    ax2.text(width + 1, bar.get_y() + bar.get_height()/2, 
            f'{acc:.1f}%', ha='left', va='center', fontweight='bold', fontsize=10)

ax2.set_xlabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax2.set_title('Accuracy by Test Scenario', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlim(0, 100)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# 3. Detailed Metrics Breakdown (Middle - spans both columns)
ax3 = fig.add_subplot(gs[1, :])
x = np.arange(len(test_names))
width = 0.2

bars1 = ax3.bar(x - 1.5*width, accuracies, width, label='Overall Accuracy', color='#3498db', edgecolor='black')
bars2 = ax3.bar(x - 0.5*width, qed_scores, width, label='Drug-Likeness (QED)', color='#9b59b6', edgecolor='black')
bars3 = ax3.bar(x + 0.5*width, confidence_scores, width, label='Confidence Score', color='#e67e22', edgecolor='black')
bars4 = ax3.bar(x + 1.5*width, validity_rates, width, label='Chemical Validity', color='#27ae60', edgecolor='black')

ax3.set_xlabel('Test Scenarios', fontsize=12, fontweight='bold')
ax3.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
ax3.set_title('Comprehensive Metrics Breakdown', fontsize=14, fontweight='bold', pad=15)
ax3.set_xticks(x)
ax3.set_xticklabels(test_names, rotation=15, ha='right')
ax3.legend(loc='upper right', fontsize=10, framealpha=0.9)
ax3.set_ylim(0, 110)
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# 4. Key Statistics Summary (Bottom Left)
ax4 = fig.add_subplot(gs[2, 0])
ax4.axis('off')

stats_text = f"""
TEST SUMMARY STATISTICS

Total Test Cases: {results['summary']['total_test_cases']}
Total Candidates Generated: {results['summary']['total_candidates']}
Chemical Validity Rate: {results['summary']['validity_rate']*100:.1f}%

AVERAGE SCORES:
• Overall Accuracy: {results['summary']['overall_score']*100:.1f}%
• Drug-Likeness (QED): {results['summary']['avg_qed']*100:.1f}%
• Confidence Score: {results['summary']['avg_confidence']*100:.1f}%
• Target Match: {results['summary']['avg_target_match']*100:.1f}%

PERFORMANCE vs BASELINE:
• Previous Model: 45.1%
• Current Model: {overall_accuracy:.1f}%
• Improvement: +{improvement:.1f} percentage points
• Relative Gain: +{(improvement/old_model_accuracy)*100:.1f}%

STATUS: {results['interpretation']}
"""

ax4.text(0.1, 0.95, stats_text, transform=ax4.transAxes, fontsize=11,
        verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.8))

# 5. Success Rate Gauge (Bottom Right)
ax5 = fig.add_subplot(gs[2, 1])

# Create gauge chart
theta = np.linspace(0, np.pi, 100)
r = 1.0

# Background arc
ax5.fill_between(np.cos(theta), np.sin(theta), 0, alpha=0.1, color='gray')

# Success zone (green)
success_theta = theta[int(overall_accuracy):]
if len(success_theta) > 0:
    ax5.fill_between(np.cos(success_theta), np.sin(success_theta), 0, alpha=0.3, color='green')

# Accuracy indicator
acc_theta = np.pi * (1 - overall_accuracy/100)
ax5.annotate('', xy=(np.cos(acc_theta), np.sin(acc_theta)), xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color='red', lw=4))

# Add labels
ax5.text(0, -0.3, f'{overall_accuracy:.1f}%', ha='center', va='center', 
        fontsize=24, fontweight='bold', color='red')
ax5.text(0, -0.6, 'Overall Accuracy', ha='center', va='center', 
        fontsize=12, fontweight='bold')

ax5.set_xlim(-1.2, 1.2)
ax5.set_ylim(-0.8, 1.2)
ax5.axis('off')
ax5.set_title('Accuracy Gauge', fontsize=14, fontweight='bold', pad=15)

# Add footer
fig.text(0.5, 0.02, f'Generated: {results["date"]} | System: {results["system"]} | Test: COVID-19 Empirical Validation', 
        ha='center', fontsize=10, style='italic', 
        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))

# Save figure
chart_file = '06_VISUALIZATION/charts/covid_accuracy_report_v3_professional.png'
plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"[OK] Professional accuracy report saved to: {chart_file}")

# Also save summary
summary_file = '05_RESULTS/test_results/accuracy_report_summary_v3.json'
summary = {
    'date': results['date'],
    'system': results['system'],
    'overall_accuracy': overall_accuracy,
    'old_model_accuracy': old_model_accuracy,
    'improvement': improvement,
    'relative_gain_percent': (improvement/old_model_accuracy)*100,
    'total_test_cases': results['summary']['total_test_cases'],
    'total_candidates': results['summary']['total_candidates'],
    'validity_rate': results['summary']['validity_rate']*100,
    'chart_file': chart_file,
    'status': results['interpretation']
}

with open(summary_file, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"[OK] Summary saved to: {summary_file}")
print(f"\n{'='*70}")
print("ACCURACY REPORT SUMMARY")
print(f"{'='*70}")
print(f"Overall Accuracy: {overall_accuracy:.1f}%")
print(f"Previous Model: 45.1%")
print(f"Improvement: +{improvement:.1f} percentage points")
print(f"Relative Gain: +{(improvement/old_model_accuracy)*100:.1f}%")
print(f"Status: {results['interpretation']}")
print(f"{'='*70}")
