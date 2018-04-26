"""
This report needs to go through all of the income transactions and look for credits that are made to the 401k of the
owner.
"""
from datetime import datetime, date
from decimal import Decimal

from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.configuration import current_date
from gnucash_reports.wrapper import get_splits, parse_walker_parameters, account_walker
from gnucash_reports.utilities import clean_account_name


def retirement_401k_report(income=None, retirement=None, start=PeriodStart.this_year,
                           end=PeriodEnd.this_year, contribution_limit='18000.0'):
    """
    Report that will calculate how much has been contributed to the retirement accounts from the income accounts
    provided.
    :param income: account walker parameters for income sources
    :param retirement: account walker parameters for retirement destinations
    :param start: the period to start calculating this report for
    :param end: the period to end calculating this report for
    :param contribution_limit: the maximum amount that can/will be contributed for the period
    :return: dictionary containing:
    contributionLimit - value from the arguments
    contribution - the amount contributed to retirement accounts from the income accounts
    dayOfYear - the current day of the year
    daysInYear - the number of days in the year
    """
    income = income or []
    retirement = retirement or []

    retirement_account_params = parse_walker_parameters(retirement)
    income_account_params = parse_walker_parameters(income)

    start = PeriodStart(start)
    end = PeriodEnd(end)

    contribution_limit = Decimal(contribution_limit)

    contribution_total = Decimal('0.0')

    today = current_date.get_today()
    beginning_of_year = date(today.year, 1, 1)

    retirement_accounts = [clean_account_name(account_name.fullname)
                           for account_name in account_walker(**retirement_account_params)]

    for account in account_walker(**income_account_params):

        for split in get_splits(account, start.date, end.date):
            parent = split.transaction

            for income_split in parent.splits:

                account_full_name = clean_account_name(income_split.account.fullname)

                if account_full_name in retirement_accounts:
                    contribution_total += income_split.value

    return {'contributionLimit': contribution_limit, 'contribution': contribution_total,
            'dayOfYear': today.timetuple().tm_yday,
            'daysInYear': date(today.year, 12, 31).timetuple().tm_yday}


# Have to change the report_type of this to match what it is called in the viewer.
retirement_401k_report.report_type = '401k_report'
