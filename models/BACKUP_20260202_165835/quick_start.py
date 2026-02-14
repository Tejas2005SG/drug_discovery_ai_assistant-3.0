#!/usr/bin/env python3
"""
QUICK START SCRIPT for NOVO-1 Drug Discovery System
Run this first to test your setup!
"""

import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    print("="*70)
    print("CHECKING DEPENDENCIES")
    print("="*70)
    
    required = ['numpy', 'pandas', 'rdkit', 'sklearn']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"[OK] {package} installed")
        except ImportError:
            print(f"[MISSING] {package} NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n[WARNING] Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        print("Or use simplified mode (works without RDKit)")
    else:
        print("\n[OK] All dependencies installed!")
    
    return len(missing) == 0

def test_imports():
    """Test if all custom modules can be imported"""
    print("\n" + "="*70)
    print("TESTING MODULE IMPORTS")
    print("="*70)
    
    try:
        from google_drive_manager import GoogleDriveManager
        print("[OK] Google Drive Manager")
    except Exception as e:
        print(f"[ERROR] Google Drive Manager: {e}")
    
    try:
        from knowledge_graph import DrugRepurposingKnowledgeGraph
        print("[OK] Knowledge Graph")
    except Exception as e:
        print(f"[ERROR] Knowledge Graph: {e}")
    
    try:
        from novo1_drug_system import NOVO1DrugDiscoverySystem
        print("[OK] NOVO-1 Drug System")
    except Exception as e:
        print(f"[ERROR] NOVO-1 Drug System: {e}")

def run_quick_test():
    """Run a quick test generation"""
    print("\n" + "="*70)
    print("RUNNING QUICK TEST")
    print("="*70)
    
    try:
        from novo1_drug_system import NOVO1DrugDiscoverySystem
        
        # Minimal test data
        diseases = [
            {'name': 'Test Disease', 'symptoms': ['fever', 'pain']}
        ]
        drugs = [
            {
                'name': 'Test Drug',
                'smiles': 'CC(C)Cc1ccc(cc1)C(C)C(=O)O',
                'targets': ['target1'],
                'indications': ['Test Disease']
            }
        ]
        
        print("\nInitializing system...")
        system = NOVO1DrugDiscoverySystem(use_google_drive=False)
        
        print("Building knowledge graph...")
        system.build_knowledge_graph(diseases, drugs)
        
        print("\nGenerating test candidate...")
        candidates = system.generate_drugs(['fever'], n_candidates=3)
        
        if candidates:
            print(f"\n[SUCCESS] Generated {len(candidates)} candidates")
            print(f"[SUCCESS] Top candidate confidence: {candidates[0]['confidence']:.1%}")
            print(f"[SUCCESS] System is working correctly!")
        else:
            print("\n[WARNING] No candidates generated (check symptoms)")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main quick start routine"""
    print("\n" + "="*70)
    print("NOVO-1 DRUG DISCOVERY SYSTEM - QUICK START")
    print("$500K Hackathon Competition Entry")
    print("="*70)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Test imports
    test_imports()
    
    # Run quick test if dependencies OK
    if deps_ok:
        run_quick_test()
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("1. If test passed: Run full system with:")
        print("   python main.py")
        print("\n2. Read the implementation guide:")
        print("   IMPLEMENTATION_GUIDE.md")
        print("\n3. Set up Google Drive storage (optional):")
        print("   - Install Google Drive Desktop")
        print("   - Create folder: drug_discovery_ai")
        print("   - Change use_google_drive=True in main.py")
    else:
        print("\n" + "="*70)
        print("INSTALLATION REQUIRED")
        print("="*70)
        print("Run: pip install numpy pandas scikit-learn")
        print("For RDKit: conda install -c conda-forge rdkit")
        print("(Or use simplified mode without RDKit)")
    
    print("\n" + "="*70)
    print("Good luck with your hackathon!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
