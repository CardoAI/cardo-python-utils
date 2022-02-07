from sqlite3 import Cursor
from typing import List, Dict


def fetch_all(cursor: Cursor) -> List[Dict]:
    """
    Returns all rows from a cursor as a list of dictionaries.

    Args:
        cursor: Cursor object storing the data to be fetched
    Returns:
         list with all the records retrieved from the db formatted as dict
    """
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
