"""
TxGNN with Matplotlib Visualization - Complete Example
Shows how to use TxGNN with accuracy metrics and visualizations.
"""

import sys
import os
# Add the project root to path (3 levels up from this file)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from txgnn.utils.predictor import TxGNNPredictor
from txgnn.utils.visualization import TxGNNVisualizer
import matplotlib.pyplot as plt


def run_with_visualization():
    """
    Run TxGNN predictions with full visualization and accuracy metrics.
    
    This demonstrates:
    1. Making predictions from symptoms
    2. Calculating accuracy metrics
    3. Creating visualizations
    4. Generating comprehensive reports
    """
    
    print("="*80)
    print("TxGNN with Matplotlib Visualization - Complete Example")
    print("="*80)
    
    # Step 1: Initialize predictor and visualizer
    print("\n[Step 1] Initializing TxGNN Predictor and Visualizer...")
    predictor = TxGNNPredictor(model_path='models/txgnn_trained.pt')
    visualizer = TxGNNVisualizer(save_dir="results")
    
    # Step 2: Define test cases with COVID-19 symptoms
    print("\n[Step 2] Defining COVID-19 test cases...")
    
    test_cases = {
        'COVID-19 Mild': ['fever', 'cough', 'fatigue', 'loss_of_taste'],
        'COVID-19 Moderate': ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'loss_of_smell', 'muscle_pain'],
        'COVID-19 Severe': ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'chest_pain', 'difficulty_breathing', 'chills'],
    }
    
    # Known effective treatments (ground truth)
    ground_truth = [
        'remdesivir', 'paxlovid', 'molnupiravir',  # Antivirals
        'dexamethasone',  # Anti-inflammatory
        'baricitinib', 'tocilizumab',  # Immunomodulators
    ]
    
    # Step 3: Run predictions for all test cases
    print("\n[Step 3] Running predictions for all test cases...")
    
    all_predictions = {}
    all_metrics = {}
    
    for case_name, symptoms in test_cases.items():
        print(f"\n  Testing: {case_name}")
        print(f"  Symptoms: {', '.join(symptoms)}")
        
        # Get predictions
        predictions = predictor.predict_drugs(symptoms, top_k=15, verbose=False)
        all_predictions[case_name] = predictions
        
        # Calculate metrics
        metrics = visualizer.calculate_metrics(predictions, ground_truth, k_values=[5, 10, 15])
        all_metrics[case_name] = metrics
        
        # Print metrics table
        visualizer.print_metrics_table(metrics, f"{case_name} - Accuracy Metrics")
    
    # Step 4: Create comprehensive visualizations
    print("\n[Step 4] Generating visualizations...")
    print("  -" * 40)
    
    # 4.1: Accuracy metrics comparison across all test cases
    print("  Creating accuracy metrics comparison chart...")
    fig1 = visualizer.plot_accuracy_metrics(
        all_metrics,
        title="TxGNN Accuracy Metrics - COVID-19 Severity Comparison",
        save_path="accuracy_comparison.png"
    )
    
    # 4.2: Top predictions for each case
    print("  Creating top predictions charts...")
    for case_name, predictions in all_predictions.items():
        visualizer.plot_top_predictions(
            predictions,
            ground_truth,
            title=f"Top Drug Predictions - {case_name}",
            top_k=15,
            save_path=f"predictions_{case_name.replace(' ', '_').lower()}.png"
        )
    
    # 4.3: Symptom importance analysis
    print("  Creating symptom importance analysis...")
    # Convert test cases to proper format
    symptom_pred_dict = {}
    for case_name, symptoms in test_cases.items():
        symptom_key = ', '.join(symptoms[:3]) + '...' if len(symptoms) > 3 else ', '.join(symptoms)
        symptom_pred_dict[symptom_key] = all_predictions[case_name]
    
    fig3 = visualizer.plot_symptom_importance(
        symptom_pred_dict,
        ground_truth,
        save_path="symptom_importance.png"
    )
    
    # Step 5: Generate comprehensive report
    print("\n[Step 5] Generating comprehensive report...")
    print("  -" * 40)
    
    report = visualizer.create_report(
        all_predictions,
        ground_truth,
        report_path="covid19_accuracy_report.json"
    )
    
    # Step 6: Summary
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE!")
    print("="*80)
    print("\nGenerated files in 'results/' directory:")
    print("  1. accuracy_comparison.png - Bar charts comparing metrics")
    print("  2. predictions_covid-19_*.png - Top predictions for each case")
    print("  3. symptom_importance.png - Which symptoms work best")
    print("  4. covid19_accuracy_report.json - Full metrics report")
    print("\n" + "="*80)
    
    return all_predictions, all_metrics, report


