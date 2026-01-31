from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, QED, rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D
from typing import Dict, Any, Optional
import json

class ChemRefinery:
    @staticmethod
    def validate_smiles(smiles: str) -> bool:
        """Check if a SMILES string creates a valid molecule."""
        if not smiles:
            return False
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None

    @staticmethod
    def analyze_molecule(smiles: str) -> Dict[str, Any]:
        """
        Calculate physicochemical properties (Lipinski, QED) for a molecule.
        """
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return {"valid": False, "error": "Invalid SMILES"}

        # Calculate properties
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Lipinski.NumHDonors(mol)
        hba = Lipinski.NumHAcceptors(mol)
        tpsa = Descriptors.TPSA(mol)
        rot_bonds = Descriptors.NumRotatableBonds(mol)
        qed_score = QED.qed(mol)
        
        # Lipinski's Rule of 5 Check
        # MW <= 500, LogP <= 5, HBD <= 5, HBA <= 10
        violations = 0
        violation_details = []
        
        if mw > 500:
            violations += 1
            violation_details.append("MW > 500")
        if logp > 5:
            violations += 1
            violation_details.append("LogP > 5")
        if hbd > 5:
            violations += 1
            violation_details.append("H-Bond Donors > 5")
        if hba > 10:
            violations += 1
            violation_details.append("H-Bond Acceptors > 10")

        # Synthetic Accessibility (simplified proxy via fragment complexity if SAScore not avail)
        # For professional grade, we use QED as a quality proxy
        
        return {
            "valid": True,
            "smiles": Chem.MolToSmiles(mol, canonical=True),
            "properties": {
                "molecular_weight": round(mw, 2),
                "logp": round(logp, 2),
                "hbd": hbd,
                "hba": hba,
                "tpsa": round(tpsa, 2),
                "rotatable_bonds": rot_bonds,
                "qed": round(qed_score, 3)
            },
            "lipinski": {
                "passed": violations <= 1, # Rule of 5 allows 1 violation
                "violations_count": violations,
                "details": violation_details
            },
            "analysis": "High drug-likeness" if qed_score > 0.6 else "Medium drug-likeness" if qed_score > 0.4 else "Low drug-likeness"
        }

    @staticmethod
    def generate_svg(smiles: str, width: int = 400, height: int = 400) -> Optional[str]:
        """Generate a 2D SVG image of the molecule."""
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return None
            
        try:
            rdDepictor.Compute2DCoords(mol)
            drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
            opts = drawer.drawOptions()
            opts.clearBackground = False
            
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            svg = drawer.GetDrawingText()
            return svg
        except Exception as e:
            print(f"Error generating SVG: {e}")
            return None
