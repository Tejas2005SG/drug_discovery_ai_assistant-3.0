import sys
import json
import httpx
from fastmcp import FastMCP

# Redirect all logging to stderr to keep stdout clean for JSON-RPC
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("target-protein-mapper")

# --- Logic Functions (Plain Python, No Decorators) ---

async def _get_hpo_ids_logic(symptoms: str) -> list:
    logger.info(f"Mapping symptoms: {symptoms}")
    symptom_list = [s.strip() for s in symptoms.split(",")]
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for symptom in symptom_list:
            if not symptom: continue
            try:
                response = await client.get(
                    "https://api.monarchinitiative.org/v3/api/search",
                    params={"q": symptom, "category": "biolink:PhenotypicFeature", "limit": 3}
                )
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    if item.get("id", "").startswith("HP:"):
                        results.append({
                            "symptom": symptom,
                            "hpo_id": item["id"],
                            "label": item.get("name", ""),
                            "score": item.get("score", 0)
                        })
            except Exception as e:
                logger.error(f"Error looking up '{symptom}': {e}")
                continue
    return results

async def _find_target_proteins_logic(hpo_ids: str) -> list:
    logger.info(f"Finding targets for: {hpo_ids}")
    hpo_list = [h.strip() for h in hpo_ids.split(",") if h.strip().startswith("HP:")]
    if not hpo_list: return []
    
    results = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for hpo_id in hpo_list[:5]:
            try:
                query = """
                query getTargets($efoId: String!) {
                    disease(efoId: $efoId) {
                        associatedTargets(page: {size: 5, index: 0}) {
                            rows {
                                target { id approvedSymbol approvedName }
                                score
                            }
                        }
                    }
                }
                """
                response = await client.post(
                    "https://api.platform.opentargets.org/api/v4/graphql",
                    json={"query": query, "variables": {"efoId": hpo_id}}
                )
                response.raise_for_status()
                data = response.json()
                disease_data = data.get("data", {}).get("disease")
                if disease_data and disease_data.get("associatedTargets"):
                    for row in disease_data["associatedTargets"]["rows"]:
                        target = row["target"]
                        results.append({
                            "hpo_id": hpo_id,
                            "gene_symbol": target["approvedSymbol"],
                            "gene_name": target["approvedName"],
                            "association_score": row["score"],
                            "ensembl_id": target["id"]
                        })
            except Exception as e:
                logger.error(f"Error querying {hpo_id}: {e}")
                continue
    results.sort(key=lambda x: x["association_score"], reverse=True)
    return results[:10]

async def _get_protein_details_logic(gene_symbols: str) -> list:
    logger.info(f"Getting details for: {gene_symbols}")
    symbols = [s.strip().upper() for s in gene_symbols.split(",") if s.strip()]
    if not symbols: return []
    
    results = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for symbol in symbols[:5]:
            try:
                response = await client.get(
                    "https://rest.uniprot.org/uniprotkb/search",
                    params={"query": f"gene:{symbol} AND organism_id:9606", "format": "json", "size": 1}
                )
                response.raise_for_status()
                data = response.json()
                if data.get("results"):
                    entry = data["results"][0]
                    protein_info = {
                        "gene_symbol": symbol,
                        "uniprot_id": entry.get("primaryAccession", ""),
                        "protein_name": entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "Unknown"),
                        "length": entry.get("sequence", {}).get("length", 0),
                        "function": "No function found"
                    }
                    for comment in entry.get("comments", []):
                        if comment.get("commentType") == "FUNCTION":
                            texts = comment.get("texts", [])
                            if texts:
                                protein_info["function"] = texts[0].get("value", "")[:500]
                                break
                    results.append(protein_info)
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue
    return results

# --- MCP Tool Registrations ---

@mcp.tool()
async def get_hpo_ids(symptoms: str) -> str:
    """Convert symptom descriptions to Human Phenotype Ontology (HPO) IDs."""
    results = await _get_hpo_ids_logic(symptoms)
    return json.dumps(results, indent=2)

@mcp.tool()
async def find_target_proteins(hpo_ids: str) -> str:
    """Find target proteins associated with given HPO IDs."""
    results = await _find_target_proteins_logic(hpo_ids)
    if not results:
        return json.dumps({"status": "no_results", "message": "No protein targets found."})
    return json.dumps(results, indent=2)

@mcp.tool()
async def get_protein_details(gene_symbols: str) -> str:
    """Get detailed protein information from UniProt for given gene symbols."""
    results = await _get_protein_details_logic(gene_symbols)
    return json.dumps(results, indent=2)

@mcp.tool()
async def resolve_symptoms_to_proteins(symptoms: str) -> str:
    """
    COMPOSITE TOOL: Resolves symptoms to a complete biological dossier in ONE turn.
    Performs HPO mapping, Target discovery, and Protein detail fetching internally.
    """
    # 1. Map to HPO
    hpos = await _get_hpo_ids_logic(symptoms)
    if not hpos:
        return json.dumps({"status": "error", "message": "No HPO IDs found."})
    
    hpo_str = ",".join([r["hpo_id"] for r in hpos])
    
    # 2. Find Targets
    targets = await _find_target_proteins_logic(hpo_str)
    if not targets:
        return json.dumps({"status": "no_targets", "phenotypes": hpos})
    
    # 3. Get Details
    symbols_str = ",".join([t["gene_symbol"] for t in targets[:5]])
    details = await _get_protein_details_logic(symbols_str)
    
    return json.dumps({
        "status": "success",
        "phenotypes": hpos,
        "molecular_targets": details,
        "raw_associations": targets[:5]
    }, indent=2)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
