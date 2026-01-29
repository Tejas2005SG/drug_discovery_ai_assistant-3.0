import httpx
from typing import Dict, Any

async def get_protein_details(symbol: str) -> Dict[str, Any]:
    """
    Uses the UniProt REST API to fetch the biological function and amino acid sequence length 
    for a specific protein symbol.
    
    Args:
        symbol: The gene/protein symbol (e.g., "BRCA1").
        
    Returns:
        A dictionary with 'function' and 'length'.
    """
    url = "https://rest.uniprot.org/uniprotkb/search"
    query_params = {
        "query": f"gene_exact:{symbol} AND organism_id:9606",
        "fields": "comment_function,length",
        "format": "json",
        "size": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=query_params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                entry = data["results"][0]
                length = entry.get("sequence", {}).get("length")
                
                comments = entry.get("comments", [])
                function_text = "No function description found."
                for comment in comments:
                    if comment.get("commentType") == "FUNCTION":
                        texts = comment.get("texts", [])
                        if texts:
                            function_text = texts[0].get("value", "")
                        break
                        
                return {
                    "symbol": symbol,
                    "length": length,
                    "function": function_text
                }
            
            return {"symbol": symbol, "error": "Not found"}
            
        except Exception as e:
            import sys
            print(f"Error fetching details for {symbol}: {e}", file=sys.stderr)
            return {"symbol": symbol, "error": str(e)}
