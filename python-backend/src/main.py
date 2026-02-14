"""
NOVO-1 Drug Discovery API - FastAPI Backend
Complete drug discovery system integrated into python-backend
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from pathlib import Path
import json
import traceback
from datetime import datetime
import time
import asyncio

# Add models path for NOVO-1 system
sys.path.append(str(Path(__file__).parent.parent.parent / "models" / "01_CORE_SYSTEM"))

app = FastAPI(
    title="NOVO-1 Drug Discovery API",
    description="FastAPI backend for NOVO-1 drug discovery model",
    version="3.0.0"
)

# CORS middleware - allow Node.js backend and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",  # Node.js backend
        "http://localhost:5173",  # Frontend dev server
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global system instance
system = None

# Pydantic models for request/response
class DiscoverRequest(BaseModel):
    symptoms: List[str]
    n_candidates: int = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["fever", "cough", "fatigue"],
                "n_candidates": 5
            }
        }

class Candidate(BaseModel):
    id: str
    smiles: str
    molecular_formula: str
    molecular_weight: float
    qed: float
    confidence_score: float
    target_proteins: List[str]
    source_drugs: List[str]
    admet_summary: dict
    passes_lipinski: bool

class DiscoverResponse(BaseModel):
    success: bool
    symptoms: List[str]
    num_candidates: int
    timestamp: str
    candidates: List[Candidate]
    thinking_steps: List[dict]
    thinking_steps: List[dict] = []

class HealthResponse(BaseModel):
    status: str
    system_initialized: bool
    timestamp: str

def initialize_system():
    """Initialize the NOVO-1 system"""
    global system
    try:
        from novo1_enhanced_system import EnhancedNOVO1System
        
        print("="*80)
        print("[INFO] Initializing NOVO-1 Drug Discovery System...")
        print("="*80)
        system = EnhancedNOVO1System(use_google_drive=False)
        
        # Load drug dataset from local models folder
        models_path = Path(__file__).parent.parent.parent / "models" / "empirical_test" / "data"
        all_drugs = []
        
        # Load FDA approved drugs
        fda_file = models_path / "fda_approved_drugs.json"
        if fda_file.exists():
            with open(fda_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'drugs' in data:
                    for drug in data['drugs']:
                        # Convert FDA format to knowledge graph format
                        smiles = drug.get('smiles_nirmatrelvir') or drug.get('smiles', '')
                        if not smiles and drug.get('smiles_ritonavir'):
                            smiles = drug.get('smiles_ritonavir')
                        
                        # Build targets list
                        targets = []
                        if drug.get('primary_target'):
                            targets.append(drug['primary_target'])
                        for t in drug.get('secondary_targets', []):
                            if t not in targets:
                                targets.append(t)
                        
                        # Get indications (treatments)
                        indications = []
                        if drug.get('mechanism'):
                            # Map mechanism to disease indications
                            mech = drug['mechanism'].lower()
                            if 'protease' in mech:
                                indications = ['COVID-19', 'Viral Infections']
                            elif 'polymerase' in mech or 'rdrp' in mech:
                                indications = ['COVID-19', 'Viral Infections']
                            else:
                                indications = ['COVID-19']
                        
                        all_drugs.append({
                            'name': drug['name'],
                            'smiles': smiles,
                            'targets': targets,
                            'indications': indications,
                            'drugbank_id': drug.get('drugbank_id', ''),
                            'mw': drug.get('mw', 0),
                            'qed': drug.get('qed_score', 0.5)
                        })
                    print(f"[OK] Loaded {len(data['drugs'])} FDA approved drugs")
        else:
            print(f"[WARNING] FDA drugs file not found: {fda_file}")
        
        # Load reference drugs from other sources
        reference_drugs = [
            {'name': 'Ibuprofen', 'smiles': 'CC(C)C1=CC=C(C=C1)C(C)C(=O)O', 'targets': ['COX-1', 'COX-2'], 'indications': ['Pain', 'Inflammation', 'Fever']},
            {'name': 'Aspirin', 'smiles': 'CC(=O)OC1=CC=CC=C1C(=O)O', 'targets': ['COX-1', 'COX-2'], 'indications': ['Pain', 'Inflammation', 'Fever']},
            {'name': 'Metformin', 'smiles': 'CN(C)C(=N)NC(=N)N', 'targets': ['AMPK'], 'indications': ['Diabetes', 'Metabolic Syndrome']},
            {'name': 'Atorvastatin', 'smiles': 'CC(C)C1=CC=C(C=C1)C(=O)N(C)C2CC(C2)C(=O)NC(CC3=CC=CC=C3)C(=O)NC(C)C', 'targets': ['HMG-CoA Reductase'], 'indications': ['High Cholesterol', 'Cardiovascular Disease']},
            {'name': 'Lisinopril', 'smiles': 'CCCC(C(=O)NCCCC(C(=O)NCCCc1ccccc1)C(=O)O)N', 'targets': ['ACE'], 'indications': ['Hypertension', 'Heart Failure']},
            {'name': 'Amlodipine', 'smiles': 'CC1=C(C(=O)OCC)NC(C)=C(C1)C(=O)NCC2=CC=CC=C2Cl', 'targets': ['Calcium Channel'], 'indications': ['Hypertension', 'Angina']},
            {'name': 'Omeprazole', 'smiles': 'CC1=CC=C(C=C1)CS(=O)C2=NC=C(N=2)C3=CC=C(N3C)C(=O)OC', 'targets': ['Proton Pump'], 'indications': ['Acid Reflux', 'GERD']},
            {'name': 'Gabapentin', 'smiles': 'NCC1(CC(=O)O)CCCCC1', 'targets': ['Calcium Channel Alpha2'], 'indications': ['Neuropathic Pain', 'Epilepsy']},
            {'name': 'Sertraline', 'smiles': 'CCNCC1=CC=C(C=C1)C2=CC=CC=C2Cl', 'targets': ['SERT'], 'indications': ['Depression', 'Anxiety']},
            {'name': 'Levothyroxine', 'smiles': 'OC(=O)C(Cc1c[cH]c(c(c1)OC2O[C@@H]([C@@H]([C@H]([C@@H]2O)O)O)CO)I)I', 'targets': ['Thyroid Receptor'], 'indications': ['Hypothyroidism']},
            {'name': 'Amoxicillin', 'smiles': 'CC1(C)N2C(=O)C(N)C(C2=O)C(O)C1', 'targets': ['Penicillin Binding Protein'], 'indications': ['Bacterial Infections']},
            {'name': 'Azithromycin', 'smiles': 'CCCCC1C2C(O1)C(C(=O)O2)OC3C(C(C(C(O3)C)O)OC4C(C(C(C(O4)C)O)O)C)O', 'targets': ['50S Ribosome'], 'indications': ['Bacterial Infections']},
            {'name': 'Prednisone', 'smiles': 'CC12CCC3C(C1CCC2O)C=CC4=CC(=O)CCC4C3', 'targets': ['Glucocorticoid Receptor'], 'indications': ['Inflammation', 'Autoimmune Disorders']},
            {'name': 'Dexamethasone', 'smiles': 'CC1CCC2(C(C1=O)CC3C4CCC(C4(CC3C2F)O)F)C', 'targets': ['Glucocorticoid Receptor'], 'indications': ['Inflammation', 'Allergies']},
            {'name': 'Furosemide', 'smiles': 'C1=CC=C(C=C1S(=O)(=O)NCC(=O)O)Cl', 'targets': ['Na-K-2Cl Cotransporter'], 'indications': ['Edema', 'Hypertension']},
            {'name': 'Warfarin', 'smiles': 'CC(=O)CC(C1=CC=CC=C1)C2=CC=CC=C2O', 'targets': ['Vitamin K Epoxide Reductase'], 'indications': ['Blood Clots', 'Atrial Fibrillation']},
            {'name': 'Insulin', 'smiles': 'MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT', 'targets': ['Insulin Receptor'], 'indications': ['Diabetes']},
            {'name': 'Acetaminophen', 'smiles': 'CC(=O)NC1=CC=C(C=C1)O', 'targets': ['COX-3'], 'indications': ['Pain', 'Fever']},
            {'name': 'Losartan', 'smiles': 'CC1=CC=C(C=C1)C2=CC=CC=C2CCCN3CCOCC3', 'targets': ['AT1 Receptor'], 'indications': ['Hypertension']},
            {'name': 'Albuterol', 'smiles': 'CC(C)(C)NCC(O)c1ccc(O)cc1', 'targets': ['Beta-2 Adrenergic Receptor'], 'indications': ['Asthma', 'COPD']},
        ]
        
        all_drugs.extend(reference_drugs)
        print(f"[OK] Loaded {len(reference_drugs)} reference drugs")
        
        # If still no drugs, create essential drug database
        if len(all_drugs) < 5:
            print("[WARNING] Creating essential drug database...")
            essential_drugs = [
                {'name': 'Aspirin', 'smiles': 'CC(=O)OC1=CC=CC=C1C(=O)O', 'targets': ['COX-1', 'COX-2'], 'indications': ['Pain', 'Inflammation']},
                {'name': 'Ibuprofen', 'smiles': 'CC(C)C1=CC=C(C=C1)C(C)C(=O)O', 'targets': ['COX-2'], 'indications': ['Pain', 'Inflammation', 'Fever']},
                {'name': 'Acetaminophen', 'smiles': 'CC(=O)NC1=CC=C(C=C1)O', 'targets': ['COX-3'], 'indications': ['Pain', 'Fever']},
                {'name': 'Caffeine', 'smiles': 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C', 'targets': ['Adenosine Receptor'], 'indications': ['Fatigue', 'Headache']},
                {'name': 'Nicotine', 'smiles': 'CN1CCCC1C2=CN=CC=C2', 'targets': ['Nicotinic Receptor'], 'indications': ['Cognitive Enhancement']},
            ]
            all_drugs.extend(essential_drugs)
            print(f"[OK] Created {len(essential_drugs)} essential drugs")
        
        print(f"[INFO] Total drugs available: {len(all_drugs)}")
        
        if len(all_drugs) == 0:
            print("[ERROR] No drugs loaded! System cannot generate candidates.")
        
        # Build knowledge graph with comprehensive disease-symptom mappings
        diseases = [
            # Respiratory Diseases
            {'name': 'COVID-19', 'symptoms': ['fever', 'cough', 'fatigue', 'shortness of breath', 'loss of taste', 'loss of smell']},
            {'name': 'Influenza', 'symptoms': ['fever', 'cough', 'sore throat', 'runny nose', 'muscle aches', 'fatigue']},
            {'name': 'Pneumonia', 'symptoms': ['fever', 'cough', 'shortness of breath', 'chest pain', 'fatigue']},
            {'name': 'Asthma', 'symptoms': ['shortness of breath', 'chest tightness', 'wheezing', 'coughing']},
            {'name': 'Bronchitis', 'symptoms': ['cough', 'mucus production', 'fatigue', 'shortness of breath', 'chest discomfort']},
            
            # Cardiovascular Diseases
            {'name': 'Hypertension', 'symptoms': ['high blood pressure', 'headache', 'dizziness', 'chest pain', 'fluttering heartbeat']},
            {'name': 'Arrhythmia', 'symptoms': ['fluttering heartbeat', 'racing heart', 'slow heartbeat', 'chest pain', 'shortness of breath']},
            {'name': 'Heart Failure', 'symptoms': ['shortness of breath', 'fatigue', 'swelling in legs', 'irregular heartbeat']},
            
            # Neurological Diseases
            {'name': 'Migraine', 'symptoms': ['severe headache', 'nausea', 'sensitivity to light', 'sensitivity to sound']},
            {'name': 'Epilepsy', 'symptoms': ['seizures', 'sudden confusion', 'staring spells', 'uncontrollable movements']},
            {'name': 'Multiple Sclerosis', 'symptoms': ['numbness', 'tingling', 'muscle weakness', 'balance problems', 'fatigue']},
            {'name': 'Alzheimer Disease', 'symptoms': ['memory loss', 'confusion', 'difficulty speaking', 'mood changes']},
            {'name': 'Parkinson Disease', 'symptoms': ['tremors', 'muscle stiffness', 'slowed movement', 'balance problems']},
            
            # Dermatological Conditions
            {'name': 'Eczema', 'symptoms': ['itchy skin', 'dry skin', 'red patches', 'inflamed skin']},
            {'name': 'Psoriasis', 'symptoms': ['red patches', 'silver scales', 'itchy skin', 'cracked skin']},
            {'name': 'Fungal Infection', 'symptoms': ['brittle toenails', 'discolored nails', 'itching', 'burning sensation']},
            
            # Musculoskeletal
            {'name': 'Arthritis', 'symptoms': ['joint pain', 'stiffness', 'swelling', 'cracking knuckles', 'reduced mobility']},
            {'name': 'Osteoporosis', 'symptoms': ['bone pain', 'height loss', 'brittle bones', 'back pain']},
            
            # Mental Health
            {'name': 'Depression', 'symptoms': ['persistent sadness', 'loss of interest', 'fatigue', 'sleep problems', 'anxiety']},
            {'name': 'Anxiety Disorder', 'symptoms': ['excessive worry', 'restlessness', 'rapid heartbeat', 'sweating', 'trembling']},
            
            # General/Unexplained Symptoms
            {'name': 'General Inflammation', 'symptoms': ['fever', 'swelling', 'redness', 'pain', 'fatigue']},
            {'name': 'Chronic Fatigue Syndrome', 'symptoms': ['persistent fatigue', 'muscle pain', 'joint pain', 'memory problems', 'sleep disturbances']},
            {'name': 'Immune System Disorder', 'symptoms': ['frequent infections', 'autoimmune response', 'inflammation', 'fatigue']},
            
            # Ear/Nose/Throat
            {'name': 'Ear Infection', 'symptoms': ['ear blockage', 'ear pain', 'hearing loss', 'fever']},
            {'name': 'Sinusitis', 'symptoms': ['nasal congestion', 'facial pain', 'headache', 'thick nasal discharge']},
        ]
        
        system.build_knowledge_graph(diseases, all_drugs)
        print(f"[OK] System initialized with {len(all_drugs)} drugs")
        print("="*80)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize system: {e}")
        traceback.print_exc()
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    print("\n" + "="*80)
    print("NOVO-1 Drug Discovery API - FastAPI Python Backend")
    print("="*80)
    if not initialize_system():
        print("[ERROR] System initialization failed!")
        print("="*80)
    else:
        print("[OK] FastAPI server ready")
        print("="*80 + "\n")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "NOVO-1 Drug Discovery API",
        "version": "3.0.0",
        "status": "running",
        "system_initialized": system is not None
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        system_initialized=system is not None,
        timestamp=datetime.now().isoformat()
    )

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "success": True,
        "message": "NOVO-1 FastAPI is running",
        "system_status": "initialized" if system else "not_initialized"
    }

@app.post("/api/discover", response_model=DiscoverResponse)
async def discover_drugs(request: DiscoverRequest):
    """
    Drug discovery endpoint
    
    - **symptoms**: List of symptoms (e.g., ["fever", "cough"])
    - **n_candidates**: Number of drug candidates to generate (default: 5)
    """
    try:
        if system is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System not initialized"
            )
        
        symptoms = request.symptoms
        n_candidates = request.n_candidates
        
        if not symptoms or len(symptoms) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No symptoms provided"
            )
        
        # Record start time for artificial delays
        start_time = time.time()
        
        # Initialize thinking steps with professional titles
        thinking_steps = []
        step_count = 1

        # Step 1: Symptom Analysis
        thinking_steps.append({
            "step": step_count,
            "title": "Symptom Analysis",
            "description": f"Analyzing {len(symptoms)} input symptoms: {', '.join(symptoms)}",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        })
        step_count += 1
        await asyncio.sleep(0.5)  # Small delay

        # Step 2: Disease Pattern Matching
        thinking_steps.append({
            "step": step_count,
            "title": "Disease Pattern Matching",
            "description": "Searching knowledge graph for disease-symptom correlations...",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        })
        step_count += 1

        # Call NOVO-1 system
        print(f"[INFO] Discovering drugs for: {symptoms}")
        results = system.generate_drugs(symptoms, n_candidates=n_candidates)
        
        # Extract data for thinking steps
        matched_diseases = results.get("matched_diseases", [])
        target_proteins = results.get("target_proteins", [])
        
        # Update Disease Matching step
        if matched_diseases:
            disease_names = [d.get("disease", "Unknown") for d in matched_diseases[:3]]
            thinking_steps[1]["status"] = "completed"
            thinking_steps[1]["description"] = f"Matched {len(matched_diseases)} diseases: {', '.join(disease_names)}"
        else:
            thinking_steps[1]["status"] = "completed"
            thinking_steps[1]["description"] = "No direct disease matches found. Using universal molecular generation."

        # Add more steps with delays
        # Step 3: Target Protein Identification
        thinking_steps.append({
            "step": step_count,
            "title": "Target Protein Identification",
            "description": f"Identified {len(target_proteins)} potential drug targets",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        })
        step_count += 1
        await asyncio.sleep(0.3)

        # Step 4: Source Drug Selection
        thinking_steps.append({
            "step": step_count,
            "title": "Source Drug Selection",
            "description": "Selecting molecular scaffolds from knowledge graph...",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        })
        step_count += 1
        await asyncio.sleep(0.3)

        # Step 5: Molecular Generation
        thinking_steps.append({
            "step": step_count,
            "title": "Molecular Generation",
            "description": f"Generating {n_candidates} novel candidates using structural mutations...",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        })
        step_count += 1

        # Add artificial delay to make it take at least 5 seconds
        elapsed = time.time() - start_time
        if elapsed < 5:
            await asyncio.sleep(5 - elapsed)
        
        # Format candidates
        formatted_candidates = []
        for candidate in results.get("candidates", []):
            all_properties = candidate.get("all_properties", {})
            admet_properties = candidate.get("admet_properties", {})
            
            # Extract absorption and distribution for admet_summary
            absorption = admet_properties.get("absorption", {})
            distribution = admet_properties.get("distribution", {})
            toxicity = admet_properties.get("toxicity", {})
            
            # Build admet_summary from actual NOVO-1 data
            admet_summary = {
                "oral_bioavailability": absorption.get("oral_bioavailability_pct", 0.0),
                "bbb_penetration": distribution.get("blood_brain_barrier_logbb", 0.0),
                "toxicity_risk": toxicity.get("overall_toxicity_risk", "Unknown"),
                "drug_likeness_score": all_properties.get("qed", 0.0)
            }
            
            formatted_candidates.append(Candidate(
                id=candidate.get("id", "NOVO_001"),
                smiles=candidate.get("smiles", ""),
                molecular_formula=all_properties.get("molecular_formula", "Unknown"),
                molecular_weight=all_properties.get("molecular_weight", 0.0),
                qed=all_properties.get("qed", 0.0),
                confidence_score=candidate.get("confidence_score", 0.0),
                target_proteins=candidate.get("target_proteins", []),
                source_drugs=candidate.get("source_drugs", []),
                admet_summary=admet_summary,
                passes_lipinski=all_properties.get("lipinski_rules", {}).get("passes_lipinski", False)
            ))
        
        # Update final step
        thinking_steps[-1]["status"] = "completed"
        thinking_steps[-1]["description"] = f"Successfully generated {len(formatted_candidates)} valid molecular candidates"
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return DiscoverResponse(
            success=True,
            symptoms=symptoms,
            num_candidates=n_candidates,
            timestamp=timestamp,
            candidates=formatted_candidates,
            thinking_steps=thinking_steps
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Drug discovery failed: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
