"""
Simple budget graph for this.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_account, get_decimal, get_splits
from datetime import date
from decimal import Decimal
from calendar import monthrange


class BudgetLevel(Report):
    report_type = 'budget_level'

    def __init__(self, name, account, budget_value):
        super(BudgetLevel, self).__init__(name)
        self.account_name = account
        self.budget_value = budget_value

    def __call__(self):
        account = get_account(self.account_name)

        today = date.today()
        beginning_of_month = date(today.year, today.month, 1)

        split_list = get_splits(account, beginning_of_month, today, debit=False)

        balance = Decimal('0.0')
        for split in split_list:
            balance += get_decimal(split.GetAmount())

        payload = self._generate_result()
        payload['data']['balance'] = balance
        payload['data']['month'] = beginning_of_month.month
        payload['data']['daysInMonth'] = monthrange(today.year, today.month)[1]
        payload['data']['today'] = today.day
        payload['data']['budgetValue'] = self.budget_value

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
