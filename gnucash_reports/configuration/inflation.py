"""
Provides the inflation rate from the configuration file.
"""
from decimal import Decimal

_inflation = Decimal('0.00')


def configure(configuration):
    """Configure an annual inflation value."""
    global _inflation

    _inflation = Decimal(configuration.get('annual_inflation', '0.00'))


def get_annual_inflation():
    """Return annual inflation."""
    return _inflation


def get_monthly_inflation():
    """Return monthly inflation value."""
    return _inflation / Decimal('12')
