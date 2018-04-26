"""
Configuration module that will set what the current date is for the rest of the application.

This is used to build reports for non current data.
"""
from datetime import datetime

_today = datetime.today().date()


def configure(configuration):
    """Configure the value returned by get_today."""
    global _today

    date = configuration.get('date', None)

    if date:
        _today = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        _today = datetime.today().date()


def get_today():
    """
    Return the configured value for today's date.

    This should be used by all date methods looking for the current date in order to do reporting.
    """
    return _today
