"""
Iterate through all of the accounts provided and give a categorized record of the expenses that have been charged to
that account.
"""
from gnu_reporting.configuration.expense_categories import get_category_for_account
from gnu_reporting.wrapper import get_decimal, account_walker, get_splits
from gnu_reporting.reports.base import Report
from dateutil.relativedelta import relativedelta
from datetime import date
from decimal import Decimal
from operator import itemgetter


class AccountUsageCategories(Report):
    report_type = 'account_usage_categories'

    def __init__(self, name, account_list, past_months=0):
        super(AccountUsageCategories, self).__init__(name)
        self._accounts = account_list
        self._past_months = past_months

    def __call__(self):

        today = date.today()
        beginning_of_month = date(today.year, today.month, 1)
        start_of_trend = beginning_of_month - relativedelta(months=self._past_months)
        end_of_trend = beginning_of_month - relativedelta(months=self._past_months-1)

        data = dict()

        for account in account_walker(self._accounts):
            for split in get_splits(account, start_of_trend, end_of_trend, credit=False):

                transaction = split.parent

                for transaction_split in transaction.GetSplitList():
                    transaction_account_name = transaction_split.GetAccount().get_full_name()
                    if transaction_account_name != account.get_full_name():
                        category = get_category_for_account(transaction_account_name)
                        current_balance = data.setdefault(category,
                                                          Decimal('0.0'))
                        current_balance += get_decimal(transaction_split.GetAmount())
                        data[category] = current_balance

        result = self._generate_result()
        result['data']['categories'] = sorted([[key, value] for key, value in data.iteritems()], key=itemgetter(1))

        return result

if __name__ == '__main__':
    from gnu_reporting.wrapper import initialize

    session = initialize('data/Accounts.gnucash')

    report = AccountUsageCategories('asdf',
                                    ['Assets.Current Assets.Joint.Ent.Checking - 10'],
                                    1)
    try:
        payload = report()
        print payload
    finally:
        session.end()

