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
from gnu_reporting.collate.bucket_generation import decimal_generator
import numpy as np


class ExpensesMonthly(Report):
    report_type = 'expenses_monthly'

    def __init__(self, name, expenses_base, ignore_list=None, past_months=12):
        super(ExpensesMonthly, self).__init__(name)
        self.expenses_base = expenses_base

        if ignore_list:
            self.ignore_list = ignore_list
        else:
            self.ignore_list = []

        self.past_months = past_months

    def __call__(self):
        todays_date = datetime.today()
        beginning_of_month = datetime(todays_date.year, todays_date.month, 1)

        start_of_trend = beginning_of_month - relativedelta(months=self.past_months)
        end_of_trend = beginning_of_month

        bucket = MonthlyCollate(start_of_trend, end_of_trend, decimal_generator, split_summation)

        for account in account_walker(self.expenses_base, self.ignore_list):
            for split in get_splits(account, start_of_trend):
                bucket.store_value(split)

        return_value = self._generate_result()
        sorted_results = []

        for key, value in bucket.container.iteritems():
            sorted_results.append(dict(date=time.mktime(key.timetuple()), value=value))

        return_value['data']['expenses'] = sorted(sorted_results, key=lambda s: s['date'])

        return return_value


class ExpensesMonthlyBox(Report):
    report_type = 'expenses_monthly_box'

    def __init__(self, name, expenses_base, ignore_list=None, past_months=12):
        super(ExpensesMonthlyBox, self).__init__(name)
        self.expenses_base = expenses_base

        if ignore_list:
            self.ignore_list = ignore_list
        else:
            self.ignore_list = []

        self.past_months = past_months

    def __call__(self):
        todays_date = datetime.today()
        beginning_of_month = datetime(todays_date.year, todays_date.month, 1)

        start_of_trend = beginning_of_month - relativedelta(months=self.past_months)
        end_of_trend = beginning_of_month

        bucket = MonthlyCollate(start_of_trend, end_of_trend, decimal_generator, split_summation)

        for account in account_walker(self.expenses_base, self.ignore_list):
            for split in get_splits(account, start_of_trend):
                bucket.store_value(split)

        return_value = self._generate_result()
        results = []

        for key, value in bucket.container.iteritems():
            results.append(float(value))

        return_value['data']['low'] = np.percentile(results, 0)
        return_value['data']['high'] = np.percentile(results, 100)
        return_value['data']['q1'] = np.percentile(results, 25)
        return_value['data']['q2'] = np.percentile(results, 50)
        return_value['data']['q3'] = np.percentile(results, 75)

        return return_value

if __name__ == '__main__':

    import simplejson as json
    from gnu_reporting.wrapper import initialize

    session = initialize('data/Accounts.gnucash')

    try:
        report = ExpensesMonthlyBox('expenses', ['Expenses'], ['Expenses.Taxes',
                                                               'Expenses.Seaside View',
                                                               'Expenses.ISSACCorp',
                                                               'Expenses.DQI'], past_months=12)

        result = report()

        print json.dumps(result)
    finally:
        session.end()



