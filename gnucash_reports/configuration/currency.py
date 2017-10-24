"""
Contains the details about the base currency of the application.
"""
from gnucash_reports.wrapper import get_account

_currency = None


def configure(json_configuration):
    global _currency
    account_name = json_configuration.get('currency', dict()).get('account_name', 'Income')

    _currency = get_account(account_name).commodity


def get_currency():
    """
    Retrieve the base currency value for the application.
    :return:
    """
    return _currency
