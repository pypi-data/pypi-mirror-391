from datetime import datetime
from conftest import auth_jwt, wkt
from kystdatahuset.ais import get_ais_positions_within_geom_time
from kystdatahuset.logging import logger

def test_get_ais_pos_for_geom_time(auth_jwt, wkt):
    response = get_ais_positions_within_geom_time(
        jwt_token=auth_jwt,
        geometry=wkt,
        start_time=datetime(2024, 1, 1),
        end_time=datetime(2024, 1, 2),
    )
    assert response is not None, "Expected a response, got None"
    assert isinstance(response, list), "Expected response to be a list"
    assert len(response) > 0, "Expected non-empty response list"
    assert all(len(item) == 12 for item in response), "Expected all items in response to be of length >= 5"
    logger.info(f"Response sample: {response[:2]}")
    logger.info(f"Retrieved {len(response)} AIS positions")
