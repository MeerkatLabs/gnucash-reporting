"""
Gather information about the balance of the investment accounts.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.periods import PeriodStart, PeriodEnd, PeriodSize
from gnu_reporting.wrapper import get_account, get_decimal, get_session, get_balance_on_date, AccountTypes, \
    account_walker, get_splits
from gnu_reporting.collate.bucket import PeriodCollate
from gnu_reporting.collate.key_generator import period
from gnu_reporting.configuration.currency import get_currency
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
            other_account_name = split.GetCorrAccountFullName()
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
