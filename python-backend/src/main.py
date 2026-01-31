from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.chem_refinery import ChemRefinery

app = FastAPI(title="Drug Discovery Chemical Engine")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoleculeRequest(BaseModel):
    smiles: str

@app.get("/")
def read_root():
    return {"status": "active", "service": "Chemical Logic Engine"}

@app.post("/api/chemistry/analyze")
async def analyze_molecule(request: MoleculeRequest):
    result = ChemRefinery.analyze_molecule(request.smiles)
    if not result.get("valid"):
        raise HTTPException(status_code=400, detail="Invalid SMILES string")
    return result

@app.get("/api/chemistry/render")
async def render_molecule(smiles: str):
    svg = ChemRefinery.generate_svg(smiles)
    if not svg:
        raise HTTPException(status_code=400, detail="Could not render molecule")
    return {"svg": svg}
