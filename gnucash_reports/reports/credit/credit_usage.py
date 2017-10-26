"""
Report that will show the amount of credit available, vs. currently used.
"""
from decimal import Decimal

from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.periods import PeriodStart
from gnucash_reports.reports.base import Report, generate_results_package
from gnucash_reports.wrapper import get_account, account_walker, get_balance_on_date, parse_walker_parameters


class CreditUsage(Report):
    report_type = 'credit_usage'

    def __init__(self, name, **kwargs):
        super(CreditUsage, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):

        return credit_usage(self.name, None, self.kwargs)


def credit_usage(name, description, definition):
    credit_accounts = parse_walker_parameters(definition.get('credit_accounts', []))

    credit_amount = Decimal(0.0)
    credit_used = Decimal(0.0)

    for credit_definition in account_walker(**credit_accounts):
        account = get_account(credit_definition['account'])
        limit = credit_definition.get('limit', '0.0')

        credit_amount += Decimal(limit)
        balance = get_balance_on_date(account)
        credit_used += balance

    return generate_results_package(name, 'credit_usage', description,
                                    credit_limit=credit_amount + credit_used,
                                    credit_amount=credit_amount)


class DebtVsLiquidAssets(Report):
    report_type = 'debt_vs_liquid_assets'

    def __init__(self, name, **kwargs):
        super(DebtVsLiquidAssets, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return debt_vs_liquid_assets(self.name, None, self.kwargs)


def debt_vs_liquid_assets(name, description, definition):
    credit_accounts = parse_walker_parameters(definition.get('credit_accounts', []))
    liquid_accounts = parse_walker_parameters(definition.get('liquid_asset_accounts', []))
    credit_used = Decimal('0.0')
    liquid_assets = Decimal('0.0')

    currency = get_currency()

    for credit_account in account_walker(**credit_accounts):
        credit_used += get_balance_on_date(credit_account, PeriodStart.today.date, currency)

    for liquid_asset_account in account_walker(**liquid_accounts):
        liquid_assets += get_balance_on_date(liquid_asset_account, PeriodStart.today.date, currency)

    return generate_results_package(name, 'debt_vs_liquid_assets', description,
                                    credit_used=-credit_used,
                                    liquid_assets=liquid_assets)