def quick_visualization_example():
    """
    Quick 1-minute example showing basic visualization.
    """
    print("\n" + "="*60)
    print("QUICK VISUALIZATION EXAMPLE")
    print("="*60)
    
    # Initialize with trained model
    predictor = TxGNNPredictor(model_path='models/txgnn_trained.pt')
    visualizer = TxGNNVisualizer(save_dir="quick_results")
    
    # Single prediction
    symptoms = ['fever', 'cough', 'shortness_of_breath']
    print(f"\nSymptoms: {symptoms}")
    
    predictions = predictor.predict_drugs(symptoms, top_k=10, verbose=True)
    
    # Ground truth for COVID-19
    ground_truth = ['paxlovid', 'remdesivir', 'molnupiravir', 'dexamethasone']
    
    # Calculate and display metrics
    metrics = visualizer.calculate_metrics(predictions, ground_truth, k_values=[5, 10])
    visualizer.print_metrics_table(metrics, "Quick Test Metrics")
    
    # Create simple visualization
    visualizer.plot_top_predictions(
        predictions,
        ground_truth,
        title="Quick Prediction Visualization",
        top_k=10,
        save_path="quick_prediction.png"
    )
    
    print("\nCheck 'quick_results/' for the visualization!")


def custom_symptoms_visualization():
    """
    Example showing how to visualize custom symptoms.
    """
    print("\n" + "="*60)
    print("CUSTOM SYMPTOMS VISUALIZATION")
    print("="*60)
    
    predictor = TxGNNPredictor(model_path='models/txgnn_trained.pt')
    visualizer = TxGNNVisualizer(save_dir="custom_results")
    
    # Try different symptom combinations
    symptom_sets = [
        ['fever', 'cough'],
        ['fever', 'cough', 'fatigue'],
        ['fever', 'cough', 'fatigue', 'headache'],
        ['fever', 'cough', 'fatigue', 'loss_of_taste', 'loss_of_smell'],
    ]
    
    ground_truth = ['paxlovid', 'remdesivir', 'molnupiravir', 'dexamethasone', 'baricitinib']
    
    all_predictions = {}
    
    print("\nTesting different symptom combinations:")
    for i, symptoms in enumerate(symptom_sets, 1):
        print(f"\n  Test {i}: {symptoms}")
        predictions = predictor.predict_drugs(symptoms, top_k=15, verbose=False)
        all_predictions[f"Set {i} ({len(symptoms)} symptoms)"] = predictions
        
        metrics = visualizer.calculate_metrics(predictions, ground_truth, k_values=[5, 10])
        print(f"    Precision@5: {metrics['Precision@5']:.3f}, Recall@10: {metrics['Recall@10']:.3f}")
    
    # Visualize comparison
    symptom_pred_dict = {}
    for i, symptoms in enumerate(symptom_sets):
        key = f"{len(symptoms)} symptoms"
        symptom_pred_dict[key] = all_predictions[f"Set {i+1} ({len(symptoms)} symptoms)"]
    
    visualizer.plot_symptom_importance(
        symptom_pred_dict,
        ground_truth,
        save_path="symptom_count_comparison.png"
    )
    
    print("\nCheck 'custom_results/' for visualizations!")


if __name__ == "__main__":
    # Option 1: Full comprehensive example
    print("\nChoose an option:")
    print("1. Full visualization with all metrics")
    print("2. Quick 1-minute example")
    print("3. Custom symptoms comparison")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_with_visualization()
        plt.show()  # Display plots
    elif choice == "2":
        quick_visualization_example()
        plt.show()
    elif choice == "3":
        custom_symptoms_visualization()
        plt.show()
    else:
        print("\nRunning quick example by default...")
        quick_visualization_example()
        plt.show()