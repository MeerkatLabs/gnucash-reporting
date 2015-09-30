"""
Cash flow report for an account and it's children.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_splits, account_walker
from datetime import datetime
from dateutil.relativedelta import relativedelta
from gnu_reporting.collate.bucket_generation import debit_credit_generator
from gnu_reporting.collate.store import store_credit_debit
from gnu_reporting.collate.bucket import MonthlyCollate
import time


class MonthlyCashFlow(Report):
    report_type = 'monthly_cash_flow_chart'

    def __init__(self, name, accounts, past_months=12):
        super(MonthlyCashFlow, self).__init__(name)
        self._account_names = accounts
        self.past_months = past_months

    def __call__(self):

        todays_date = datetime.today()
        beginning_of_month = datetime(todays_date.year, todays_date.month, 1)

        start_of_trend = beginning_of_month - relativedelta(months=self.past_months)
        end_of_trend = beginning_of_month

        bucket = MonthlyCollate(start_of_trend, end_of_trend, debit_credit_generator, store_credit_debit)

        for account in account_walker(self._account_names):

            for split in get_splits(account, start_of_trend, end_of_trend):
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

    report = MonthlyCashFlow('expenses', ['Assets.Seaside View Rental'], past_months=12)

    result = report()

    print json.dumps(result)

    session.end()
