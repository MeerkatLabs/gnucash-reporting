"""
Chart that will show the cash flow from income accounts to expense accounts.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.collate.bucket import PeriodCollate
from gnu_reporting.collate.bucket_generation import debit_credit_generator
from gnu_reporting.collate.store import store_credit_debit
from gnu_reporting.periods import PeriodEnd, PeriodStart, PeriodSize
from gnu_reporting.wrapper import get_balance_on_date, account_walker, get_splits, get_decimal
import time


class IncomeVsExpense(Report):
    report_type = 'income_vs_expense'

    def __init__(self, name, income_accounts, expense_accounts, period_start=PeriodStart.this_month_year_ago,
                 period_end=PeriodEnd.this_month, period_size=PeriodSize.month):
        super(IncomeVsExpense, self).__init__(name)
        self._income = income_accounts
        self._expenses = expense_accounts
        self._period_start = PeriodStart(period_start)
        self._period_end = PeriodEnd(period_end)
        self._period_size = PeriodSize(period_size)

    def __call__(self):

        bucket = PeriodCollate(self._period_start.date, self._period_end.date, debit_credit_generator,
                               store_credit_debit, frequency=self._period_size.frequency,
                               interval=self._period_size.interval)

        for account in account_walker(self._income + self._expenses):
            for split in get_splits(account, self._period_start.date, self._period_end.date):
                bucket.store_value(split)

        return_value = self._generate_result()
        credit_values = []
        debit_values = []
        difference_value = []

        for key, value in bucket.container.iteritems():
            time_value = time.mktime(key.timetuple())

            # Have to switch the signs so that the graph will make sense.  In GNUCash the income accounts are debited
            # when paid, and the expense accounts are 'credited' when purchased.
            credit_values.append(dict(date=time_value, value=-value['credit']))
            debit_values.append(dict(date=time_value, value=-value['debit']))
            difference_value.append(dict(date=time_value, value=value['credit'] + value['debit']))

        # Income accounts are the debits, and Expense accounts are the credits.
        return_value['data']['expenses'] = sorted(credit_values, key=lambda s: s['date'])
        return_value['data']['income'] = sorted(debit_values, key=lambda s: s['date'])
        return_value['data']['net'] = sorted(debit_values, key=lambda s: ['date'])

        return return_value
