"""
Cash flow report for an account and it's children.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_splits, account_walker
from gnu_reporting.periods import PeriodStart, PeriodEnd, PeriodSize
from gnu_reporting.collate.bucket_generation import debit_credit_generator
from gnu_reporting.collate.store import store_credit_debit
from gnu_reporting.collate.bucket import PeriodCollate
import time


class MonthlyCashFlow(Report):
    report_type = 'cash_flow_chart'

    def __init__(self, name, accounts, period_start=PeriodStart.this_month_year_ago,
                 period_end=PeriodEnd.this_month, period_size=PeriodSize.month):
        super(MonthlyCashFlow, self).__init__(name)
        self._account_names = accounts

        self._start = PeriodStart(period_start)
        self._end = PeriodEnd(period_end)
        self._size = PeriodSize(period_size)

    def __call__(self):

        bucket = PeriodCollate(self._start.date, self._end.date, debit_credit_generator,
                               store_credit_debit, frequency=self._size.frequency, interval=self._size.interval)

        for account in account_walker(self._account_names):
            for split in get_splits(account, self._start.date, self._end.date):
                bucket.store_value(split)

        return_value = self._generate_result()
        credit_values = []
        debit_values = []
        difference_value = []

        for key, value in bucket.container.iteritems():
            credit_values.append(dict(date=time.mktime(key.timetuple()), value=value['credit']))
            debit_values.append(dict(date=time.mktime(key.timetuple()), value=value['debit']))
            difference_value.append(dict(date=time.mktime(key.timetuple()), value=value['credit'] + value['debit']))

        return_value['data']['credits'] = sorted(credit_values, key=lambda s: s['date'])
        return_value['data']['debits'] = sorted(debit_values, key=lambda s: s['date'])
        return_value['data']['gross'] = sorted(debit_values, key=lambda s: ['date'])

        return return_value


if __name__ == '__main__':
    import simplejson as json
    from gnu_reporting.wrapper import initialize

    session = initialize('data/Accounts.gnucash')

    try:
        report = MonthlyCashFlow('expenses', ['Assets.Seaside View Rental'], period_size=PeriodSize.two_week.value)

        result = report()

        print json.dumps(result)
    finally:
        session.end()
