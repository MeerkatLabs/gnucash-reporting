"""
Report that will show the amount of credit available, vs. currently used.
"""
from decimal import Decimal

from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.periods import PeriodStart
from gnucash_reports.wrapper import get_account, account_walker, get_balance_on_date, parse_walker_parameters


def credit_usage(credit_accounts=None):
    """
    Report generates a usage vs limit data set for the credit accounts that are defined.

    definition contains:
    :param credit_accounts: list of dictionaries containing credit card accounts and limits on those accounts
      - account - full name of the account to look up balance of.
      - limit - maximum amount that can be debited from that account.
    :return: dictionary containing:
    - credit_limit - total limit from all accounts
    - credit_amount - the amount of credit used on all accounts
    """
    credit_accounts = credit_accounts or []

    credit_limit = Decimal(0.0)
    credit_used = Decimal(0.0)

    for credit_definition in credit_accounts:
        account = get_account(credit_definition['account'])
        limit = credit_definition.get('limit', '0.0')

        balance = get_balance_on_date(account)
        credit_used -= balance
        credit_limit += Decimal(limit)

    return {
        'credit_limit': credit_limit,
        'credit_amount': credit_used
    }


def debt_vs_liquid_assets(credit_accounts=None, liquid_asset_accounts=None):
    """
    Provides a report showing the balances of credit_accounts and liquid_asset_accounts.  This data can be used to show
    if there is enough liquid assets to be able to cover credit card debt.
    :param credit_accounts: account walking parameters for all of the credit accounts to be used in this report.
    :param liquid_asset_accounts: account walking parameters for all of the liquid asset accounts to be used in this
    report.
    :return: dictionary showing results
    - credit_used - currency amount showing how much credit is being used.
    - liquid_assets - currency amount showing how much is in the liquid asset_accounts
    """
    credit_accounts = parse_walker_parameters(credit_accounts)
    liquid_accounts = parse_walker_parameters(liquid_asset_accounts)
    credit_used = Decimal('0.0')
    liquid_assets = Decimal('0.0')

    currency = get_currency()

    for credit_account in account_walker(**credit_accounts):
        # Multiplying by account.sign because if this is a liability account, the value is negative.  For the report
        # it should be a positive value because it shows that there is credit used.
        credit_used += get_balance_on_date(credit_account, PeriodStart.today.date, currency) * credit_account.sign

    for liquid_asset_account in account_walker(**liquid_accounts):
        liquid_assets += get_balance_on_date(liquid_asset_account, PeriodStart.today.date, currency)

    return {
        'credit_used': credit_used,
        'liquid_assets': liquid_assets
    }
