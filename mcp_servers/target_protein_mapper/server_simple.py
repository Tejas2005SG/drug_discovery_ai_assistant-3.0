
from fastmcp import FastMCP
import httpx
import sys

mcp = FastMCP("target_protein_mapper")

@mcp.tool()
async def get_hpo_ids(symptom: str) -> str:
    """Map natural language symptom to HPO ID."""
    url = "https://api.monarchinitiative.org/v3/api/search"
    params = {"q": symptom, "category": "biolink:PhenotypicFeature", "limit": 1}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            data = resp.json()
            if data and data.get("items"):
                return str(data["items"][0]["id"])
            return "No HPO found"
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return f"Error: {str(e)}"

@mcp.tool()
async def find_target_proteins(hpo_ids: list[str]) -> list[dict]:
    """Find proteins associated with HPO IDs."""
    url = "https://api.platform.opentargets.org/api/v4/graphql"
    results = []
    async with httpx.AsyncClient() as client:
        for hid in hpo_ids:
            fid = hid.replace(":", "_")
            query = """
            query GetTargets($efoId: String!) {
              disease(efoId: $efoId) {
                associatedTargets(page: {size: 5}) {
                  rows {
                    target { approvedSymbol approvedName }
                    score
                  }
                }
              }
            }
            """
            try:
                resp = await client.post(url, json={"query": query, "variables": {"efoId": fid}})
                data = resp.json()
                disease = data.get("data", {}).get("disease")
                if disease and disease.get("associatedTargets"):
                    for row in disease["associatedTargets"]["rows"]:
                        t = row["target"]
                        results.append({
                            "symbol": t["approvedSymbol"],
                            "name": t["approvedName"],
                            "score": row["score"]
                        })
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
    return results

@mcp.tool()
async def get_protein_details(symbol: str) -> dict:
    """Get protein function and length from UniProt."""
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene_exact:{symbol} AND organism_id:9606",
        "fields": "comment_function,length",
        "format": "json", "size": 1
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            data = resp.json()
            if data.get("results"):
                entry = data["results"][0]
                length = entry.get("sequence", {}).get("length")
                func = "No function"
                for c in entry.get("comments", []):
                    if c.get("commentType") == "FUNCTION":
                        func = c.get("texts", [{}])[0].get("value", "No function")
                        break
                return {"symbol": symbol, "length": length, "function": func}
            return {"error": "Not found"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
