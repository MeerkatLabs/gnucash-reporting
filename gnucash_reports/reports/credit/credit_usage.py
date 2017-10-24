"""
Report that will show the amount of credit available, vs. currently used.
"""
from gnucash_reports.wrapper import get_account, account_walker, get_balance_on_date
from gnucash_reports.periods import PeriodStart
from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.reports.base import Report
from decimal import Decimal
from datetime import date


class CreditUsage(Report):
    report_type = 'credit_usage'

    def __init__(self, name, credit_accounts):
        super(CreditUsage, self).__init__(name)
        self._credit_accounts = credit_accounts

    def __call__(self):

        today = date.today()

        credit_amount = Decimal(0.0)
        credit_used = Decimal(0.0)

        for credit_definition in self._credit_accounts:
            account = get_account(credit_definition['account'])
            limit = credit_definition.get('limit', '0.0')

            credit_amount += Decimal(limit)
            balance = get_balance_on_date(account, today)
            credit_used += balance

        payload = self._generate_result()
        payload['data']['credit_limit'] = credit_amount + credit_used
        payload['data']['credit_amount'] = -credit_used

        return payload


class DebtVsLiquidAssets(Report):
    report_type = 'debt_vs_liquid_assets'

    def __init__(self, name, credit_accounts, liquid_asset_accounts):
        super(DebtVsLiquidAssets, self).__init__(name)
        self._credit_accounts = credit_accounts
        self._liquid_asset_accounts = liquid_asset_accounts

    def __call__(self):

        credit_used = Decimal('0.0')
        liquid_assets = Decimal('0.0')

        currency = get_currency()

        for credit_account in account_walker(self._credit_accounts):
            credit_used += get_balance_on_date(credit_account, PeriodStart.today.date, currency)

        for liquid_asset_account in account_walker(self._liquid_asset_accounts):
            liquid_assets += get_balance_on_date(liquid_asset_account, PeriodStart.today.date, currency)

        result = self._generate_result()
        result['data']['credit_used'] = -credit_used
        result['data']['liquid_assets'] = liquid_assets

        return result
