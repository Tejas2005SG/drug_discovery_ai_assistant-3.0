"""
TxGNN Visualization Module
Provides comprehensive accuracy metrics and visualizations for drug prediction results.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os


class TxGNNVisualizer:
    """
    Visualization and metrics calculation for TxGNN predictions.
    
    Features:
    - Accuracy metrics (Precision@K, Recall@K, MRR, NDCG)
    - Confusion matrix visualization
    - ROC curves
    - Top-K prediction charts
    - Comparison across multiple test cases
    """
    
    def __init__(self, save_dir: str = "visualizations"):
        """
        Initialize visualizer.
        
        Args:
            save_dir: Directory to save generated plots
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
    def calculate_metrics(
        self,
        predictions: List[Tuple[str, float]],
        ground_truth: List[str],
        k_values: List[int] = [5, 10, 15]
    ) -> Dict:
        """
        Calculate comprehensive accuracy metrics.
        
        Args:
            predictions: List of (drug_name, score) tuples sorted by score
            ground_truth: List of known effective drugs
            k_values: List of K values for Precision@K and Recall@K
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        predicted_drugs = [p[0] for p in predictions]
        
        # Precision@K and Recall@K
        for k in k_values:
            top_k_drugs = predicted_drugs[:k]
            true_positives = len(set(top_k_drugs) & set(ground_truth))
            
            precision_k = true_positives / k if k > 0 else 0
            recall_k = true_positives / len(ground_truth) if ground_truth else 0
            
            metrics[f'Precision@{k}'] = precision_k
            metrics[f'Recall@{k}'] = recall_k
            metrics[f'F1@{k}'] = 2 * (precision_k * recall_k) / (precision_k + recall_k) if (precision_k + recall_k) > 0 else 0
        
        # Mean Reciprocal Rank (MRR)
        mrr = 0
        for i, drug in enumerate(predicted_drugs):
            if drug in ground_truth:
                mrr = 1 / (i + 1)
                break
        metrics['MRR'] = mrr
        
        # Normalized Discounted Cumulative Gain (NDCG)
        ndcg = self._calculate_ndcg(predictions, ground_truth)
        metrics['NDCG'] = ndcg
        
        # Hit Rate@K
        for k in k_values:
            top_k_drugs = predicted_drugs[:k]
            hit = 1 if any(drug in ground_truth for drug in top_k_drugs) else 0
            metrics[f'HitRate@{k}'] = hit
        
        return metrics
    
    def _calculate_ndcg(
        self,
        predictions: List[Tuple[str, float]],
        ground_truth: List[str]
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain.
        
        NDCG measures the quality of ranking by considering position
        of relevant items. Higher positions get more credit.
        """
        def dcg(scores):
            return sum([(2**s - 1) / np.log2(i + 2) for i, s in enumerate(scores)])
        
        # Binary relevance (1 if in ground truth, 0 otherwise)
        relevance = [1 if drug in ground_truth else 0 for drug, _ in predictions]
        
        # Ideal DCG (all relevant items at top)
        ideal_relevance = sorted(relevance, reverse=True)
        
        actual_dcg = dcg(relevance)
        ideal_dcg = dcg(ideal_relevance)
        
        return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0
    
    def plot_accuracy_metrics(
        self,
        metrics_dict: Dict[str, Dict],
        title: str = "TxGNN Accuracy Metrics",
        save_path: Optional[str] = None
    ):
        """
        Create comprehensive accuracy metrics visualization.
        
        Args:
            metrics_dict: Dictionary mapping test case names to metrics
            title: Plot title
            save_path: Path to save the plot
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        test_cases = list(metrics_dict.keys())
        
        # 1. Precision@K comparison
        ax1 = axes[0, 0]
        k_values = [5, 10, 15]
        x = np.arange(len(test_cases))
        width = 0.25
        
        for i, k in enumerate(k_values):
            precisions = [metrics_dict[tc][f'Precision@{k}'] for tc in test_cases]
            ax1.bar(x + i * width, precisions, width, label=f'Precision@{k}')
        
        ax1.set_ylabel('Precision')
        ax1.set_title('Precision@K Comparison')
        ax1.set_xticks(x + width)
        ax1.set_xticklabels(test_cases, rotation=45, ha='right')
        ax1.legend()
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)
        
        # 2. Recall@K comparison
        ax2 = axes[0, 1]
        for i, k in enumerate(k_values):
            recalls = [metrics_dict[tc][f'Recall@{k}'] for tc in test_cases]
            ax2.bar(x + i * width, recalls, width, label=f'Recall@{k}')
        
        ax2.set_ylabel('Recall')
        ax2.set_title('Recall@K Comparison')
        ax2.set_xticks(x + width)
        ax2.set_xticklabels(test_cases, rotation=45, ha='right')
        ax2.legend()
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        
        # 3. F1 Score comparison
        ax3 = axes[1, 0]
        for i, k in enumerate(k_values):
            f1_scores = [metrics_dict[tc][f'F1@{k}'] for tc in test_cases]
            ax3.bar(x + i * width, f1_scores, width, label=f'F1@{k}')
        
        ax3.set_ylabel('F1 Score')
        ax3.set_title('F1@K Score Comparison')
        ax3.set_xticks(x + width)
        ax3.set_xticklabels(test_cases, rotation=45, ha='right')
        ax3.legend()
        ax3.set_ylim(0, 1)
        ax3.grid(True, alpha=0.3)
        
        # 4. Overall metrics heatmap
        ax4 = axes[1, 1]
        metrics_names = ['MRR', 'NDCG', 'HitRate@5', 'HitRate@10', 'HitRate@15']
        heatmap_data = []
        
        for tc in test_cases:
            row = [metrics_dict[tc].get(m, 0) for m in metrics_names]
            heatmap_data.append(row)
        
        heatmap_data = np.array(heatmap_data)
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.3f',
            xticklabels=metrics_names,
            yticklabels=test_cases,
            cmap='YlOrRd',
            ax=ax4,
            cbar_kws={'label': 'Score'}
        )
        ax4.set_title('Overall Metrics Heatmap')
        
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.save_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Saved accuracy metrics plot to: {full_path}")
        
        return fig
    
    def plot_top_predictions(
        self,
        predictions: List[Tuple[str, float]],
        ground_truth: List[str],
        title: str = "Top Drug Predictions",
        top_k: int = 15,
        save_path: Optional[str] = None
    ):
        """
        Visualize top drug predictions with ground truth highlighting.
        
        Args:
            predictions: List of (drug_name, score) tuples
            ground_truth: List of known effective drugs
            title: Plot title
            top_k: Number of top predictions to show
            save_path: Path to save the plot
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get top-k predictions
        top_predictions = predictions[:top_k]
        drugs = [p[0] for p in top_predictions]
        scores = [p[1] for p in top_predictions]
        
        # Color based on ground truth
        colors = ['#2ecc71' if drug in ground_truth else '#e74c3c' for drug in drugs]
        
        # Create horizontal bar chart
        y_pos = np.arange(len(drugs))
        bars = ax.barh(y_pos, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add score labels on bars
        for i, (bar, score) in enumerate(zip(bars, scores)):
            width = bar.get_width()
            ax.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{score:.3f}', ha='left', va='center', fontsize=9)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(drugs)
        ax.invert_yaxis()  # Top predictions at top
        ax.set_xlabel('Prediction Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.grid(True, axis='x', alpha=0.3)
        
        # Legend
        true_patch = mpatches.Patch(color='#2ecc71', label='Known Treatment')
        false_patch = mpatches.Patch(color='#e74c3c', label='Not Known Treatment')
        ax.legend(handles=[true_patch, false_patch], loc='lower right')
        
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.save_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Saved top predictions plot to: {full_path}")
        
        return fig
    
    def plot_symptom_importance(
        self,
        symptom_predictions: Dict[str, List[Tuple[str, float]]],
        ground_truth: List[str],
        save_path: Optional[str] = None
    ):
        """
        Visualize which symptoms lead to better predictions.
        
        Args:
            symptom_predictions: Dict mapping symptom sets to predictions
            ground_truth: List of known effective drugs
            save_path: Path to save the plot
        """
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        symptom_sets = list(symptom_predictions.keys())
        precisions_5 = []
        precisions_10 = []
        
        # Calculate metrics for each symptom set
        for symptoms, predictions in symptom_predictions.items():
            metrics = self.calculate_metrics(predictions, ground_truth, k_values=[5, 10])
            precisions_5.append(metrics['Precision@5'])
            precisions_10.append(metrics['Precision@10'])
        
        # Plot 1: Precision comparison
        ax1 = axes[0]
        x = np.arange(len(symptom_sets))
        width = 0.35
        
        ax1.bar(x - width/2, precisions_5, width, label='Precision@5', color='#3498db', alpha=0.8)
        ax1.bar(x + width/2, precisions_10, width, label='Precision@10', color='#e74c3c', alpha=0.8)
        
        ax1.set_ylabel('Precision', fontsize=12)
        ax1.set_title('Prediction Accuracy by Symptom Set', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels([s.replace(', ', '\n') for s in symptom_sets], rotation=0, ha='center', fontsize=9)
        ax1.legend()
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Radar chart of different metrics
        ax2 = axes[1]
        categories = ['P@5', 'P@10', 'R@5', 'R@10', 'MRR', 'NDCG']
        
        # Average metrics across all symptom sets
        avg_metrics = {}
        for k in [5, 10]:
            avg_metrics[f'P@{k}'] = np.mean([self.calculate_metrics(symptom_predictions[s], ground_truth)[f'Precision@{k}'] for s in symptom_sets])
            avg_metrics[f'R@{k}'] = np.mean([self.calculate_metrics(symptom_predictions[s], ground_truth)[f'Recall@{k}'] for s in symptom_sets])
        avg_metrics['MRR'] = np.mean([self.calculate_metrics(symptom_predictions[s], ground_truth)['MRR'] for s in symptom_sets])
        avg_metrics['NDCG'] = np.mean([self.calculate_metrics(symptom_predictions[s], ground_truth)['NDCG'] for s in symptom_sets])
        
        values = [avg_metrics.get(cat, 0) for cat in categories]
        values += values[:1]  # Complete the circle
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        ax2 = plt.subplot(122, projection='polar')
        ax2.plot(angles, values, 'o-', linewidth=2, color='#2ecc71')
        ax2.fill(angles, values, alpha=0.25, color='#2ecc71')
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(categories)
        ax2.set_ylim(0, 1)
        ax2.set_title('Average Metrics Radar Chart', fontsize=14, fontweight='bold', pad=20)
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.save_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Saved symptom importance plot to: {full_path}")
        
        return fig
    
    def create_report(
        self,
        test_results: Dict,
        ground_truth: List[str],
        report_path: str = "txgnn_accuracy_report.json"
    ):
        """
        Create a comprehensive JSON report of all metrics.
        
        Args:
            test_results: Dictionary with test case names and predictions
            ground_truth: List of known effective drugs
            report_path: Path to save the JSON report
        """
        report = {
            'summary': {
                'total_test_cases': len(test_results),
                'ground_truth_drugs': ground_truth,
                'total_ground_truth': len(ground_truth)
            },
            'test_cases': {}
        }
        
        # Calculate metrics for each test case
        for test_name, predictions in test_results.items():
            metrics = self.calculate_metrics(predictions, ground_truth)
            
            # Get top predictions that are in ground truth
            top_10_drugs = [p[0] for p in predictions[:10]]
            found_drugs = [drug for drug in top_10_drugs if drug in ground_truth]
            
            report['test_cases'][test_name] = {
                'metrics': metrics,
                'top_10_predictions': top_10_drugs,
                'found_in_ground_truth': found_drugs,
                'num_found': len(found_drugs)
            }
        
        # Calculate overall statistics
        all_precisions_5 = [report['test_cases'][tc]['metrics']['Precision@5'] for tc in report['test_cases']]
        all_recalls_10 = [report['test_cases'][tc]['metrics']['Recall@10'] for tc in report['test_cases']]
        all_mrr = [report['test_cases'][tc]['metrics']['MRR'] for tc in report['test_cases']]
        
        report['summary']['average_precision@5'] = np.mean(all_precisions_5)
        report['summary']['average_recall@10'] = np.mean(all_recalls_10)
        report['summary']['average_mrr'] = np.mean(all_mrr)
        report['summary']['std_precision@5'] = np.std(all_precisions_5)
        
        # Save report
        full_path = os.path.join(self.save_dir, report_path)
        with open(full_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nSaved accuracy report to: {full_path}")
        print(f"\nSummary:")
        print(f"  Average Precision@5: {report['summary']['average_precision@5']:.3f} ± {report['summary']['std_precision@5']:.3f}")
        print(f"  Average Recall@10: {report['summary']['average_recall@10']:.3f}")
        print(f"  Average MRR: {report['summary']['average_mrr']:.3f}")
        
        return report
    
    def print_metrics_table(self, metrics: Dict, title: str = "Metrics"):
        """
        Print a nicely formatted metrics table to console.
        
        Args:
            metrics: Dictionary of metrics
            title: Table title
        """
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}")
        
        # Group metrics
        precision_metrics = {k: v for k, v in metrics.items() if k.startswith('Precision')}
        recall_metrics = {k: v for k, v in metrics.items() if k.startswith('Recall')}
        f1_metrics = {k: v for k, v in metrics.items() if k.startswith('F1')}
        other_metrics = {k: v for k, v in metrics.items() if k not in precision_metrics and k not in recall_metrics and k not in f1_metrics}
        
        print("\nPrecision Metrics:")
        for k, v in sorted(precision_metrics.items()):
            bar = "=" * int(v * 20)
            print(f"  {k:15s}: {v:.3f} {bar}")
        
        print("\nRecall Metrics:")
        for k, v in sorted(recall_metrics.items()):
            bar = "=" * int(v * 20)
            print(f"  {k:15s}: {v:.3f} {bar}")
        
        print("\nF1 Scores:")
        for k, v in sorted(f1_metrics.items()):
            bar = "=" * int(v * 20)
            print(f"  {k:15s}: {v:.3f} {bar}")
        
        print("\nOther Metrics:")
        for k, v in sorted(other_metrics.items()):
            if isinstance(v, float):
                bar = "=" * int(v * 20)
                print(f"  {k:15s}: {v:.3f} {bar}")
            else:
                print(f"  {k:15s}: {v}")
        
        print(f"{'='*60}\n")


# Quick demo function
def demo_visualization():
    """Run a quick demonstration of the visualization capabilities."""
    print("="*70)
    print("TxGNN Visualization Demo")
    print("="*70)
    
    # Sample data for demonstration
    sample_predictions = [
        ('paxlovid', 0.85),
        ('dexamethasone', 0.82),
        ('remdesivir', 0.78),
        ('baricitinib', 0.75),
        ('molnupiravir', 0.72),
        ('tocilizumab', 0.68),
        ('hydroxychloroquine', 0.55),
        ('ivermectin', 0.52),
        ('azithromycin', 0.48),
        ('acetaminophen', 0.45),
        ('ibuprofen', 0.42),
        ('chloroquine', 0.38),
        ('colchicine', 0.35),
        ('doxycycline', 0.32),
        ('prednisone', 0.28),
    ]
    
    ground_truth = ['paxlovid', 'dexamethasone', 'remdesivir', 'baricitinib', 'molnupiravir', 'tocilizumab']
    
    # Initialize visualizer
    viz = TxGNNVisualizer(save_dir="demo_viz")
    
    # Calculate and display metrics
    metrics = viz.calculate_metrics(sample_predictions, ground_truth)
    viz.print_metrics_table(metrics, "Sample COVID-19 Prediction Metrics")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    viz.plot_top_predictions(sample_predictions, ground_truth, 
                            title="Top Drug Predictions for COVID-19",
                            save_path="top_predictions.png")
    
    # Test multiple cases
    test_cases = {
        'Mild Case': sample_predictions,
        'Moderate Case': sample_predictions,
        'Severe Case': sample_predictions
    }
    
    metrics_dict = {}
    for case, preds in test_cases.items():
        metrics_dict[case] = viz.calculate_metrics(preds, ground_truth)
    
    viz.plot_accuracy_metrics(metrics_dict, 
                             title="TxGNN Accuracy Metrics Comparison",
                             save_path="accuracy_metrics.png")
    
    # Create report
    report = viz.create_report(test_cases, ground_truth, 
                              report_path="demo_report.json")
    
    print("\n" + "="*70)
    print("Demo complete! Check the 'demo_viz/' directory for generated plots.")
    print("="*70)


if __name__ == "__main__":
    demo_visualization()