"""
Attempt to determine federal tax information.
"""
from decimal import Decimal

from gnucash_reports.configuration.tax_tables import calculate_tax
from gnucash_reports.reports.base import Report
from gnucash_reports.wrapper import get_account, get_splits
from gnucash_reports.periods import PeriodStart, PeriodEnd


class IncomeTax(Report):
    report_type = 'income_tax'

    def __init__(self, name, income_accounts, tax_accounts, period_start=PeriodStart.this_year,
                 period_end=PeriodEnd.this_year, tax_name='federal', tax_status='single'):
        super(IncomeTax, self).__init__(name)
        self.income_accounts = income_accounts
        self.tax_accounts = tax_accounts
        self._start = PeriodStart(period_start)
        self._end = PeriodEnd(period_end)

        self._tax_name = tax_name
        self._tax_status = tax_status

    def __call__(self):

        total_income = Decimal(0.0)
        total_taxes = Decimal(0.0)

        for account_name in self.income_accounts:
            account = get_account(account_name)

            for split in get_splits(account, self._start.date, self._end.date):
                value = split.value * -1
                total_income += value

        for account_name in self.tax_accounts:
            account = get_account(account_name)
            for split in get_splits(account,  self._start.date, self._end.date):
                value = split.value
                total_taxes += value

        tax_value = calculate_tax(self._tax_name, self._tax_status, total_income)

        result = self._generate_result()
        result['data']['income'] = total_income
        result['data']['tax_value'] = tax_value
        result['data']['taxes_paid'] = total_taxes

        return result
