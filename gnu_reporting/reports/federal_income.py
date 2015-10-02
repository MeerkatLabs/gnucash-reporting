"""
Attempt to determine federal tax information.
"""
from decimal import Decimal
from datetime import date

from gnu_reporting.configuration.tax_tables import calculate_tax
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_account, get_decimal, get_splits


class FederalIncomeTax(Report):
    report_type = 'federal_income'

    def __init__(self, name, income_accounts, tax_accounts):
        super(FederalIncomeTax, self).__init__(name)
        self.income_accounts = income_accounts
        self.tax_accounts = tax_accounts

    def __call__(self):

        total_income = Decimal(0.0)
        total_taxes = Decimal(0.0)

        today = date.today()
        beginning_of_year = date(today.year, 1, 1)

        for account_name in self.income_accounts:
            account = get_account(account_name)

            for split in get_splits(account, beginning_of_year):
                value = get_decimal(split.GetAmount()) * -1
                total_income += value

        for account_name in self.tax_accounts:
            account = get_account(account_name)
            for split in get_splits(account, beginning_of_year):
                value = get_decimal(split.GetAmount())
                total_taxes += value

        tax_value = calculate_tax('federal', 'married_jointly', total_income)

        result = self._generate_result()
        result['data']['income'] = total_income
        result['data']['tax_value'] = tax_value
        result['data']['taxes_paid'] = total_taxes

        return result
