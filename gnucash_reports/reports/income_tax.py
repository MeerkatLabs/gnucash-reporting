"""
Attempt to determine federal tax information.
"""
from decimal import Decimal

from gnucash_reports.configuration.tax_tables import calculate_tax
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters
from gnucash_reports.utilities import clean_account_name


def income_tax(income=None, tax=None, start=PeriodStart.this_year, end=PeriodEnd.this_year,
               tax_name='federal', tax_status='single', deductions=None, deduction=None):
    """
    Walk through all of the income accounts provided to determine tax owed based on tax tables.  Then use deductions,
    deduction_accounts to reduce income, and then calculate a simple tax owed based on the tax_name and tax_status
    information.  Will only use the account data between the start and end values.
    :param income: account walker parameters for the income accounts
    :param tax: account walker parameters for the tax paid accounts
    :param start: Period start date
    :param end: Period end date,
    :param tax_name: name of tax table to use
    :param tax_status: name of tax sub-table to use
    :param deductions: list of decimal definitions that should be deducted from the taxable income
    :param deduction: account walker parameters that should be used to reduce the taxable income as well
    :return: dictionary containing
    income - total taxable income made during the period
    tax_value - total calculated tax based on income value
    taxes_paid - total taxes paid into the tax accounts
    """

    income_accounts = income or []
    tax_accounts = tax or []
    deductions = deductions or []
    deduction_accounts = deduction or []

    income_accounts = parse_walker_parameters(income_accounts)
    tax_accounts = parse_walker_parameters(tax_accounts)
    period_start = PeriodStart(start)
    period_end = PeriodEnd(end)
    deduction_accounts = parse_walker_parameters(deduction_accounts)

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

    return {'income': total_income, 'tax_value': tax_value, 'taxes_paid': total_taxes}
