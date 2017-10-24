"""
Collection of reports that will warn when the level of an account gets to be low.
"""
from gnucash_reports.periods import PeriodStart
from gnucash_reports.reports.base import Report
from gnucash_reports.wrapper import get_account, get_balance_on_date


class AccountLevels(Report):
    report_type = 'account_levels'

    def __init__(self, name, account, good_value, warn_value, error_value, when=PeriodStart.today):
        super(AccountLevels, self).__init__(name)
        self.account = account
        self.good_value = good_value
        self.warn_value = warn_value
        self.error_value = error_value
        self.when = PeriodStart(when)

    def __call__(self):
        account = get_account(self.account)

        balance = get_balance_on_date(account, self.when.date)

        payload = self._generate_result()
        payload['data']['balance'] = balance
        payload['data']['good_value'] = self.good_value
        payload['data']['warn_value'] = self.warn_value
        payload['data']['error_value'] = self.error_value

        return payload
