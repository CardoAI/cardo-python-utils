from datetime import date, datetime
from typing import List, Dict, Union, Literal

import pandas as pd

from python_utils.time import get_date, last_day_of_month


def unique_not_null_values(df: pd.DataFrame, column: str) -> List:
    """
    Get a list with unique values from the values of a dataframe column
    1. Filter the df to keep rows with notnull values in the given column
    2. Return a list with all the values of the column appearing only once

    Args:
        df: dataframe object we are getting the unique values from
        column: the column name on which we are looking for the unique values
    Returns:
        list with all unique values
    Examples:
        >>> test_df = pd.DataFrame({'col1': [1, None, 1, 3, 2], 'col2': [3, 7, 4, 1, 3]})
        >>> unique_not_null_values(test_df, 'col1')
        [1.0, 3.0, 2.0]
    """
    return df[df[column].notnull()][column].unique().tolist()


def rename_and_replace_column_information(df: pd.DataFrame, data: Dict) -> pd.DataFrame:
    """
    We use this mostly when we serialize the data from postgres.
    It replaces the column values with a dictionary and also renames the column names.
    Performs a rename of the columns

    Args:
        df: Pandas Data Frame
        data: data that maps columns and replacement/mapping as in example:
            {
            'column_in_pandas': {
                'replace_to': 'new_column_name',
                'map': {
                    1: 2,
                    2: 3
                }
            }
    Returns:
        New Modified Pandas Dataframe.
    Examples:
        >>> test_df = pd.DataFrame({'col1': ['a', 'b'], 'col2': [1, 2]})
        >>> rename_and_replace_column_information(test_df, {'col1': {'replace_to': 'new', 'map': {'a': 1}}})
          new  col2
        0   1     1
        1   b     2
        >>> test_df = pd.DataFrame({'col1': ['a', 'b'], 'col2': [1, 2]})
        >>> rename_and_replace_column_information(test_df, {})
          col1  col2
        0    a     1
        1    b     2
    """
    map_data = {key: value.get('map') for key, value in data.items()}
    if map_data:
        df.replace(map_data, inplace=True)

    rename_columns = {key: value.get('replace_to') for key, value in data.items()}
    if rename_columns:
        df.rename(columns=rename_columns, inplace=True)
    return df


def get_dates_between(
        start_date: Union[date, datetime, str],
        end_date: Union[date, datetime, str],
        inclusive: Literal["both", "neither", "left", "right"] = "both"
) -> List[date]:
    """
    1. Give start and end dates.
    2. Set inclusive if you want, by default the value is both
    3. Return list of dates
    Args:
        start_date (date, datetime, str): The left bound for the date generation by pandas
        end_date (date, datetime, str): The right bound for the date generation by pandas
        inclusive: Include boundaries; Whether to set each bound as closed or open
    Returns:
        list of date obj representing the dates in between the start and end
    Raises:
        ValueError: if one of passed dates is str and not well formatted to be converted to date obj
        Examples:
        >>> get_dates_between(date(2021, 2, 1), date(2021, 2, 3))
        [datetime.date(2021, 2, 1), datetime.date(2021, 2, 2), datetime.date(2021, 2, 3)]
        >>> get_dates_between(datetime(2021, 2, 1, 0, 0), datetime(2021, 2, 3, 0, 0))
        [datetime.date(2021, 2, 1), datetime.date(2021, 2, 2), datetime.date(2021, 2, 3)]
        >>> get_dates_between("2021-2-1", "2021-2-3")
        [datetime.date(2021, 2, 1), datetime.date(2021, 2, 2), datetime.date(2021, 2, 3)]
        >>> get_dates_between(date(2021, 2, 1), date(2021, 2, 3), inclusive="right")
        [datetime.date(2021, 2, 2), datetime.date(2021, 2, 3)]
        >>> get_dates_between("2021-2-1-1-1", "2021-3-1-1-1-1")
        Traceback (most recent call last):
        ...
        ValueError: Invalid date 2021-2-1-1-1
    """
    start_date = get_date(start_date, raise_error=True)
    end_date = get_date(end_date, raise_error=True)
    dates_range = pd.date_range(start=start_date, end=end_date, inclusive=inclusive).tolist()
    return [date(d.year, d.month, d.day) for d in dates_range]


def get_months_between_dates(
        start_date: Union[date, datetime, str],
        end_date: Union[date, datetime, str],
        inclusive: Literal["both", "neither", "left", "right"] = "both"
) -> List[date]:
    """
    Get a timestamp for each month between the two dates.
    The start_date is appended because the pandas list begins from the next month

    Args:
        start_date (date, datetime, str): The left bound for the date generation by pandas
        end_date (date, datetime, str): The right bound for the date generation by pandas
        inclusive: Include boundaries; Whether to set each bound as closed or open
    Returns:
        list of date obj representing the end date of each month in between
    Raises:
        ValueError: if one of passed dates is str and not well formatted to be converted to date obj
    Examples:
        >>> get_months_between_dates(date(2021, 2, 1), date(2021, 3, 1))
        [datetime.date(2021, 2, 28), datetime.date(2021, 3, 31)]
        >>> get_months_between_dates(datetime(2021, 2, 1, 0, 0), datetime(2021, 3, 1, 1, 1))
        [datetime.date(2021, 2, 28), datetime.date(2021, 3, 31)]
        >>> get_months_between_dates("2021-2-1", "2021-3-1")
        [datetime.date(2021, 2, 28), datetime.date(2021, 3, 31)]
        >>> get_months_between_dates(date(2021, 2, 1), date(2021, 3, 1), inclusive="right")
        [datetime.date(2021, 3, 31)]
        >>> get_months_between_dates("2021-2-1-1-1", "2021-3-1-1-1-1")
        Traceback (most recent call last):
        ...
        ValueError: Invalid date 2021-2-1-1-1
    """
    start_date = get_date(start_date, raise_error=True)
    end_date = get_date(end_date, raise_error=True)
    dates_range = pd.date_range(start_date, end_date, freq="MS", inclusive=inclusive).to_list()
    return [
        last_day_of_month(year=cur_month.year, month=cur_month.month)
        for cur_month in dates_range
    ]
