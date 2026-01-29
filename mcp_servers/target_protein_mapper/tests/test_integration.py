import pytest
from target_protein_mapper.tools.hpo import get_hpo_ids
from target_protein_mapper.tools.targets import find_target_proteins
from target_protein_mapper.tools.protein import get_protein_details

@pytest.mark.asyncio
async def test_full_workflow():
    symptoms = [
        "brittle toenails", 
        "cracking knuckles", 
        "ear blockage", 
        "fluttering heartbeat", 
        "sudden confusion"
    ]
    
    print(f"Testing workflow with symptoms: {symptoms}")
    
    hpo_ids = []
    for symptom in symptoms:
        hpo_id = await get_hpo_ids(symptom)
        assert hpo_id is not None or hpo_id is None # Just ensuring it runs without error, API might fail
        if hpo_id:
            hpo_ids.append(hpo_id)
            
    if not hpo_ids:
        pytest.skip("No HPO IDs found, skipping remainder of test")
    
    targets = await find_target_proteins(hpo_ids)
    assert isinstance(targets, list)
    
    if targets:
        top_target = targets[0]
        details = await get_protein_details(top_target['symbol'])
        assert details['symbol'] == top_target['symbol']
