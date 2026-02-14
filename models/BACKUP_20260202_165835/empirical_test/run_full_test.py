"""
Master Script: Run Complete COVID-19 Empirical Test
Executes the full pipeline: data generation → comparison → accuracy calculation → visualization
"""

import sys
import os
import subprocess
import time

def run_script(script_path, description):
    """Run a Python script and show progress"""
    print(f"\n{'='*70}")
    print(f"STEP: {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            return True
        else:
            print(f"[FAILED] {description} failed")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[FAILED] {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"[FAILED] {description} failed with error: {e}")
        return False

def main():
    """Run complete empirical test pipeline"""
    
    print("\n" + "="*70)
    print("COVID-19 EMPIRICAL TEST - FULL PIPELINE")
    print("="*70)
    print("\nThis pipeline will:")
    print("  1. Generate drugs using NOVO-1 for COVID-19 symptoms")
    print("  2. Compare generated drugs with FDA-approved reference drugs")
    print("  3. Calculate accuracy metrics (Precision, Recall, F1)")
    print("  4. Generate visualizations and final report")
    print("="*70)
    
    start_time = time.time()
    
    # Define scripts to run
    scripts = [
        ("models/empirical_test/models/novo1_predictor.py", 
         "Generate NOVO-1 Drugs for COVID-19"),
        ("models/empirical_test/comparison/molecular_similarity.py", 
         "Calculate Molecular Similarities"),
        ("models/empirical_test/comparison/calculate_accuracy.py", 
         "Calculate Accuracy Metrics"),
        ("models/empirical_test/visualization/generate_charts.py", 
         "Generate Visualizations")
    ]
    
    # Run each script
    results = []
    for script_path, description in scripts:
        success = run_script(script_path, description)
        results.append((description, success))
        
        if not success:
            print(f"\n[!] Pipeline stopped due to failure in: {description}")
            break
    
    elapsed_time = time.time() - start_time
    
    # Print final summary
    print("\n" + "="*70)
    print("EMPIRICAL TEST COMPLETE")
    print("="*70)
    print(f"\nTotal Time: {elapsed_time:.1f} seconds")
    print(f"\nPipeline Results:")
    
    for description, success in results:
        status = "[OK] COMPLETE" if success else "[FAILED]"
        print(f"  {status} - {description}")
    
    if all(success for _, success in results):
        print("\n" + "="*70)
        print("[SUCCESS] ALL STEPS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nGenerated Files:")
        print("  [DIR] models/empirical_test/results/")
        print("     - generated_drugs.json - NOVO-1 drug candidates")
        print("     - comparison_report.json - Molecular comparison data")
        print("     - accuracy_metrics.json - Accuracy calculations")
        print("\n  [DIR] models/empirical_test/visualization/")
        print("     - accuracy_dashboard.png - 9-panel visualization")
        print("="*70)
        
        # Try to show accuracy summary
        try:
            import json
            with open('models/empirical_test/results/accuracy_metrics.json', 'r') as f:
                acc_data = json.load(f)
            
            print("\n[RESULTS] FINAL ACCURACY RESULTS:")
            print(f"   Precision: {acc_data['accuracy_metrics']['precision']:.1%}")
            print(f"   Recall:    {acc_data['accuracy_metrics']['recall']:.1%}")
            print(f"   F1-Score:  {acc_data['accuracy_metrics']['f1_score']:.3f}")
            print(f"   Overall:   {acc_data['accuracy_metrics']['overall_accuracy']:.1%}")
            print(f"\n   {acc_data['interpretation']['overall_interpretation']}")
            print("="*70)
            
        except Exception as e:
            print(f"\n[!] Could not load accuracy results: {e}")
    else:
        print("\n[!] Some steps failed. Check error messages above.")
    
    print("\n")

if __name__ == "__main__":
    main()
