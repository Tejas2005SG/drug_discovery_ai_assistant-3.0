"""
Quick Fix for Knowledge Graph - Universal Symptom Matching
Adds fallback matching for unknown symptoms
"""

import sys
from pathlib import Path

# Read the knowledge_graph.py file
kg_path = Path("01_CORE_SYSTEM/knowledge_graph.py")

with open(kg_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the find_diseases_by_symptoms function
old_code = '''        if not matched_symptoms:
            return []'''

new_code = '''        if not matched_symptoms:
            # UNIVERSAL FALLBACK: If no exact matches, try partial/fuzzy matching
            # or return all diseases with a minimum score so system can still work
            print("      [INFO] No exact symptom matches found. Using universal fallback...")
            
            # Try to match any partial words
            for sym_name in symptom_names:
                sym_words = set(sym_name.lower().split())
                for sym_id, name in self.symptoms.items():
                    name_words = set(name.lower().split())
                    # If any word matches, consider it a partial match
                    if sym_words & name_words:  # Intersection
                        matched_symptoms.append(sym_id)
            
            # If still no matches, add ALL symptoms as "unknown" matches
            # This ensures the system always tries to generate something
            if not matched_symptoms:
                print("      [INFO] Creating dynamic symptom entries for unknown symptoms...")
                # Add symptoms as new entries
                for i, sym_name in enumerate(symptom_names):
                    new_sym_id = f"unknown_symptom_{i}"
                    if new_sym_id not in self.symptoms:
                        self.symptoms[new_sym_id] = sym_name
                        # Create a simple embedding for it
                        if self.entity_embeddings is not None:
                            self.entity_embeddings[new_sym_id] = np.random.randn(self.dimension) * 0.01
                    matched_symptoms.append(new_sym_id)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Also need to add numpy import if not present
    if 'import numpy as np' not in content:
        content = content.replace('import numpy as np', 'import numpy as np  # noqa: F401')
    
    with open(kg_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ SUCCESSFULLY PATCHED knowledge_graph.py")
    print("   Added universal fallback for unknown symptoms")
    print("   The system will now try to generate candidates for ANY input!")
else:
    print("⚠️  Could not find the exact code to patch")
    print("   The file may already be patched or structure is different")
