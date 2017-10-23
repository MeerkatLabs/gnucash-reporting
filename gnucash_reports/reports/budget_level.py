"""
Simple budget graph for this.
"""
from gnucash_reports.reports.base import Report
from gnucash_reports.wrapper import get_decimal, get_splits, account_walker
from gnucash_reports.configuration.expense_categories import get_accounts_for_category
from gnucash_reports.periods import PeriodStart, PeriodEnd
from decimal import Decimal
from calendar import monthrange
from datetime import date


class BudgetLevel(Report):
    report_type = 'budget_level'

    def __init__(self, name, account, budget_value, ignore_accounts=None, year_to_date=True):
        super(BudgetLevel, self).__init__(name)

        if isinstance(account, basestring):
            account = [account]

        self.account_name = account
        self.budget_value = Decimal(budget_value)

        if ignore_accounts is None:
            ignore_accounts = []
        self.ignore_accounts = ignore_accounts

        self._year_to_date = year_to_date

    def __call__(self):
        balance = Decimal('0.0')

        for account in account_walker(self.account_name, self.ignore_accounts):
            split_list = get_splits(account, PeriodStart.this_month.date, PeriodEnd.today.date, debit=False)

            for split in split_list:
                balance += get_decimal(split.GetAmount())

        payload = self._generate_result()
        payload['data']['balance'] = balance
        payload['data']['month'] = PeriodEnd.today.date.month
        payload['data']['daysInMonth'] = monthrange(PeriodEnd.today.date.year,
                                                    PeriodEnd.today.date.month)[1]
        payload['data']['today'] = PeriodEnd.today.date.day
        payload['data']['budgetValue'] = self.budget_value

        if self._year_to_date:
            yearly_balance = Decimal('0.0')

            for account in account_walker(self.account_name, self.ignore_accounts):
                split_list = get_splits(account, PeriodStart.this_year.date, PeriodEnd.this_year.date, debit=False)

                for split in split_list:
                    yearly_balance += get_decimal(split.GetAmount())

            today = date.today()
            payload['data']['yearlyBalance'] = yearly_balance
            payload['data']['daysInYear'] = (date(today.year+1, 1, 1) - date(today.year, 1, 1)).days
            payload['data']['currentYearDay'] = today.timetuple().tm_yday

        return payload


class CategoryBudgetLevel(BudgetLevel):
    report_type = 'category_budget_level'

    def __init__(self, name, category, budget_value):
        super(CategoryBudgetLevel, self).__init__(name, get_accounts_for_category(category), budget_value)


class BudgetPlanning(Report):
    report_type = 'budget_planning'

    def __init__(self, name, income, expense_definitions):
        super(BudgetPlanning, self).__init__(name)

        self.income = Decimal(income)
        self.expense_definitions = expense_definitions

    def __call__(self):
        remaining_income = self.income

        categories = []

        for definition in self.expense_definitions:
            value = Decimal(definition['value'])
            categories.append(dict(name=definition['name'], value=value))
            remaining_income -= value

        payload = self._generate_result()
        payload['data']['income'] = self.income
        payload['data']['remaining'] = remaining_income
        payload['data']['categories'] = categories

        return payload


if __name__ == '__main__':

    from gnucash_reports.wrapper import initialize
    import simplejson as json

    session = initialize('data/Accounts.gnucash')
    goal_amount = Decimal('500.00')

    report = BudgetLevel('Estimated Taxes', 'Expenses.Dining', goal_amount)
    payload = report()

    session.end()

    print json.dumps(payload)
