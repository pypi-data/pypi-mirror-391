from typing import List
import pandas as pd 
from datetime import datetime
from kystdatahuset.types import PandasFreqency
from more_itertools import pairwise

def date_range(start_date: datetime, end_date: datetime, freq: PandasFreqency = "D") -> List[datetime]:
    """
    Generate a list of dates from start_date to end_date, inclusive.
    """
    if start_date > end_date:
        raise ValueError("start_date must be less than or equal to end_date")
    
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    return pairwise([dt.to_pydatetime() for dt in dates])    
