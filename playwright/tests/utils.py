"""
Useful functions for testing.
"""

from datetime import datetime


def validate_date_format(date: str, date_format: str) -> bool:
    """
    Validate the format of a date on the website is as expected.
    """
    ALLOWED_DATE_FORMATS = "%d %B %Y"

    if date_format not in ALLOWED_DATE_FORMATS:
        raise ValueError(f"Date format: {date_format} is not supported")

    try:
        datetime.strptime(date, date_format)
    except ValueError as exc:
        raise AssertionError("Date format is incorrect") from exc
