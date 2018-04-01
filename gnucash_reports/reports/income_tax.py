"""
Attempt to determine federal tax information.
"""
from decimal import Decimal

from gnucash_reports.configuration.tax_tables import calculate_tax
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters
from gnucash_reports.utilities import clean_account_name


def income_tax(definition):
    income_accounts = parse_walker_parameters(definition.get('income_accounts', []))
    tax_accounts = parse_walker_parameters(definition.get('tax_accounts', []))
    period_start = PeriodStart(definition.get('period_start', PeriodStart.this_year))
    period_end = PeriodEnd(definition.get('period_end', PeriodEnd.this_year))
    tax_name = definition.get('tax_name', 'federal')
    tax_status = definition.get('tax_status', 'single')
    deductions = definition.get('deductions', [])
    deduction_accounts = parse_walker_parameters(definition.get('deduction_accounts', []))

    total_income = Decimal(0.0)
    total_taxes = Decimal(0.0)
    pre_tax_deductions = Decimal(0.0)

    # Find all of the deduction accounts, and store them in a list so that they can be walked when handling the
    # income from the income accounts
    deduction_account_names = set()
    for account in account_walker(**deduction_accounts):
        deduction_account_names.add(clean_account_name(account.fullname))

    # Calculate all of the income that has been received, and calculate all of the contributions to the deduction
    # accounts that will reduce tax burden.
    for account in account_walker(**income_accounts):
        for split in get_splits(account, period_start.date, period_end.date):
            value = split.value * -1  # negate the value because income is leaving these accounts
            total_income += value

            # Go through the split's parent and find all of the values that are in the deduction accounts as well
            transaction = split.transaction
            for t_split in transaction.splits:
                if clean_account_name(t_split.account.fullname) in deduction_account_names:
                    pre_tax_deductions += t_split.value

    # Calculate all of the taxes that have been currently paid
    for account in account_walker(**tax_accounts):
        for split in get_splits(account,  period_start.date, period_end.date):
            value = split.value
            total_taxes += value

    # Remove all of the deductions from the total income value
    for deduction in deductions:
        pre_tax_deductions += Decimal(deduction)

    # Remove all of the contributions from the income accounts that went into pre-tax accounts and any standard
    # deductions
    total_income -= pre_tax_deductions

    tax_value = calculate_tax(tax_name, tax_status, total_income)

    return dict(income=total_income, tax_value=tax_value, taxes_paid=total_taxes)
