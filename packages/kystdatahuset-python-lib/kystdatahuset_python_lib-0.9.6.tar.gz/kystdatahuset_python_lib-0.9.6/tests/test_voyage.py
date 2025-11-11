from kystdatahuset.voyage import get_voyages_for_ships_by_mmsi
from kystdatahuset.logging import logger
from datetime import datetime
from conftest import auth_jwt

def test_get_voyages_for_ships_by_mmsi(auth_jwt):
    response = get_voyages_for_ships_by_mmsi(
        auth_jwt=auth_jwt,
        mmsi_ids=[258090000, 259028000],
        start_date=datetime(2024,1,1),
        end_date=datetime(2024,5,1),
        freq="MS"
    )    
    assert response is not None, "Expected a response, got None"
    assert isinstance(response, list), "Expected response to be a list"
    logger.info(f"Retrieved {len(response)} voyages")