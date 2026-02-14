"""
Empirical Test Visualization Generator
Creates charts and visualizations for the COVID-19 accuracy test
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import pandas as pd

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 150

def load_data():
    """Load all result data"""
    with open('models/empirical_test/results/accuracy_metrics.json', 'r') as f:
        accuracy_data = json.load(f)
    
    with open('models/empirical_test/results/comparison_report.json', 'r') as f:
        comparison_data = json.load(f)
    
    with open('models/empirical_test/results/generated_drugs.json', 'r') as f:
        generated_data = json.load(f)
    
    with open('models/empirical_test/data/fda_approved_drugs.json', 'r') as f:
        reference_data = json.load(f)
    
    return accuracy_data, comparison_data, generated_data, reference_data

def create_accuracy_dashboard(accuracy_data, comparison_data, generated_data, reference_data):
    """Create comprehensive accuracy dashboard"""
    
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Accuracy Metrics Bar Chart (Top Left)
    ax1 = plt.subplot(3, 3, 1)
    metrics = ['Precision', 'Recall', 'F1-Score', 'Validity', 'QED Success']
    values = [
        accuracy_data['accuracy_metrics']['precision'],
        accuracy_data['accuracy_metrics']['recall'],
        accuracy_data['accuracy_metrics']['f1_score'],
        accuracy_data['accuracy_metrics']['validity_rate'],
        accuracy_data['accuracy_metrics']['qed_success']
    ]
    colors = ['#2ecc71' if v >= 0.6 else '#f39c12' if v >= 0.4 else '#e74c3c' for v in values]
    
    bars = ax1.barh(metrics, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Score', fontweight='bold')
    ax1.set_title('Accuracy Metrics Overview', fontweight='bold', fontsize=12)
    ax1.set_xlim(0, 1)
    ax1.axvline(x=0.6, color='green', linestyle='--', alpha=0.5, label='Good (60%)')
    ax1.axvline(x=0.4, color='red', linestyle='--', alpha=0.5, label='Fair (40%)')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax1.text(val + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{val:.1%}', va='center', fontweight='bold', fontsize=10)
    
    # 2. Overall Accuracy Gauge (Top Middle)
    ax2 = plt.subplot(3, 3, 2)
    overall_acc = accuracy_data['accuracy_metrics']['overall_accuracy']
    
    # Create gauge-like visualization
    theta = np.linspace(0, np.pi, 100)
    r = 1.0
    
    # Background arc
    ax2.fill_between(np.cos(theta), np.sin(theta), 0, alpha=0.1, color='gray')
    
    # Value arc
    value_theta = theta[int(overall_acc * 100)]
    ax2.fill_between(np.cos(theta[:int(overall_acc * 100)]), 
                     np.sin(theta[:int(overall_acc * 100)]), 0, 
                     alpha=0.6, color='#2ecc71' if overall_acc >= 0.6 else '#f39c12')
    
    ax2.text(0, -0.5, f'{overall_acc:.1%}', ha='center', va='center', 
             fontsize=24, fontweight='bold')
    ax2.text(0, -0.8, 'Overall Accuracy', ha='center', va='center', 
             fontsize=10, fontweight='bold')
    ax2.set_xlim(-1.2, 1.2)
    ax2.set_ylim(-1, 1.2)
    ax2.axis('off')
    ax2.set_title('Empirical Accuracy Score', fontweight='bold', fontsize=12)
    
    # 3. Precision-Recall Breakdown (Top Right)
    ax3 = plt.subplot(3, 3, 3)
    breakdown = accuracy_data['accuracy_metrics']['breakdown']
    
    pie_data = [breakdown['true_positives'], breakdown['false_positives']]
    pie_labels = [f"True Positives\n({breakdown['true_positives']})", 
                  f"False Positives\n({breakdown['false_positives']})"]
    colors_pie = ['#2ecc71', '#e74c3c']
    explode = (0.05, 0)
    
    wedges, texts, autotexts = ax3.pie(pie_data, labels=pie_labels, autopct='%1.1f%%',
                                         colors=colors_pie, explode=explode,
                                         shadow=True, startangle=90,
                                         textprops={'fontsize': 9, 'fontweight': 'bold'})
    ax3.set_title('Precision Breakdown\n(True vs False Positives)', 
                  fontweight='bold', fontsize=12)
    
    # 4. Molecular Similarity Distribution (Middle Left)
    ax4 = plt.subplot(3, 3, 4)
    sim_data = comparison_data['similarity_analysis']
    categories = ['High\n(≥0.7)', 'Medium\n(0.5-0.7)', 'Low\n(<0.5)']
    counts = [sim_data['high_similarity_count'], 
              sim_data['medium_similarity_count'],
              sim_data['low_similarity_count']]
    colors_bar = ['#2ecc71', '#f39c12', '#e74c3c']
    
    bars = ax4.bar(categories, counts, color=colors_bar, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    ax4.set_ylabel('Number of Drugs', fontweight='bold')
    ax4.set_title('Similarity Distribution\n(vs FDA Reference)', 
                  fontweight='bold', fontsize=12)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, counts):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 5. Target Coverage Analysis (Middle Center)
    ax5 = plt.subplot(3, 3, 5)
    target_data = comparison_data['target_analysis']
    
    if 'reference_targets' in target_data and target_data['reference_targets']:
        ref_targets = target_data['reference_targets']
        gen_targets = list(target_data['generated_targets'].keys())
        
        # Create Venn-like comparison
        overlap = set(gen_targets).intersection(set(ref_targets))
        only_gen = set(gen_targets) - set(ref_targets)
        only_ref = set(ref_targets) - set(gen_targets)
        
        categories = ['Shared\nTargets', 'Generated\nOnly', 'Reference\nOnly']
        values = [len(overlap), len(only_gen), len(only_ref)]
        colors_target = ['#9b59b6', '#3498db', '#e74c3c']
        
        bars = ax5.bar(categories, values, color=colors_target, alpha=0.8,
                       edgecolor='black', linewidth=1.5)
        ax5.set_ylabel('Number of Targets', fontweight='bold')
        ax5.set_title('Target Coverage Analysis', fontweight='bold', fontsize=12)
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val}', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # Add coverage text
        coverage = target_data['coverage']
        ax5.text(0.5, max(values) * 0.5, f'Coverage:\n{coverage:.1%}', 
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    # 6. QED Score Comparison (Middle Right)
    ax6 = plt.subplot(3, 3, 6)
    prop_data = comparison_data['property_comparison']
    
    qed_generated = prop_data['generated_stats']['avg_qed']
    qed_reference = prop_data['reference_stats']['avg_qed']
    
    x_pos = [0, 1]
    qed_values = [qed_generated, qed_reference]
    labels = ['NOVO-1\nGenerated', 'FDA\nReference']
    colors_qed = ['#3498db', '#2ecc71']
    
    bars = ax6.bar(x_pos, qed_values, color=colors_qed, alpha=0.8,
                   edgecolor='black', linewidth=1.5, width=0.6)
    ax6.set_ylabel('QED Score', fontweight='bold')
    ax6.set_title('Drug-Likeness Comparison', fontweight='bold', fontsize=12)
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels(labels)
    ax6.axhline(y=0.67, color='red', linestyle='--', linewidth=2, 
                label='Good Drug Threshold', alpha=0.7)
    ax6.legend(fontsize=8)
    ax6.set_ylim(0, 1)
    ax6.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, qed_values):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 7. Molecular Weight Distribution (Bottom Left)
    ax7 = plt.subplot(3, 3, 7)
    
    # Extract MW data
    gen_mws = [d['molecular_weight'] for d in generated_data['candidates']]
    ref_mws = [d['mw'] for d in reference_data['reference_drugs']['drugs'] if d['mw'] < 10000]
    
    # Create histogram
    ax7.hist(gen_mws, bins=10, alpha=0.6, label='NOVO-1 Generated', 
             color='#3498db', edgecolor='black')
    ax7.hist(ref_mws, bins=10, alpha=0.6, label='FDA Reference', 
             color='#2ecc71', edgecolor='black')
    ax7.set_xlabel('Molecular Weight (Da)', fontweight='bold')
    ax7.set_ylabel('Frequency', fontweight='bold')
    ax7.set_title('Molecular Weight Distribution', fontweight='bold', fontsize=12)
    ax7.legend(fontsize=9)
    ax7.grid(True, alpha=0.3)
    
    # 8. Summary Statistics Table (Bottom Center)
    ax8 = plt.subplot(3, 3, 8)
    ax8.axis('off')
    
    summary_text = f"""
    EMPIRICAL TEST SUMMARY
    ═══════════════════════════════════════════
    
    Disease: COVID-19 (SARS-CoV-2)
    Data Source: CDC/FDA (Feb 2025)
    
    GENERATION RESULTS:
    • Total Drugs: {len(generated_data['candidates'])}
    • Valid Molecules: {generated_data['statistics']['valid_molecules']}/{generated_data['statistics']['total_generated']} (100%)
    • Avg QED: {generated_data['statistics']['avg_qed']:.3f}
    • Avg MW: {generated_data['statistics']['avg_mw']:.1f} Da
    
    ACCURACY METRICS:
    • Precision: {accuracy_data['accuracy_metrics']['precision']:.1%}
    • Recall: {accuracy_data['accuracy_metrics']['recall']:.1%}
    • F1-Score: {accuracy_data['accuracy_metrics']['f1_score']:.3f}
    
    OVERALL ACCURACY: {accuracy_data['accuracy_metrics']['overall_accuracy']:.1%}
    
    INTERPRETATION:
    {accuracy_data['interpretation']['overall_interpretation']}
    """
    
    ax8.text(0.5, 0.5, summary_text, transform=ax8.transAxes, fontsize=9,
             verticalalignment='center', horizontalalignment='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, pad=1),
             family='monospace', fontweight='bold')
    
    # 9. Best Matches (Bottom Right)
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    # Get top 5 best matches
    best_matches = comparison_data['similarity_analysis']['best_matches'][:5]
    
    match_text = "TOP 5 MOLECULAR MATCHES\n"
    match_text += "═══════════════════════════\n\n"
    
    for i, match in enumerate(best_matches, 1):
        match_text += f"{i}. {match['generated_id']}\n"
        match_text += f"   → {match['reference_name']}\n"
        match_text += f"   Similarity: {match['similarity']:.3f}\n\n"
    
    ax9.text(0.5, 0.5, match_text, transform=ax9.transAxes, fontsize=9,
             verticalalignment='center', horizontalalignment='center',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3, pad=1),
             family='monospace')
    
    plt.suptitle('COVID-19 Empirical Test - Accuracy Analysis Dashboard', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    plt.savefig('models/empirical_test/visualization/accuracy_dashboard.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print('[OK] Saved: accuracy_dashboard.png')
    
    return fig

def main():
    """Generate all visualizations"""
    print('\n' + '='*70)
    print('GENERATING EMPIRICAL TEST VISUALIZATIONS')
    print('='*70)
    
    # Load data
    accuracy_data, comparison_data, generated_data, reference_data = load_data()
    
    # Create dashboard
    fig = create_accuracy_dashboard(accuracy_data, comparison_data, generated_data, reference_data)
    
    print('\n' + '='*70)
    print('[OK] VISUALIZATION COMPLETE')
    print('='*70)
    print('\nGenerated Files:')
    print('  • accuracy_dashboard.png - Comprehensive 9-panel dashboard')
    print('  • accuracy_metrics.json - Detailed accuracy data')
    print('  • comparison_report.json - Molecular comparison data')
    print('='*70 + '\n')
    
    plt.close()

if __name__ == "__main__":
    main()
