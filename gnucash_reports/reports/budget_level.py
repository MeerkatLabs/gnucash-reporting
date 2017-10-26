"""
Simple budget graph for this.
"""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from gnucash_reports.configuration.expense_categories import get_accounts_for_category
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.reports.base import Report, generate_results_package
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters


class BudgetLevel(Report):
    report_type = 'budget_level'

    def __init__(self, name, **kwargs):
        super(BudgetLevel, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return budget_level(self.name, None, self.kwargs)


def budget_level(name, description, definition):
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

        today = date.today()
        data_payload.update({
            'yearlyBalance': yearly_balance,
            'daysInYear': (date(today.year+1, 1, 1) - date(today.year, 1, 1)).days,
            'currentYearDay': today.timetuple().tm_yday
        })

    return generate_results_package(name, 'budget_level', description, **data_payload)


class CategoryBudgetLevel(BudgetLevel):
    report_type = 'category_budget_level'

    def __init__(self, name, category, budget_value):
        super(CategoryBudgetLevel, self).__init__(name, **{
            'account': get_accounts_for_category(category),
            'budget_value': budget_value
        })


class BudgetPlanning(Report):
    report_type = 'budget_planning'

    def __init__(self, name, **kwargs):
        super(BudgetPlanning, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return budget_planning(self.name, None, self.kwargs)


def budget_planning(name, description, definition):
    income = Decimal(definition.get('income', Decimal(0.0)))
    expense_definitions = definition.get('expense_definitions', [])
    remaining_income = income

    categories = []

    for definition in expense_definitions:
        value = Decimal(definition['value'])
        categories.append(dict(name=definition['name'], value=value))
        remaining_income -= value

    return generate_results_package(name, 'budget_planning', description,
                                    income=income, categories=categories,
                                    remaining=remaining_income)
