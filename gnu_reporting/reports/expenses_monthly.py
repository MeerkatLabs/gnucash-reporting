"""
Gathers up all of the expenses and breaks down the values by month.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_account, get_decimal, get_splits
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from decimal import Decimal
import time


class ExpensesMonthly(Report):
    report_type = 'expenses_monthly'

    def __init__(self, name, expenses_base, ignore_list, past_months=12):
        super(ExpensesMonthly, self).__init__(name)
        self.expenses_base = expenses_base
        self.ignore_list = ignore_list
        self.past_months = past_months

    def __call__(self):
        results = dict()
        remaining_accounts = [a for a in self.expenses_base]

        todays_date = datetime.today()
        beginning_of_month = datetime(todays_date.year, todays_date.month, 1)

        start_of_trend = beginning_of_month - relativedelta(months=self.past_months)
        end_of_trend = beginning_of_month

        for dt in rrule(MONTHLY, dtstart=start_of_trend, until=end_of_trend):
            results[date(dt.year, dt.month, 1)] = Decimal('0.0')

        while remaining_accounts:
            account_name = remaining_accounts.pop()
            print 'Processing account: %s' % account_name

            if account_name in self.ignore_list:
                continue

            account = get_account(account_name)

            if not account.GetPlaceholder():

                for split in get_splits(account, start_of_trend):
                    split_date = datetime.fromtimestamp(split.parent.GetDate())
                    key = date(split_date.year, split_date.month, 1)

                    results[key] += get_decimal(split.GetAmount())

            remaining_accounts += [a.get_full_name() for a in account.get_children()]

        return_value = self._generate_result()
        return_value['data']['expenses'] = []

        for key, value in results.iteritems():
            return_value['data']['expenses'].append(dict(date=time.mktime(key.timetuple()), value=value))

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



