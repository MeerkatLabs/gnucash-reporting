"""
Gather information about the balance of the investment accounts.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.periods import PeriodStart, PeriodEnd, PeriodSize
from gnu_reporting.wrapper import get_account, get_decimal, get_session, get_balance_on_date, AccountTypes, \
    account_walker, get_splits, get_corr_account_full_name
from gnu_reporting.collate.bucket import PeriodCollate
from gnu_reporting.configuration.currency import get_currency
from gnu_reporting.configuration.investment_allocations import get_asset_allocation
from decimal import Decimal
from operator import itemgetter
import time
from datetime import datetime
from dateutils import relativedelta


class InvestmentBalance(Report):
    report_type = 'investment_balance'

    def __init__(self, name, account):
        super(InvestmentBalance, self).__init__(name)
        self.account_name = account

    def __call__(self):
        account = get_account(self.account_name)

        data = dict(purchases=[], dividend=[], value=[])

        last_dividend = Decimal('0.0')
        last_purchase = Decimal('0.0')

        currency = get_currency()

        purchases = dict()
        dividends = dict()
        values = dict()

        for split in account.GetSplitList():
            other_account_name = get_corr_account_full_name(split)
            other_account = get_account(other_account_name)

            account_type = AccountTypes(other_account.GetType())
            date = datetime.fromtimestamp(split.parent.GetDate())

            # Store previous data
            if len(purchases):
                previous_date = date - relativedelta(days=1)
                previous_date_key = time.mktime(previous_date.timetuple())
                purchases[previous_date_key] = last_purchase
                dividends[previous_date_key] = last_dividend
                values[previous_date_key] = get_balance_on_date(account, previous_date, currency)

            # Find the correct amount that was paid from the account into this account.
            change_amount = get_decimal(split.GetValue())

            if change_amount > 0:
                # Need to get the value from the corr account split.
                for parent_splits in split.parent.GetSplitList():
                    if parent_splits.GetAccount().get_full_name() == other_account_name:
                        change_amount = -get_decimal(parent_splits.GetValue())

            if account_type == AccountTypes.mutual_fund or account_type == AccountTypes.asset:
                # Asset or mutual fund transfer
                last_purchase += change_amount
            else:
                last_dividend += get_decimal(split.GetValue())

            key = time.mktime(date.timetuple())
            purchases[key] = last_purchase
            dividends[key] = last_dividend
            values[key] = get_balance_on_date(account, date, currency)

        # Now get all of the price updates in the database.
        price_database = get_session().get_book().get_price_db()
        commodity = account.GetCommodity()
        for price in price_database.get_prices(commodity, None):
            date = time.mktime(price.get_time().timetuple())

            values[date] = max(values.get(date, Decimal('0.0')),
                               get_balance_on_date(account, price.get_time(), currency))

        data['purchases'] = sorted([(key, value) for key, value in purchases.iteritems()], key=itemgetter(0))
        data['dividend'] = sorted([(key, value) for key, value in dividends.iteritems()], key=itemgetter(0))
        data['value'] = sorted([(key, value) for key, value in values.iteritems()], key=itemgetter(0))

        results = self._generate_result()
        results['data'] = data

        return results


def investment_bucket_generator():
    return dict(money_in=Decimal('0.0'), income=Decimal('0.0'), expense=Decimal('0.0'))


def store_investment(bucket, value):
    other_account_name = get_corr_account_full_name(value)
    other_account = get_account(other_account_name)

    account_type = AccountTypes(other_account.GetType())

    # Find the correct amount that was paid from the account into this account.
    change_amount = get_decimal(value.GetValue())

    if change_amount > 0:
        # Need to get the value from the corr account split.
        for parent_splits in value.parent.GetSplitList():
            if parent_splits.GetAccount().get_full_name() == other_account_name:
                change_amount = -get_decimal(parent_splits.GetValue())

    if account_type == AccountTypes.mutual_fund or account_type == AccountTypes.asset or \
       account_type == AccountTypes.equity:
        # Asset or mutual fund transfer
        bucket['money_in'] += change_amount
    elif account_type == AccountTypes.income:
        bucket['income'] += get_decimal(value.GetValue())
    elif account_type == AccountTypes.expense:
        bucket['expense'] += get_decimal(value.GetValue())
    else:
        print 'Unknown account type: %s' % account_type

    return bucket


class InvestmentTrend(Report):
    report_type = 'investment_trend'

    def __init__(self, name, investment_accounts, ignore_accounts=None,
                 period_start=PeriodStart.this_month_year_ago,
                 period_end=PeriodEnd.this_month, period_size=PeriodSize.month):
        super(InvestmentTrend, self).__init__(name)
        self._investment_accounts = investment_accounts
        if ignore_accounts:
            self._ignore_accounts = ignore_accounts
        else:
            self._ignore_accounts = []

        self._period_start = PeriodStart(period_start)
        self._period_end = PeriodEnd(period_end)
        self._period_size = PeriodSize(period_size)

    def __call__(self):

        investment_value = dict()
        buckets = PeriodCollate(self._period_start.date, self._period_end.date,
                                investment_bucket_generator, store_investment, frequency=self._period_size.frequency,
                                interval=self._period_size.interval)

        start_value = Decimal('0.0')
        start_value_date = self._period_start.date - relativedelta(days=1)
        currency = get_currency()

        for account in account_walker(self._investment_accounts, ignore_list=self._ignore_accounts):
            for split in get_splits(account, self._period_start.date, self._period_end.date):
                buckets.store_value(split)

            start_value += get_balance_on_date(account, start_value_date, currency)

            for key in buckets.container.keys():
                date_value = key + relativedelta(months=1) - relativedelta(days=1)
                investment_value[key] = investment_value.get(key, Decimal('0.0')) + get_balance_on_date(account,
                                                                                                        date_value,
                                                                                                        currency)

        results = self._generate_result()
        results['data']['start_value'] = start_value

        results['data']['income'] = sorted(
            [(time.mktime(key.timetuple()), value['income']) for key, value in buckets.container.iteritems()],
            key=itemgetter(0))

        results['data']['money_in'] = sorted(
            [(time.mktime(key.timetuple()), value['money_in']) for key, value in buckets.container.iteritems()],
            key=itemgetter(0))

        results['data']['expense'] = sorted(
            [(time.mktime(key.timetuple()), value['expense']) for key, value in buckets.container.iteritems()],
            key=itemgetter(0))

        results['data']['value'] = sorted(
            [[time.mktime(key.timetuple()), value] for key, value in investment_value.iteritems()],
        )

        results['data']['basis'] = sorted(
            [[time.mktime(key.timetuple()), Decimal('0.0')] for key in buckets.container.keys()],
            key=itemgetter(0)
        )

        monthly_start = start_value
        for index, record in enumerate(results['data']['basis']):
            record[1] += (monthly_start + results['data']['income'][index][1] + results['data']['money_in'][index][1] +
                          results['data']['expense'][index][1])
            monthly_start = record[1]

        return results


class InvestmentAllocation(Report):
    report_type = 'investment_allocation'

    def __init__(self, name, investment_accounts, ignore_accounts=None):
        super(InvestmentAllocation, self).__init__(name)
        self._investment_accounts = investment_accounts
        if ignore_accounts:
            self._ignore_accounts = ignore_accounts
        else:
            self._ignore_accounts = []

    def __call__(self):
        breakdown = dict()
        today = datetime.today()
        currency = get_currency()

        for account in account_walker(self._investment_accounts, self._ignore_accounts):
            balance = get_balance_on_date(account, today, currency)
            commodity = account.GetCommodity().get_nice_symbol()

            results = get_asset_allocation(commodity, balance)

            for key, value in results.iteritems():
                breakdown[key] = breakdown.get(key, Decimal('0.0')) + value

        return_value = self._generate_result()
        return_value['data']['categories'] = sorted([[key, value] for key, value in breakdown.iteritems()],
                                                    key=itemgetter(0))

        return return_value


if __name__ == '__main__':

    from gnu_reporting.wrapper import initialize
    from decimal import Decimal
    import simplejson as json

    session = initialize('data/Accounts.gnucash')
    goal_amount = Decimal('500.00')
    try:
        report = InvestmentBalance('Estimated Taxes',
                                   'Assets.Investments.Vanguard.Brokerage Account.Mutual Funds.Tax-Managed Capital Appreciation Admiral Shares')
        payload = report()
        print json.dumps(payload)
    finally:
        session.end()
