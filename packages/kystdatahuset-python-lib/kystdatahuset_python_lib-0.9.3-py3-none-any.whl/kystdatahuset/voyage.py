from typing import List, Dict
from requests_cache import datetime
from kystdatahuset.api_client import post_api
from kystdatahuset.types import PandasFrequency
from kystdatahuset.utils import date_range

def get_voyages_for_ships_by_mmsi(auth_jwt: str, mmsi_ids: List[int], start_date: datetime, end_date: datetime, freq: PandasFrequency = "MS") -> List[Dict]:
    """Get voyagen data for ships identified by MMSI ids

    Args:
        auth_jwt (str): A valid JWT retrieved through an authentication call to the API
        mmsi_ids (List[int]): A list of one or more MMSIs
        start_date (datetime): A start date
        end_date (datetime): An end date
        freq (PandasFrequency, optional): An optional frequency that the request will be split into. Defaults to "MS".

    Raises:
        Exception: If the API call fails or returns an error.

    Returns:
        List[Dict]: List of voyages
    """
    responses = []
    
    date_ranges = date_range(start_date, end_date, freq)
    for pair in date_ranges:
        print(pair)  # Debug print to verify date ranges    
        
        response = post_api(
            jwt_token=auth_jwt,
            fragment="api/voyage/for-ships/by-mmsi",
            payload={
                "mmsiIds": mmsi_ids,
                "startTime": start_date.isoformat(),
                "endTime": end_date.isoformat()
            },
        )
        
        if (response is None) or (not response["success"]):
            raise Exception(f"Failed to get voyages for ships by MMSI: {response['msg'] if response else 'No response'}")
        else:
            responses.extend(response["data"])

    return responses

