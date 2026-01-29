import sys
import json
import httpx
from fastmcp import FastMCP

# Redirect all logging to stderr to keep stdout clean for JSON-RPC
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("target-protein-mapper")

@mcp.tool()
async def get_hpo_ids(symptoms: str) -> str:
    """
    Convert symptom descriptions to Human Phenotype Ontology (HPO) IDs.
    
    Args:
        symptoms: Comma-separated symptom descriptions (e.g., "tremor, muscle weakness")
    
    Returns:
        JSON array of HPO matches with id, label, and score.
        Returns empty array [] if no matches found - this is normal for some symptoms.
    """
    logger.info(f"get_hpo_ids called with: {symptoms}")
    
    symptom_list = [s.strip() for s in symptoms.split(",")]
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for symptom in symptom_list:
            if not symptom:
                continue
            try:
                # Monarch Initiative API for HPO lookup
                response = await client.get(
                    "https://api.monarchinitiative.org/v3/api/search",
                    params={
                        "q": symptom,
                        "category": "biolink:PhenotypicFeature",
                        "limit": 3
                    }
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
                # Continue with other symptoms instead of failing
                continue
    
    logger.info(f"Found {len(results)} HPO matches")
    return json.dumps(results, indent=2)


@mcp.tool()
async def find_target_proteins(hpo_ids: str) -> str:
    """
    Find target proteins associated with given HPO IDs using Open Targets.
    
    Args:
        hpo_ids: Comma-separated HPO IDs (e.g., "HP:0001337,HP:0003701")
    
    Returns:
        JSON array of target proteins with gene symbol, name, and association score.
        Returns informative message if no targets found.
    """
    logger.info(f"find_target_proteins called with: {hpo_ids}")
    
    hpo_list = [h.strip() for h in hpo_ids.split(",") if h.strip().startswith("HP:")]
    
    if not hpo_list:
        return json.dumps({
            "status": "no_valid_input",
            "message": "No valid HPO IDs provided. HPO IDs should start with 'HP:'"
        })
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for hpo_id in hpo_list[:5]:  # Limit to 5 to avoid rate limits
            try:
                # Open Targets Platform GraphQL API
                query = """
                query getTargets($efoId: String!) {
                    disease(efoId: $efoId) {
                        id
                        name
                        associatedTargets(page: {size: 5, index: 0}) {
                            rows {
                                target {
                                    id
                                    approvedSymbol
                                    approvedName
                                }
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
    
    if not results:
        return json.dumps({
            "status": "no_results",
            "message": f"No protein targets found for HPO IDs: {hpo_ids}. This may be because these phenotypes don't have direct protein associations in Open Targets.",
            "suggestion": "Try using broader symptom terms or proceed with general analysis."
        })
    
    # Sort by score and return top results
    results.sort(key=lambda x: x["association_score"], reverse=True)
    logger.info(f"Found {len(results)} target proteins")
    return json.dumps(results[:10], indent=2)


@mcp.tool()
async def get_protein_details(gene_symbols: str) -> str:
    """
    Get detailed protein information from UniProt for given gene symbols.
    
    Args:
        gene_symbols: Comma-separated gene symbols (e.g., "BRCA1,TP53,EGFR")
    
    Returns:
        JSON array with protein details including function, length, and UniProt ID.
    """
    logger.info(f"get_protein_details called with: {gene_symbols}")
    
    symbols = [s.strip().upper() for s in gene_symbols.split(",") if s.strip()]
    
    if not symbols:
        return json.dumps({
            "status": "no_input",
            "message": "No gene symbols provided"
        })
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for symbol in symbols[:5]:  # Limit queries
            try:
                # UniProt REST API
                response = await client.get(
                    f"https://rest.uniprot.org/uniprotkb/search",
                    params={
                        "query": f"gene:{symbol} AND organism_id:9606",
                        "format": "json",
                        "size": 1
                    }
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
                        "function": ""
                    }
                    
                    # Extract function from comments
                    for comment in entry.get("comments", []):
                        if comment.get("commentType") == "FUNCTION":
                            texts = comment.get("texts", [])
                            if texts:
                                protein_info["function"] = texts[0].get("value", "")[:500]
                                break
                    
                    results.append(protein_info)
                    
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                results.append({
                    "gene_symbol": symbol,
                    "error": str(e)
                })
    
    logger.info(f"Retrieved details for {len(results)} proteins")
    return json.dumps(results, indent=2)


if __name__ == "__main__":
    # CRITICAL: Run in stdio mode with no console output
    # All logs go to stderr, only JSON-RPC goes to stdout
    mcp.run(transport="stdio")
