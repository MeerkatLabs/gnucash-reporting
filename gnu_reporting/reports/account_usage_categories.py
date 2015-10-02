"""
Iterate through all of the accounts provided and give a categorized record of the expenses that have been charged to
that account.
"""
from gnu_reporting.configuration.expense_categories import get_category_for_account
from gnu_reporting.wrapper import get_decimal, account_walker, get_splits
from gnu_reporting.reports.base import Report
import time
from dateutil.relativedelta import relativedelta
from datetime import date


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

        for account in account_walker(self._accounts):
            for split in get_splits(account, start_of_trend, end_of_trend, credit=False):
                pass
