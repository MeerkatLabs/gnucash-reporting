"""
Collection of reports that will warn when the level of an account gets to be low.
"""
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_account, get_decimal
from datetime import date
import time


class AccountLevels(Report):
    report_type = 'account_levels'

    def __init__(self, name, account, good_value, warn_value, error_value):
        super(AccountLevels, self).__init__(name)
        self.account = account
        self.good_value = good_value
        self.warn_value = warn_value
        self.error_value = error_value

    def __call__(self):
        account = get_account(self.account)
        today = date.today()
        today_time = time.mktime(today.timetuple())

        balance = account.GetBalanceAsOfDate(today_time)

        payload = self._generate_result()
        payload['data']['balance'] = get_decimal(balance)
        payload['data']['good_value'] = self.good_value
        payload['data']['warn_value'] = self.warn_value
        payload['data']['error_value'] = self.error_value

        return payload
