"""
Provides the inflation rate from the configuration file.
"""
from decimal import Decimal

_inflation = Decimal('0.00')


def configure(json_dictionary):
    global _inflation

    _inflation = Decimal(json_dictionary.get('inflation', '0.00'))


def get_inflation():
    return _inflation
