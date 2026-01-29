import httpx
from typing import List, Dict, Any

async def find_target_proteins(hpo_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Takes a list of HPO IDs and queries the Open Targets GraphQL API to find proteins (targets) 
    associated with these phenotypes.
    
    Args:
        hpo_ids: A list of HPO ID strings (e.g., ["HP:0001676"]).
        
    Returns:
        A list of dictionaries containing protein 'symbol', 'name', and 'association_score'.
    """
    url = "https://api.platform.opentargets.org/api/v4/graphql"
    results = []
    
    async with httpx.AsyncClient() as client:
        for hpo_id in hpo_ids:
            # Open Targets typically expects IDs like HP_0001676 for HPO, replacing ':' with '_'
            formatted_id = hpo_id.replace(":", "_")
            
            query = """
            query GetTargets($efoId: String!) {
              disease(efoId: $efoId) {
                associatedTargets(page: {size: 10}) {
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
            
            variables = {"efoId": formatted_id}
            
            try:
                response = await client.post(url, json={"query": query, "variables": variables})
                response.raise_for_status()
                data = response.json()
                
                disease_data = data.get("data", {}).get("disease")
                if disease_data and disease_data.get("associatedTargets"):
                    rows = disease_data["associatedTargets"]["rows"]
                    for row in rows:
                        target = row["target"]
                        results.append({
                            "symbol": target["approvedSymbol"],
                            "name": target["approvedName"],
                            "association_score": row["score"],
                            "source_hpo": hpo_id
                        })
            except Exception as e:
                import sys
                print(f"Error fetching targets for {hpo_id}: {e}", file=sys.stderr)
                
    return results
