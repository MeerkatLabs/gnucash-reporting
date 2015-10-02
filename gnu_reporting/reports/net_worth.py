"""
Calculator that will go through and calculate the net worth of the accounts.
"""
from datetime import date
import time

from gnu_reporting.wrapper import account_walker, get_decimal
from gnu_reporting.configuration.currency import get_currency
from gnu_reporting.configuration.inflation import get_inflation
from gnu_reporting.reports.base import Report
from dateutils import relativedelta
from gnu_reporting.collate.bucket import MonthlyCollate
from gnu_reporting.collate.store import split_summation
from gnu_reporting.collate.bucket_generation import decimal_generator


class NetWorthCalculator(Report):
    report_type = 'net_worth'

    def __init__(self, name, asset_accounts, liability_accounts, past_months=12):
        super(NetWorthCalculator, self).__init__(name)
        self._asset_accounts = asset_accounts
        self._liability_accounts = liability_accounts
        self._past_months = past_months

    def __call__(self):
        todays_date = date.today()
        beginning_of_month = date(todays_date.year, todays_date.month, 1)

        start_of_trend = beginning_of_month - relativedelta(months=self._past_months)
        end_of_trend = beginning_of_month

        asset_bucket = MonthlyCollate(start_of_trend, end_of_trend, decimal_generator, split_summation)
        liability_bucket = MonthlyCollate(start_of_trend, end_of_trend, decimal_generator, split_summation)
        net_bucket = MonthlyCollate(start_of_trend, end_of_trend, decimal_generator, split_summation)

        currency = get_currency()

        # Calculate the asset balances
        for account in account_walker(self._asset_accounts):
            for key, value in asset_bucket.container.iteritems():
                time_key = time.mktime(key.timetuple())
                balance = account.GetBalanceAsOfDateInCurrency(time_key, currency, False)

                asset_bucket.container[key] += get_decimal(balance)

        # Calculate the liability balances
        for account in account_walker(self._liability_accounts):
            for key, value in liability_bucket.container.iteritems():
                time_key = time.mktime(key.timetuple())
                balance = account.GetBalanceAsOfDateInCurrency(time_key, currency, False)

                liability_bucket.container[key] += get_decimal(balance)

        # Now calculate the net values from the difference.
        for key, value in liability_bucket.container.iteritems():
            net_bucket.container[key] = asset_bucket.container[key] + liability_bucket.container[key]

        result = self._generate_result()
        result['data']['assets'] = sorted([dict(date=time.mktime(key.timetuple()), value=value)
                                           for key, value in asset_bucket.container.iteritems()],
                                          key=lambda s: s['date'])
        result['data']['liabilities'] = sorted([dict(date=time.mktime(key.timetuple()), value=-value)
                                                for key, value in liability_bucket.container.iteritems()],
                                               key=lambda s: s['date'])
        result['data']['net'] = sorted([dict(date=time.mktime(key.timetuple()), value=value)
                                        for key, value in net_bucket.container.iteritems()],
                                       key=lambda s: s['date'])

        inflation = get_inflation()
        starting_point = None
        inflation_data = []
        for record in result['data']['net']:
            if starting_point:
                starting_point += (starting_point*inflation)
            else:
                starting_point = record['value']

            inflation_data.append(dict(date=record['date'], value=starting_point))

        result['data']['inflation'] = inflation_data

        return result


if __name__ == '__main__':

    from gnu_reporting.wrapper import initialize
    import simplejson as json

    session = initialize('data/Accounts.gnucash')

    try:
        report = NetWorthCalculator('Net Worth',
                                    ['Assets'],
                                    ['Liabilities'])
        payload = report()
        print json.dumps(payload)
    except Exception as e:
        print 'e', e
    finally:
        session.end()


