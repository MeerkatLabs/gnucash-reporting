"""
Gather information about the balance of the investment accounts.
"""
from gnucash_reports.reports.base import Report
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.wrapper import get_account, get_session, get_balance_on_date, AccountTypes, \
    account_walker, get_splits, get_corr_account_full_name
from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.configuration.investment_allocations import get_asset_allocation
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

        for split in account.splits:
            other_account_name = get_corr_account_full_name(split)
            other_account = get_account(other_account_name)

            account_type = AccountTypes(other_account.type.upper())
            date = split.transaction.post_date

            # Store previous data
            if len(purchases):
                previous_date = date - relativedelta(days=1)
                previous_date_key = time.mktime(previous_date.timetuple())
                purchases[previous_date_key] = last_purchase
                dividends[previous_date_key] = last_dividend
                values[previous_date_key] = get_balance_on_date(account, previous_date, currency)

            # Find the correct amount that was paid from the account into this account.
            change_amount = split.value

            if change_amount > 0:
                # Need to get the value from the corr account split.
                for parent_splits in split.transaction.splits:
                    if parent_splits.account.fullname == other_account_name:
                        change_amount = -parent_splits.value

            if account_type == AccountTypes.mutual_fund or account_type == AccountTypes.asset:
                # Asset or mutual fund transfer
                last_purchase += change_amount
            else:
                last_dividend += split.value

            key = time.mktime(date.timetuple())
            purchases[key] = last_purchase
            dividends[key] = last_dividend
            values[key] = get_balance_on_date(account, date, currency)

        # Now get all of the price updates in the database.
        price_database = get_session().get_book().get_price_db()
        commodity = account.commodity
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

    account_type = AccountTypes(other_account.type.upper())

    # Find the correct amount that was paid from the account into this account.
    change_amount = value.value

    if change_amount > 0:
        # Need to get the value from the corr account split.
        for parent_splits in value.parent.splits:
            if parent_splits.account.fullname == other_account_name:
                change_amount = -parent_splits.value

    if account_type == AccountTypes.mutual_fund or account_type == AccountTypes.asset or \
       account_type == AccountTypes.equity:
        # Asset or mutual fund transfer
        bucket['money_in'] += change_amount
    elif account_type == AccountTypes.income:
        bucket['income'] += value.value
    elif account_type == AccountTypes.expense:
        bucket['expense'] += value.value
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

    def __init__(self, name, investment_accounts, ignore_accounts=None, category_mapping=None):
        super(InvestmentAllocation, self).__init__(name)
        self._investment_accounts = investment_accounts
        if ignore_accounts:
            self._ignore_accounts = ignore_accounts
        else:
            self._ignore_accounts = []

        if category_mapping:
            self._category_mapping = category_mapping
        else:
            self._category_mapping = dict()

    def __call__(self):
        breakdown = dict()
        today = datetime.today()
        currency = get_currency()

        for account in account_walker(self._investment_accounts, self._ignore_accounts):
            balance = get_balance_on_date(account, today, currency)
            commodity = account.commodity.mnemonic

            results = get_asset_allocation(commodity, balance)

            for key, value in results.iteritems():
                breakdown[key] = breakdown.get(key, Decimal('0.0')) + value

        return_value = self._generate_result()
        return_value['data']['categories'] = sorted([[self._category_mapping.get(key, key), value]
                                                     for key, value in breakdown.iteritems()],
                                                    key=itemgetter(0))

        return return_value


if __name__ == '__main__':

    from gnucash_reports.wrapper import initialize
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
