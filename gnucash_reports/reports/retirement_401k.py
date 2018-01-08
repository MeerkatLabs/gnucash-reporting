"""
This report needs to go through all of the income transactions and look for credits that are made to the 401k of the
owner.
"""
from datetime import date
from decimal import Decimal

from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.wrapper import get_account, get_splits


def retirement_401k_report(definition):

    income_accounts = definition.get('income_accounts', [])
    retirement_accounts = definition.get('retirement_accounts', [])

    start = PeriodStart(definition.get('period_start', PeriodStart.this_year))
    end = PeriodEnd(definition.get('period_end', PeriodEnd.this_year))

    contribution_limit = definition.get('contribution_limit', Decimal('18000.0'))

    contribution_total = Decimal('0.0')
    today = date.today()
    beginning_of_year = date(today.year, 1, 1)

    retirement_accounts = [account_name.replace(':', '.') for account_name in retirement_accounts]

    for account_name in income_accounts:
        account = get_account(account_name)

        for split in get_splits(account, start.date, end.date):
            parent = split.transaction

            for income_split in parent.splits:

                account_full_name = income_split.account.fullname.replace(':', '.')

                if account_full_name in retirement_accounts:
                    contribution_total += income_split.value

    return dict(contributionLimit=contribution_limit, contribution=contribution_total,
                dayOfYear=(today - beginning_of_year).days + 1,
                daysInYear=(date(today.year, 12, 31) - beginning_of_year).days + 1)


# Have to change the report_type of this to match what it is called in the viewer.
retirement_401k_report.report_type = '401k_report'
