"""
Gathers up all of the expenses and breaks down the values by month.
"""
from datetime import datetime
import time

from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_splits, account_walker
from dateutil.relativedelta import relativedelta
from gnu_reporting.collate.bucket import MonthlyCollate
from gnu_reporting.collate.store import split_summation


class ExpensesMonthly(Report):
    report_type = 'expenses_monthly'

    def __init__(self, name, expenses_base, ignore_list, past_months=12):
        super(ExpensesMonthly, self).__init__(name)
        self.expenses_base = expenses_base
        self.ignore_list = ignore_list
        self.past_months = past_months

    def __call__(self):
        remaining_accounts = [a for a in self.expenses_base]

        todays_date = datetime.today()
        beginning_of_month = datetime(todays_date.year, todays_date.month, 1)

        start_of_trend = beginning_of_month - relativedelta(months=self.past_months)
        end_of_trend = beginning_of_month

        bucket = MonthlyCollate(start_of_trend, end_of_trend, split_summation)

        for account in account_walker(remaining_accounts, self.ignore_list):
            for split in get_splits(account, start_of_trend):
                bucket.store_value(split)

        return_value = self._generate_result()
        sorted_results = []

        for key, value in bucket.container.iteritems():
            sorted_results.append(dict(date=time.mktime(key.timetuple()), value=value))

        return_value['data']['expenses'] = sorted(sorted_results, key=lambda s: s['date'])

        return return_value

if __name__ == '__main__':

    import simplejson as json
    from gnu_reporting.wrapper import initialize

    session = initialize('data/Accounts.gnucash')

    report = ExpensesMonthly('expenses', ['Expenses'], ['Expenses.Taxes',
                                                        'Expenses.Seaside View',
                                                        'Expenses.ISSACCorp',
                                                        'Expenses.DQI'], past_months=12)

    result = report()

    print json.dumps(result)

    session.end()



