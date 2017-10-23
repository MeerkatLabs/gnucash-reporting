"""
Calculator that will go through and calculate the net worth of the accounts.
"""
from datetime import date
import time

from gnucash_reports.wrapper import account_walker, get_decimal, get_balance_on_date
from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.configuration.inflation import get_monthly_inflation
from gnucash_reports.reports.base import Report
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from dateutils import relativedelta
from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.collate.store import split_summation
from gnucash_reports.collate.bucket_generation import decimal_generator
from calendar import monthrange
from decimal import Decimal


class NetWorthCalculator(Report):
    report_type = 'net_worth'

    def __init__(self, name, asset_accounts, liability_accounts, period_start=PeriodStart.this_month_year_ago,
                 period_end=PeriodEnd.today, period_size=PeriodSize.month):
        super(NetWorthCalculator, self).__init__(name)
        self._asset_accounts = asset_accounts
        self._liability_accounts = liability_accounts

        self._period_start = PeriodStart(period_start)
        self._period_end = PeriodEnd(period_end)
        self._period_size = PeriodSize(period_size)

    def __call__(self):

        start_of_trend = self._period_start.date
        end_of_trend = self._period_end.date

        asset_bucket = PeriodCollate(start_of_trend, end_of_trend, decimal_generator, split_summation,
                                     frequency=self._period_size.frequency, interval=self._period_size.interval)
        liability_bucket = PeriodCollate(start_of_trend, end_of_trend, decimal_generator, split_summation,
                                         frequency=self._period_size.frequency, interval=self._period_size.interval)
        net_bucket = PeriodCollate(start_of_trend, end_of_trend, decimal_generator, split_summation,
                                   frequency=self._period_size.frequency, interval=self._period_size.interval)

        currency = get_currency()

        # Calculate the asset balances
        for account in account_walker(self._asset_accounts):
            for key, value in asset_bucket.container.iteritems():
                balance = get_balance_on_date(account, key, currency)
                asset_bucket.container[key] += balance

        # Calculate the liability balances
        for account in account_walker(self._liability_accounts):
            for key, value in liability_bucket.container.iteritems():
                balance = get_balance_on_date(account, key, currency)
                liability_bucket.container[key] += balance

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

        inflation = get_monthly_inflation()
        starting_point = None
        inflation_data = []
        for record in result['data']['net']:
            if starting_point:
                starting_point += (starting_point * inflation)
            else:
                starting_point = record['value']

            inflation_data.append(dict(date=record['date'], value=starting_point))

        result['data']['inflation'] = inflation_data

        return result


class NetWorthTable(Report):
    """
    Gathers up the values of the accounts at the end of the specified months in order to show net asset values.
    """
    report_type = 'net_worth_table'

    def __init__(self, name, asset_definitions, liability_definitions, trends=None, deltas=None):
        super(NetWorthTable, self).__init__(name)
        self._asset_definitions = asset_definitions
        self._liability_definitions = liability_definitions
        if trends:
            self._trends = trends
        else:
            self._trends = [-2, -1]

        if deltas:
            self._deltas = deltas
        else:
            self._deltas = [-1, -12]

    def __call__(self):
        today = date.today()

        trend_months = []
        for month_delta in self._trends:
            relative = today + relativedelta(months=month_delta)
            new_date = date(relative.year, relative.month, monthrange(relative.year, relative.month)[1])
            trend_months.append(new_date)

        delta_months = []
        for month_delta in self._deltas:
            relative = today + relativedelta(months=month_delta)
            new_date = date(relative.year, relative.month, monthrange(relative.year, relative.month)[1])
            delta_months.append(new_date)

        total_asset_data = self._calculate_payload(self._asset_definitions, delta_months, trend_months)
        total_liability_data = self._calculate_payload(self._liability_definitions, delta_months, trend_months,
                                                       liability=True)

        # Now to calculate the values for the net worth display
        net_worth_data = dict(current_data=total_asset_data['current_data'] + total_liability_data['current_data'],
                              deltas=[], trend=[])
        for index, trend in enumerate(trend_months):
            assets = total_asset_data['trend'][index]
            expenses = total_liability_data['trend'][index]
            net_worth_data['trend'].append(assets + expenses)

        for index, delta in enumerate(delta_months):
            assets = total_asset_data['delta_sub_total'][index]
            liability = total_liability_data['delta_sub_total'][index]
            net_value = assets + liability

            try:
                result = (net_worth_data['current_data'] - net_value) / net_value
                net_worth_data['deltas'].append(result)
            except:
                net_worth_data['deltas'].append('N/A')


        results = self._generate_result()
        results['data']['trend'] = [time.mktime(t.timetuple()) for t in trend_months]
        results['data']['deltas'] = self._deltas
        results['data']['assets'] = total_asset_data
        results['data']['liability'] = total_liability_data
        results['data']['net_worth'] = net_worth_data

        return results

    def _calculate_payload(self, account_list, delta_months, trend_months, liability=False):
        currency = get_currency()
        today = date.today()
        end_of_month = date(today.year, today.month, monthrange(today.year, today.month)[1])
        total_data = dict(records=[], current_data=Decimal('0.0'),
                          deltas=[Decimal('0.0') for a in delta_months],
                          delta_sub_total=[Decimal('0.0') for a in delta_months],
                          trend=[Decimal('0.0') for a in trend_months])

        for definition in account_list:
            definition_data = dict(name=definition['name'],
                                   current_data=Decimal('0.0'),
                                   deltas=[Decimal('0.0') for a in delta_months],
                                   trend=[Decimal('0.0') for a in trend_months])

            # Get Current Data first
            for account in account_walker(definition['accounts']):
                balance = get_balance_on_date(account, end_of_month, currency)
                definition_data['current_data'] += balance
                total_data['current_data'] += balance

            # Calculate the trends
            for index, trend in enumerate(trend_months):
                for account in account_walker(definition['accounts']):
                    balance = get_balance_on_date(account, trend, currency)
                    definition_data['trend'][index] += balance
                    total_data['trend'][index] += balance

            # Calculate deltas
            for index, delta in enumerate(delta_months):
                value = Decimal(0.0)
                for account in account_walker(definition['accounts']):
                    balance = get_balance_on_date(account, delta, currency)
                    value += balance
                    total_data['delta_sub_total'][index] += balance

                try:
                    definition_data['deltas'][index] = (definition_data['current_data'] - value) / value
                    if liability:
                        definition_data['deltas'][index] = -definition_data['deltas'][index]
                except:
                    definition_data['deltas'][index] = 'N/A'

            total_data['records'].append(definition_data)

        # Calculate the deltas for the total values.
        for index, value in enumerate(total_data['delta_sub_total']):
            try:
                total_data['deltas'][index] = (total_data['current_data'] - value) / value
                if liability:
                    total_data['deltas'][index] = -total_data['deltas'][index]
            except:
                definition_data['deltas'][index] = 'N/A'

        return total_data


if __name__ == '__main__':

    from gnucash_reports.wrapper import initialize
    import simplejson as json

    session = initialize('data/Accounts.gnucash')

    try:
        report = NetWorthTable('Net Worth',
                               [dict(name='Assets', accounts=['Assets'])],
                               [dict(name='Liabilities', accounts=['Liabilities'])])
        payload = report()
        print json.dumps(payload)
    except Exception as e:
        print 'e', e
    finally:
        session.end()
