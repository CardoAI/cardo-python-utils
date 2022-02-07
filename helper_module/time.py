from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Union, Optional, Generator

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"


def date_range(start_date: date, end_date: date) -> Generator[date, None, None]:
    """
    Generator for yield-ing date objects in a given range. If start_date == end_date
    it still yields just one time the value. INCLUDES end_date!
    Args:
        start_date: date obj from where to start the generator e.g: date(2021, 1, 1)
        end_date: date obj from where to start the generator e.g: date(2021, 1, 1),
                    included in the end
    Returns:
        Generator for date range
    Examples:
        >>> a = date_range(date(2021, 1, 1), date(2021, 2, 1))
        >>> print(type(a))
        <class 'generator'>
        >>> sum(1 for _ in a)
        32
    """
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


def last_day_of_month(month: int, year: int) -> date:
    """
    Take the month and year and return a datetime object representing
    the last day of the given month. Supports leap years.
    Args:
        year: Int representing the year
        month: Int between 1-12 representing the month
    Returns:
        datetime obj representing the last day of month
    Examples:
        >>> last_day_of_month(1, 2022)
        datetime.date(2022, 1, 31)
        >>> last_day_of_month(2, 2021)
        datetime.date(2021, 2, 28)
        >>> last_day_of_month(2, 2020)
        datetime.date(2020, 2, 29)
    """
    current_month_last_day = monthrange(year, month)[1]
    return date(year, month, current_month_last_day)


def get_previous_end_of_month(reference_date: timezone.datetime.date) -> date:
    """
    Take a date object and return the last date of the previous month
    Eg: date(2021, 2, 6) -> returns date(2021, 1, 31)
    Args:
        reference_date: date object
    Returns:
         date object
    Examples:
        >>> get_previous_end_of_month(date(2021, 2, 6))
        datetime.date(2021, 1, 31)
        >>> get_previous_end_of_month(date(2021, 1, 1))
        datetime.date(2020, 12, 31)
    """
    return reference_date.replace(day=1) - relativedelta(days=1)


def date_to_datetime(date_to_convert: date) -> datetime:
    """
    Convert from date obj to datetime obj
    Args:
        date_to_convert: date obj to convert
    Returns:
        datetime obje
    Examples:
          >>> date_to_datetime(date(2021, 5, 23))
          datetime.datetime(2021, 5, 23, 0, 0)
    """
    return datetime(
        year=date_to_convert.year,
        month=date_to_convert.month,
        day=date_to_convert.day
    )


def get_datetime(
        value: Optional[Union[date, datetime, str]],
        raise_error=False
) -> Optional[datetime]:
    """
    Convert a given value to a datetime.
    Args:
        raise_error: flag to raise error if return is None or not
        value: to be converted. Can be date/datetime obj as well as str formated in date/datetime
    Returns:
        datetime obj
    Raises:
        ValueError: If raise_error flag is True and parsed_datetime is None
    Examples:
        >>> get_datetime(date(2021, 1, 1))
        datetime.datetime(2021, 1, 1, 0, 0)
        >>> get_datetime(datetime(2021, 1, 1, 0, 2))
        datetime.datetime(2021, 1, 1, 0, 2)
        >>> get_datetime('2021-1-1')
        datetime.datetime(2021, 1, 1, 0, 0)
        >>> get_datetime('2021-20-20-20-20') is None
        True
        >>> get_datetime(None) is None
        True
        >>> get_datetime('2021-20-20-20-20', raise_error=True)
        Traceback (most recent call last):
        ...
        ValueError: Invalid datetime 2021-20-20-20-20
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return date_to_datetime(value)

    # A common date is in the form "2020-01-01", 10 characters
    if value is not None:
        if len(value) > 10:
            parsed_datetime = parse_datetime(value)
        else:
            parsed_date = parse_date(value)
            parsed_datetime = date_to_datetime(parsed_date) if parsed_date else None
    else:
        parsed_datetime = None

    if parsed_datetime is None and raise_error:
        raise ValueError(f"Invalid datetime {value}")
    return parsed_datetime


def get_date(
        value: Optional[Union[date, datetime, str]],
        raise_error=False
) -> Optional[date]:
    """
    Convert a given value to a date.
    Args:
        raise_error: flag to raise error if return is None or not
        value: to be converted. Can be date/datetime obj as well as str formatted in date/datetime
    Returns:
        date obj
    Raises:
        ValueError: If raise_error flag is True and parsed_date is None
    Examples:
        >>> get_date(date(2021, 1, 1))
        datetime.date(2021, 1, 1)
        >>> get_date(datetime(2021, 1, 1, 0, 2))
        datetime.date(2021, 1, 1)
        >>> get_date('2020-01-01 13:12:13')
        datetime.date(2020, 1, 1)
        >>> get_date('sadasadasdas') is None
        True
        >>> get_date(None) is None
        True
        >>> get_date('2021-20-20-20-20', raise_error=True)
        Traceback (most recent call last):
        ...
        ValueError: Invalid date 2021-20-20-20-20
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    if value is not None:
        # A common date is in the form "2020-01-01", 10 characters
        if len(value) > 10:
            parsed_date = parse_datetime(value)
            parsed_date = parsed_date.date() if parsed_date else None
        else:
            parsed_date = parse_date(value)
    else:
        parsed_date = None

    if parsed_date is None and raise_error:
        raise ValueError(f"Invalid date {value}")

    return parsed_date


def difference_months(start_date: date, end_date: date) -> int:
    """
    Get the difference in months between two date objects.
    Args:
        start_date (date): the beginning of the period
        end_date (date): the end of the period
    Returns:
        difference as int
    Examples:
        >>> difference_months(date(2020, 10, 1), date(2021, 10, 1))
        12
        >>> difference_months(date(2021, 10, 1), date(2021, 10, 1))
        0
        >>> difference_months(date(2021, 10, 1), date(2021, 8, 1))
        -2
    """
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def get_last_date_of_week(reference_date: Optional[date] = None) -> date:
    """
    1.Give a reference date or get the current date as a start point.
    2.Return the last day of the week the given date is in.
    Args:
        reference_date: day in the week to start the search for
    Returns:
        last day of the week
    Examples:
        >>> get_last_date_of_week(date(2022, 1, 27))
        datetime.date(2022, 1, 30)
    """
    if not reference_date:  # pragma: no cover
        reference_date = timezone.localdate()
    return reference_date + relativedelta(days=6 - reference_date.weekday())
