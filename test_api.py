import requests
import json
from datetime import datetime

# Test the drug discovery API
url = "http://127.0.0.1:8000/api/discover"

# Test symptoms
symptoms = [
    "brittle toenails",
    "cracking knuckles", 
    "ear blockage",
    "fluttering heartbeat",
    "sudden confusion"
]

payload = {
    "symptoms": symptoms,
    "n_candidates": 5
}

print("="*80)
print("TESTING DRUG DISCOVERY API")
print("="*80)
print(f"\nSymptoms: {', '.join(symptoms)}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\nSending request...")

try:
    response = requests.post(url, json=payload, timeout=120)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Time: {response.elapsed.total_seconds():.2f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*80)
        print("RESPONSE STRUCTURE")
        print("="*80)
        
        # Print top-level fields
        print(f"\n✓ success: {data.get('success')}")
        
        # Print thinking steps
        thinking_steps = data.get('thinking_steps', [])
        print(f"\n✓ thinking_steps: {len(thinking_steps)} steps")
        
        for i, step in enumerate(thinking_steps, 1):
            print(f"\n  Step {i}: {step.get('title')}")
            print(f"    Status: {step.get('status')}")
            print(f"    Description: {step.get('description', 'N/A')[:80]}...")
            if step.get('details'):
                print(f"    Details: {len(step['details'])} fields")
        
        # Print results
        results = data.get('results', {})
        print(f"\n✓ results.content length: {len(results.get('content', ''))} characters")
        print(f"✓ results.symptoms: {results.get('symptoms')}")
        
        candidates = results.get('candidates', [])
        print(f"\n✓ results.candidates: {len(candidates)} candidates generated")
        
        if candidates:
            print("\n" + "="*80)
            print("CANDIDATE DETAILS")
            print("="*80)
            
            for i, cand in enumerate(candidates, 1):
                print(f"\n--- Candidate {i} ---")
                print(f"ID: {cand.get('id')}")
                print(f"SMILES: {cand.get('smiles')[:60]}...")
                print(f"Molecular Formula: {cand.get('molecular_formula')}")
                print(f"Molecular Weight: {cand.get('molecular_weight'):.2f} Da")
                print(f"QED: {cand.get('qed'):.3f}")
                print(f"LogP: {cand.get('logp'):.2f}")
                print(f"Confidence: {cand.get('confidence'):.1f}%")
                print(f"Method: {cand.get('generation_method')}")
                print(f"Target Proteins: {', '.join(cand.get('target_proteins', []))}")
                
                admet = cand.get('admet', {})
                print(f"Bioavailability: {admet.get('bioavailability', 0):.1f}%")
                print(f"Toxicity Risk: {admet.get('toxicity_risk', 'unknown')}")
                print(f"Half-life: {admet.get('half_life', 0):.1f} hours")
                
                lipinski = cand.get('lipinski', {})
                print(f"Lipinski Violations: {lipinski.get('violations', 0)}")
                print(f"Passes Lipinski: {lipinski.get('passes', False)}")
        
        # Save full response to file
        output_file = "test_drug_discovery_response.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Full response saved to: {output_file}")
        
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
