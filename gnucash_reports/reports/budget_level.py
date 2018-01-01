"""
Simple budget graph for this.
"""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from gnucash_reports.configuration.expense_categories import get_accounts_for_category
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters


def budget_level(definition):
    accounts = parse_walker_parameters(definition.get('accounts', []))
    budget_value = definition.get('budget_value', Decimal(0.0))
    year_to_date = definition.get('year_to_date', True)

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
            split_list = get_splits(account, PeriodStart.this_year.date, PeriodEnd.this_year.date, debit=False)

            for split in split_list:
                yearly_balance += split.value

        today = PeriodStart.today.date
        data_payload.update({
            'yearlyBalance': yearly_balance,
            'daysInYear': (date(today.year+1, 1, 1) - date(today.year, 1, 1)).days,
            'currentYearDay': today.timetuple().tm_yday
        })

    return data_payload


def category_budget_level(definition):
    category = definition.pop('category')
    definition['accounts'] = get_accounts_for_category(category)
    return budget_level(definition)


def budget_planning(definition):
    income = Decimal(definition.get('income', Decimal(0.0)))
    expense_definitions = definition.get('expense_definitions', [])
    remaining_income = income

    categories = []

    for definition in expense_definitions:
        value = Decimal(definition['value'])
        categories.append(dict(name=definition['name'], value=value))
        remaining_income -= value

    return dict(income=income, categories=categories, remaining=remaining_income)
