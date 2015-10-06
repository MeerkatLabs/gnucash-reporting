"""
Gather information about the balance of the investment accounts.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_account, get_decimal, get_session, get_balance_on_date, AccountTypes
from gnu_reporting.configuration.currency import get_currency
from decimal import Decimal
from operator import itemgetter
import time
from datetime import datetime


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

        for split in account.GetSplitList():
            other_account_name = split.GetCorrAccountFullName()
            other_account = get_account(other_account_name)

            account_type = AccountTypes(other_account.GetType())
            date = datetime.fromtimestamp(split.parent.GetDate())

            if account_type == AccountTypes.mutual_fund or account_type == AccountTypes.asset:
                # Asset or mutual fund transfer
                last_purchase += get_decimal(split.GetValue())
            else:
                last_dividend += get_decimal(split.GetValue())

            key = time.mktime(date.timetuple())
            data['purchases'].append((key, last_purchase))
            data['dividend'].append((key, last_dividend))
            data['value'].append((key, get_balance_on_date(account, date, currency)))

        # Now get all of the price updates in the database.
        price_database = get_session().get_book().get_price_db()
        commodity = account.GetCommodity()
        for price in price_database.get_prices(commodity, None):
            date = time.mktime(price.get_time().timetuple())
            data['value'].append((date, get_balance_on_date(account, price.get_time(), currency)))

        data['value'] = sorted(data['value'], key=itemgetter(0))

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
        report = InvestmentBalance('Estimated Taxes', 'Assets.Investments.Vanguard.Brokerage Account.Mutual Funds.Tax-Managed Capital Appreciation Admiral Shares')
        payload = report()
        print json.dumps(payload)
    finally:
        session.end()
