"""
Simple budget graph for this.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_account, get_decimal, get_splits
from gnu_reporting.periods import PeriodStart, PeriodEnd
from decimal import Decimal
from calendar import monthrange


class BudgetLevel(Report):
    report_type = 'budget_level'

    def __init__(self, name, account, budget_value):
        super(BudgetLevel, self).__init__(name)
        self.account_name = account
        self.budget_value = budget_value

        self._start = PeriodStart.this_month
        self._end = PeriodEnd.today

    def __call__(self):
        account = get_account(self.account_name)

        split_list = get_splits(account, self._start.date, self._end.date, debit=False)

        balance = Decimal('0.0')
        for split in split_list:
            balance += get_decimal(split.GetAmount())

        payload = self._generate_result()
        payload['data']['balance'] = balance
        payload['data']['month'] = self._start.date.month
        payload['data']['daysInMonth'] = monthrange(self._end.date.year, self._end.date.day)[1]
        payload['data']['today'] = self._end.date.day
        payload['data']['budgetValue'] = self.budget_value

        return payload


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

    from gnu_reporting.wrapper import initialize
    from decimal import Decimal
    import simplejson as json

    session = initialize('data/Accounts.gnucash')
    goal_amount = Decimal('500.00')

    report = BudgetLevel('Estimated Taxes', 'Expenses.Dining', goal_amount)
    payload = report()

    session.end()

    print json.dumps(payload)
