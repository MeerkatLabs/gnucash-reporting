"""
Iterate through all of the accounts provided and give a categorized record of the expenses that have been charged to
that account.
"""
from decimal import Decimal
from operator import itemgetter

from gnucash_reports.configuration.expense_categories import get_category_for_account
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.reports.base import Report
from gnucash_reports.wrapper import account_walker, get_splits


class AccountUsageCategories(Report):
    report_type = 'account_usage_categories'

    def __init__(self, name, account_list, period_start=PeriodStart.this_month, period_end=PeriodEnd.this_month):
        super(AccountUsageCategories, self).__init__(name)
        self._accounts = account_list
        self._start = PeriodStart(period_start)
        self._end = PeriodEnd(period_end)

    def __call__(self):

        start_of_trend = self._start.date
        end_of_trend = self._end.date

        data = dict()

        for account in account_walker(self._accounts):
            for split in get_splits(account, start_of_trend, end_of_trend, credit=False):

                transaction = split.transaction

                for transaction_split in transaction.splits:
                    transaction_account_name = transaction_split.account.fullname
                    if transaction_account_name != account.fullname:
                        category = get_category_for_account(transaction_account_name)
                        current_balance = data.setdefault(category,
                                                          Decimal('0.0'))
                        current_balance += transaction_split.value
                        data[category] = current_balance

        result = self._generate_result()
        result['data']['categories'] = sorted([[key, value] for key, value in data.iteritems()], key=itemgetter(0))

        return result


if __name__ == '__main__':
    from gnucash_reports.wrapper import initialize

    session = initialize('data/Accounts.gnucash')

    report = AccountUsageCategories('asdf',
                                    ['Assets.Current Assets.Joint.Ent.Checking - 10'],
                                    1)
    try:
        payload = report()
        print payload
    finally:
        session.end()

