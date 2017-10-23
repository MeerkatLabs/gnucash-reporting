"""
This report needs to go through all of the income transactions and look for credits that are made to the 401k of the
owner.
"""
from gnucash_reports.reports.base import Report
from gnucash_reports.wrapper import get_account, get_decimal, get_splits
from gnucash_reports.periods import PeriodStart, PeriodEnd
from datetime import date
from decimal import Decimal


class Retirement401kReport(Report):
    report_type = '401k_report'

    def __init__(self, name, income_accounts, retirement_accounts, contribution_limit=None,
                 period_start=PeriodStart.this_year, period_end=PeriodEnd.this_year):
        super(Retirement401kReport, self).__init__(name)

        self.income_accounts = income_accounts
        self.retirement_accounts = retirement_accounts

        self._start = PeriodStart(period_start)
        self._end = PeriodEnd(period_end)

        if contribution_limit:
            self.contribution_limit = contribution_limit
        else:
            self.contribution_limit = Decimal('18000.0')

    def __call__(self):
        contribution_total = Decimal('0.0')
        today = date.today()
        beginning_of_year = date(today.year, 1, 1)

        for account_name in self.income_accounts:
            account = get_account(account_name)

            for split in get_splits(account, self._start.date, self._end.date):
                parent = split.parent

                for income_split in parent.GetSplitList():

                    if income_split.GetAccount().get_full_name() in self.retirement_accounts:
                        contribution_total += get_decimal(income_split.GetAmount())

        result = self._generate_result()
        result['data']['contributionLimit'] = self.contribution_limit
        result['data']['contribution'] = contribution_total
        result['data']['dayOfYear'] = (today - beginning_of_year).days + 1
        result['data']['daysInYear'] = (date(today.year, 12, 31) - beginning_of_year).days + 1

        return result
