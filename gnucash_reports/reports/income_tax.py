"""
Attempt to determine federal tax information.
"""
from decimal import Decimal

from gnucash_reports.configuration.tax_tables import calculate_tax
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.reports.base import Report, generate_results_package
from gnucash_reports.wrapper import get_account, get_splits, account_walker, parse_walker_parameters


class IncomeTax(Report):
    report_type = 'income_tax'

    def __init__(self, name, **kwargs):
        super(IncomeTax, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return income_tax(self.name, None, self.kwargs)


def income_tax(name, description, definition):
    income_accounts = parse_walker_parameters(definition.get('income_accounts', []))
    tax_accounts = parse_walker_parameters(definition.get('tax_accounts', []))
    period_start = PeriodStart(definition.get('period_start', PeriodStart.this_year))
    period_end = PeriodEnd(definition.get('period_end', PeriodEnd.this_year))
    tax_name = definition.get('tax_name', 'federal')
    tax_status = definition.get('tax_status', 'single')

    total_income = Decimal(0.0)
    total_taxes = Decimal(0.0)

    for account in account_walker(**income_accounts):
        for split in get_splits(account, period_start.date, period_end.date):
            value = split.value * -1  # negate the value because income is leaving these accounts
            total_income += value

    for account_name in account_walker(**tax_accounts):
        account = get_account(account_name)
        for split in get_splits(account,  period_start.date, period_end.date):
            value = split.value
            total_taxes += value

    tax_value = calculate_tax(tax_name, tax_status, total_income)

    return generate_results_package(name, 'income_tax', description,
                                    income=total_income,
                                    tax_value=tax_value,
                                    taxes_paid=total_taxes)
