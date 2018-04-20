"""
Chart that will show the cash flow from income accounts to expense accounts.
"""
import time

from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.collate.bucket_generation import debit_credit_generator
from gnucash_reports.collate.store import store_credit_debit
from gnucash_reports.periods import PeriodEnd, PeriodStart, PeriodSize
from gnucash_reports.wrapper import account_walker, get_splits, parse_walker_parameters

from operator import itemgetter


def income_vs_expense(income_accounts=None, expense_accounts=None, start=PeriodStart.this_month_year_ago,
                      end=PeriodEnd.this_month, period_size=PeriodSize.month):
    """
    Report that collects the expenses from the expense accounts defined, the income from the income accounts defined
    and collates the data into buckets based on the arguments for start, end, and period_size.
    :param income_accounts: account walker parameters for the income accounts to walk through
    :param expense_accounts: account walker parameters for the expense accounts to walk through
    :param start: how far back to collect data for
    :param end: how far forward to collect data for
    :param period_size: the size of the buckets to collect data for.
    :return: dictionary containing:
    - expenses: list of dictionaries containing date and value key value pairs for the expenses defined
    - income: list of dictionaries containing date and value paris for the income defined
    - net: list of dictionaries containing date and value pairs for the net values defined
    """
    income_accounts = income_accounts or []
    expense_accounts = expense_accounts or []

    income_accounts = parse_walker_parameters(income_accounts)
    expense_accounts = parse_walker_parameters(expense_accounts)

    period_start = PeriodStart(start)
    period_end = PeriodEnd(end)
    period_size = PeriodSize(period_size)

    bucket = PeriodCollate(period_start.date, period_end.date, debit_credit_generator,
                           store_credit_debit, frequency=period_size.frequency,
                           interval=period_size.interval)

    for account in account_walker(**income_accounts):
        for split in get_splits(account, period_start.date, period_end.date):
            bucket.store_value(split)

    for account in account_walker(**expense_accounts):
        for split in get_splits(account, period_start.date, period_end.date):
            bucket.store_value(split)

    credit_values = []
    debit_values = []
    difference_value = []

    for key, value in bucket.container.iteritems():
        time_value = time.mktime(key.timetuple())

        # Have to switch the signs so that the graph will make sense.  In GNUCash the income accounts are debited
        # when paid, and the expense accounts are 'credited' when purchased.
        credit_values.append((time_value, -value['credit']))
        debit_values.append((time_value, -value['debit']))
        difference_value.append((time_value, -(value['debit'] + value['credit'])))

    return {'expenses': sorted(credit_values, key=itemgetter(0)),
            'income': sorted(debit_values, key=itemgetter(0)),
            'net': sorted(difference_value, key=itemgetter(0))}
