import re
from calendar import monthrange
from datetime import datetime, date, timedelta, timezone
from typing import Union, Optional, Generator

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

# ------------------------ Taken from django dateparse ----------------------- #

datetime_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:[\.,](?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'\s*(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)

date_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
)


def get_fixed_timezone(offset):  # pragma no cover
    """Return a tzinfo instance with a fixed offset from UTC."""
    if isinstance(offset, timedelta):
        offset = offset.total_seconds() // 60
    sign = '-' if offset < 0 else '+'
    hhmm = '%02d%02d' % divmod(abs(offset), 60)
    name = sign + hhmm
    return timezone(timedelta(minutes=offset), name)


def parse_datetime(value):  # pragma no cover
    """Parse a string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.

    Raise ValueError if the input is well formatted but not a valid datetime.
    Return None if the input isn't well formatted.
    """
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        if match := datetime_re.match(value):
            kw = match.groupdict()
            kw['microsecond'] = kw['microsecond'] and kw['microsecond'].ljust(6, '0')
            tzinfo = kw.pop('tzinfo')
            if tzinfo == 'Z':
                tzinfo = timezone.utc
            elif tzinfo is not None:
                offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
                offset = 60 * int(tzinfo[1:3]) + offset_mins
                if tzinfo[0] == '-':
                    offset = -offset
                tzinfo = get_fixed_timezone(offset)
            kw = {k: int(v) for k, v in kw.items() if v is not None}
            return datetime(**kw, tzinfo=tzinfo)


def parse_date(value):  # pragma no cover
    """Parse a string and return a datetime.date.

    Raise ValueError if the input is well formatted but not a valid date.
    Return None if the input isn't well formatted.
    """
    try:
        return date.fromisoformat(value)
    except ValueError:
        if match := date_re.match(value):
            kw = {k: int(v) for k, v in match.groupdict().items()}
            return date(**kw)


# ---------------------------------------------------------------------------- #

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
    Take the month and year and return a date representing
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


def get_previous_end_of_month(reference_date: date) -> date:
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
    return reference_date.replace(day=1) - timedelta(days=1)


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
        reference_date = date.today()
    return reference_date + timedelta(days=6 - reference_date.weekday())
