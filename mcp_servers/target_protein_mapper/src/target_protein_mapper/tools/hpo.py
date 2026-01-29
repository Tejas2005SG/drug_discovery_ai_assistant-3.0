import httpx

async def get_hpo_ids(symptom: str) -> str:
    """
    Takes a natural language symptom (e.g., 'fluttering heartbeat') and returns its standardized HPO ID (e.g., 'HP:0001676').
    
    Args:
        symptom: A string describing the medical symptom.
        
    Returns:
        The HPO ID string (e.g., "HP:0001676") or None if not found.
    """
    url = "https://api.monarchinitiative.org/v3/api/search"
    params = {
        "q": symptom,
        "category": "biolink:PhenotypicFeature",
        "limit": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get("items"):
                return data["items"][0]["id"]
            return None
        except Exception as e:
            import sys
            print(f"Error fetching HPO ID for '{symptom}': {e}", file=sys.stderr)
            return None
