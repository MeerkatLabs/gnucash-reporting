"""
Simple budget graphs.
"""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters


def budget_level(accounts=None, budget_value='0.0', year_to_date=True):
    """
    Calculates how much is spent in the accounts provided.
    :param accounts: account walker parameters to calculate spending in.
    :param budget_value: budget value for the month
    :param year_to_date: should a year to date be calculated as well

    :return: dictionary containing:
    balance - the current balance for the month
    month - the month number
    daysInMonth - the number of days in the month
    today - current day in the month
    budgetValue - the maximum allowed to be spent in this month

    Optional values returned if year_to_date is true:
    yearlyBalance - the amount spent in these accounts this year
    daysInYear - the number of days in the current year
    currentYearDay - the current year day for this year
    """
    accounts = accounts or []
    budget_value = Decimal(budget_value or '0.0')

    accounts = parse_walker_parameters(accounts)
    budget_value = Decimal(budget_value)

    balance = Decimal('0.0')

    for account in account_walker(**accounts):
        split_list = get_splits(account, PeriodStart.this_month.date, PeriodEnd.today.date, debit=False)

        for split in split_list:
            balance += split.value

    data_payload = {
        'balance': balance,
        'month': PeriodEnd.today.date.month,
        'daysInMonth': monthrange(PeriodEnd.today.date.year, PeriodEnd.today.date.month)[1],
        'today': PeriodEnd.today.date.day,
        'budgetValue': budget_value
    }

    if year_to_date:
        yearly_balance = Decimal('0.0')

        for account in account_walker(**accounts):
            split_list = get_splits(account, PeriodStart.this_year.date, PeriodEnd.today.date, debit=False)

            for split in split_list:
                yearly_balance += split.value

        today = PeriodStart.today.date
        data_payload.update({
            'yearlyBalance': yearly_balance,
            'daysInYear': (date(today.year+1, 1, 1) - date(today.year, 1, 1)).days,
            'currentYearDay': today.timetuple().tm_yday
        })

    return data_payload


def budget_planning(income='0.0', expense_definitions=None):
    """
    Shows how successful budget plan is based on the income amount provided.
    :param income: how much income per month is brought in.
    :param expense_definitions: list of categories that are part of the budget, each is a dictionary containing:
    name: a name for the category
    value: the amount budgeted for that category
    :return: dictionary containing:
    income - the income value that is passed into this report
    categories - the expense_definitions that are passed into this report
    remaining - the amount of income that is remaining after all of the categories have been added together.
    """
    income = Decimal(income)
    expense_definitions = expense_definitions or []
    remaining_income = income

    categories = []

    for definition in expense_definitions:
        value = Decimal(definition['value'])

        categories.append({'name': definition['name'],
                           'value': value})

        remaining_income -= value

    return {
        'income': income,
        'categories': categories,
        'remaining': remaining_income
    }
