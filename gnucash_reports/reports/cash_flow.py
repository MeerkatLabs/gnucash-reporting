"""
Cash flow report for an account and it's children.
"""
import time

from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.collate.bucket_generation import debit_credit_generator
from gnucash_reports.collate.store import store_credit_debit
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters
from operator import itemgetter


def cash_flow(accounts=None, start=PeriodStart.this_month_year_ago, end=PeriodEnd.this_month,
              period_size=PeriodSize.month):
    """
    Create a report showing the amount of money that enters and exits an account over a period of time.  Each row
    in the report is based on period size values.
    :param accounts: account walker properties to define the accounts that are reported on
    :param start: the PeriodStart definition that tells when the report should start collecting data from
    :param end: the PeriodEnd definition that tells when the report should stop collecting data
    :param period_size: the size of the buckets to store the data into.
    :return: dictionary containing:
    credits - sorted list of dictionaries containing date and value keys
    debit - sorted list of dictionaries containing date and value keys
    net - sorted list of dictionaries containing date and value keys
    """
    accounts = accounts or []

    accounts = parse_walker_parameters(accounts)
    period_start = PeriodStart(start)
    period_end = PeriodEnd(end)
    period_size = PeriodSize(period_size)

    bucket = PeriodCollate(period_start.date, period_end.date, debit_credit_generator,
                           store_credit_debit, frequency=period_size.frequency, interval=period_size.interval)

    for account in account_walker(**accounts):
        for split in get_splits(account, period_start.date, period_end.date):
            bucket.store_value(split)

    credit_values = []
    debit_values = []
    difference_value = []

    for key, value in bucket.container.items():
        store_key = time.mktime(key.timetuple())
        credit_values.append((store_key, value['credit']))
        debit_values.append((store_key, value['debit']))
        difference_value.append((store_key, value['credit'] + value['debit']))

    return {'credits': sorted(credit_values, key=itemgetter(0)),
            'debits': sorted(debit_values, key=itemgetter(0)),
            'net': sorted(difference_value, key=itemgetter(0))}
