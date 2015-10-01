"""
Report that will show the amount of credit available, vs. currently used.
"""
from gnu_reporting.wrapper import get_account, get_decimal
from gnu_reporting.reports.base import Report
from decimal import Decimal
from datetime import date
import time


class CreditUsage(Report):
    report_type = 'credit_usage'

    def __init__(self, name, credit_accounts):
        super(CreditUsage, self).__init__(name)
        self._credit_accounts = credit_accounts

    def __call__(self):

        today = date.today()
        today_time = time.mktime(today.timetuple())

        credit_amount = Decimal(0.0)
        credit_used = Decimal(0.0)

        for credit_definition in self._credit_accounts:
            account = get_account(credit_definition['account'])
            limit = credit_definition.get('limit', '0.0')

            credit_amount += Decimal(limit)

            balance = get_decimal(account.GetBalanceAsOfDate(today_time))
            credit_used += balance

        payload = self._generate_result()
        payload['data']['credit_limit'] = credit_amount + credit_used
        payload['data']['credit_amount'] = -credit_used

        return payload
