"""
Report that will show the amount of credit available, vs. currently used.
"""
from decimal import Decimal

from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.periods import PeriodStart
from gnucash_reports.wrapper import get_account, account_walker, get_balance_on_date, parse_walker_parameters


def credit_usage(definition):
    credit_accounts = definition.get('credit_accounts', [])

    credit_amount = Decimal(0.0)
    credit_used = Decimal(0.0)

    for credit_definition in credit_accounts:
        account = get_account(credit_definition['account'])
        limit = credit_definition.get('limit', '0.0')

        credit_amount += Decimal(limit)
        balance = get_balance_on_date(account)
        credit_used += balance

    return {
        'credit_limit': credit_amount + credit_used,
        'credit_amount': credit_amount
    }


def debt_vs_liquid_assets(definition):
    credit_accounts = parse_walker_parameters(definition.get('credit_accounts', []))
    liquid_accounts = parse_walker_parameters(definition.get('liquid_asset_accounts', []))
    credit_used = Decimal('0.0')
    liquid_assets = Decimal('0.0')

    currency = get_currency()

    for credit_account in account_walker(**credit_accounts):
        credit_used += get_balance_on_date(credit_account, PeriodStart.today.date, currency)

    for liquid_asset_account in account_walker(**liquid_accounts):
        liquid_assets += get_balance_on_date(liquid_asset_account, PeriodStart.today.date, currency)

    return dict(credit_used=-credit_used, liquid_assets=liquid_assets)
