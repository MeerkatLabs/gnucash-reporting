"""
Gathers up all of the expenses and breaks down the values by month.
"""
from datetime import datetime
import time

from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_splits, account_walker
from gnu_reporting.periods import PeriodStart, PeriodEnd, PeriodSize
from dateutil.relativedelta import relativedelta
from gnu_reporting.collate.bucket import PeriodCollate, CategoryCollate
from gnu_reporting.collate.store import split_summation, count
from gnu_reporting.collate.bucket_generation import decimal_generator, integer_generator
from operator import itemgetter
import numpy as np


class ExpensesMonthly(Report):
    report_type = 'expenses_period'

    def __init__(self, name, expenses_base, ignore_list=None, period_start=PeriodStart.this_month_year_ago.value,
                 period_end=PeriodEnd.this_month.value, period_size=PeriodSize.month.value, show_record_count=False):
        super(ExpensesMonthly, self).__init__(name)
        self.expenses_base = expenses_base

        if ignore_list:
            self.ignore_list = ignore_list
        else:
            self.ignore_list = []

        self._start = PeriodStart(period_start)
        self._end = PeriodEnd(period_end)
        self._size = PeriodSize(period_size)
        self._show_record_count = show_record_count

    def __call__(self):

        bucket = PeriodCollate(self._start.date, self._end.date, decimal_generator, split_summation,
                               frequency=self._size.frequency, interval=self._size.interval)
        record_count = PeriodCollate(self._start.date, self._end.date, integer_generator, count,
                                     frequency=self._size.frequency, interval=self._size.interval)

        for account in account_walker(self.expenses_base, self.ignore_list):
            for split in get_splits(account, self._start.date, self._end.date):
                bucket.store_value(split)
                record_count.store_value(split)

        return_value = self._generate_result()
        sorted_results = []
        sorted_count_results = []

        for key, value in bucket.container.iteritems():
            sorted_results.append(dict(date=time.mktime(key.timetuple()), value=value))

        for key, value in record_count.container.iteritems():
            sorted_count_results.append(dict(date=time.mktime(key.timetuple()), value=value))

        return_value['data']['expenses'] = sorted(sorted_results, key=lambda s: s['date'])

        if self._show_record_count:
            return_value['data']['count'] = sorted(sorted_count_results, key=lambda s: s['date'])

        return return_value


class ExpensesMonthlyBox(Report):
    report_type = 'expenses_box'

    def __init__(self, name, expenses_base, ignore_list=None, period_start=PeriodStart.this_month_year_ago,
                 period_end=PeriodEnd.this_month, period_size=PeriodSize.month):
        super(ExpensesMonthlyBox, self).__init__(name)
        self.expenses_base = expenses_base

        if ignore_list:
            self.ignore_list = ignore_list
        else:
            self.ignore_list = []

        self._start = PeriodStart(period_start)
        self._end = PeriodEnd(period_end)
        self._size = PeriodSize(period_size)

    def __call__(self):

        bucket = PeriodCollate(self._start.date, self._end.date, decimal_generator, split_summation,
                               frequency=self._size.frequency, interval=self._size.interval)

        for account in account_walker(self.expenses_base, self.ignore_list):
            for split in get_splits(account, self._start.date, self._end.date):
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


class ExpenseCategories(Report):
    report_type = 'expenses_categories'

    def __init__(self, name, expenses_base, ignore_list=None, period_start=PeriodStart.this_year.value,
                 period_end=PeriodEnd.this_year.value):
        super(ExpenseCategories, self).__init__(name)
        self.expenses_base = expenses_base

        if ignore_list:
            self.ignore_list = ignore_list
        else:
            self.ignore_list = []

        self._start = PeriodStart(period_start)
        self._end = PeriodEnd(period_end)

    def __call__(self):
        bucket = CategoryCollate(decimal_generator, split_summation)

        for account in account_walker(self.expenses_base, self.ignore_list):
            for split in get_splits(account, self._start.date, self._end.date):
                bucket.store_value(split)

        return_value = self._generate_result()

        return_value['data']['categories'] = sorted([[key, value] for key, value in bucket.container.iteritems()],
                                                    key=itemgetter(0))

        return return_value

if __name__ == '__main__':

    import simplejson as json
    from gnu_reporting.wrapper import initialize

    session = initialize('data/Accounts.gnucash')

    try:
        report = ExpensesMonthlyBox('expenses', ['Expenses'], ['Expenses.Taxes',
                                                               'Expenses.Seaside View',
                                                               'Expenses.ISSACCorp',
                                                               'Expenses.DQI'])

        result = report()

        print json.dumps(result)
    finally:
        session.end()



