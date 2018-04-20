"""
Gathers up all of the expenses and breaks down the values by month.
"""
import time
import math
from operator import itemgetter

from gnucash_reports.collate.bucket import PeriodCollate, CategoryCollate, AccountCollate
from gnucash_reports.collate.bucket_generation import decimal_generator
from gnucash_reports.collate.store import split_summation
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters


def expenses_period(expenses=None, start=PeriodStart.this_month_year_ago, end=PeriodEnd.this_month,
                    period_size=PeriodSize.month):
    """
    Calculate the amount of money that when into an expense account over the given period.
    :param expenses: account walker parameters for accounts to calculate
    :param start: the start of the time frame for the report
    :param end: the end of the time frame for the report
    :param period_size: the size of the buckets for the report
    :return: dictionary containing:
    expenses: sorted dictionary containing keys for date and value.
    """
    expenses = expenses or []

    accounts = parse_walker_parameters(expenses)
    start_period = PeriodStart(start)
    end_period = PeriodEnd(end)
    period_size = PeriodSize(period_size)

    bucket = PeriodCollate(start_period.date, end_period.date, decimal_generator, split_summation,
                           frequency=period_size.frequency, interval=period_size.interval)

    for account in account_walker(**accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)

    sorted_results = []

    for key, value in bucket.container.iteritems():
        sorted_results.append((time.mktime(key.timetuple()), value))

    data_set = {
        'expenses': sorted(sorted_results, key=itemgetter(0))
    }

    return data_set


def expenses_box(expenses=None, start=PeriodStart.this_month_year_ago, end=PeriodEnd.this_month,
                 period_size=PeriodSize.month):
    """
    Calculate the amount of money that when into an expense account over the given period.
    :param expenses: account walker parameters for accounts to calculate
    :param start: the start of the time frame for the report
    :param end: the end of the time frame for the report
    :param period_size: the size of the buckets for the report
    :return: dictionary containing:
    expenses: dictionary containing the following keys:
        low - lowest amount spent
        high - highest amount spent
        q1 - first quartile value
        q2 - second quartile value
        q3 - third quartile value
    """
    expenses = expenses or []

    accounts = parse_walker_parameters(expenses)
    start_period = PeriodStart(start)
    end_period = PeriodEnd(end)
    period_size = PeriodSize(period_size)

    bucket = PeriodCollate(start_period.date, end_period.date, decimal_generator, split_summation,
                           frequency=period_size.frequency, interval=period_size.interval)

    for account in account_walker(**accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)

    results = []

    for key, value in bucket.container.iteritems():
        results.append(float(value))

    results = sorted(results)

    return {'low': results[0], 'high': results[-1], 'q1': get_median(get_lower_half(results)),
            'q2': get_median(results), 'q3': get_median(get_upper_half(results))}


def expenses_categories(expenses=None, start=PeriodStart.this_month, end=PeriodEnd.this_month):
    """
    Walk through the accounts defined in expenses base and collate the spending in the period into the categories
    defined in the configuration object.
    :param expenses: account walker definition of the accounts to grab expenses for.
    :param start: when the report should start collecting data from
    :param end: when the report should stop collecting data
    :return: dictionary containing:
    categories - list of tuples (category name, value) containing the results sorted by category name
    """
    expenses = expenses or []

    accounts = parse_walker_parameters(expenses)
    start_period = PeriodStart(start)
    end_period = PeriodEnd(end)

    bucket = CategoryCollate(decimal_generator, split_summation)

    for account in account_walker(**accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)

    return {'categories': sorted([[key, value] for key, value in bucket.container.iteritems()], key=itemgetter(0))}


def expense_accounts(expenses=None, start=PeriodStart.this_month_year_ago, end=PeriodEnd.this_month):
    """
    Walk through the accounts defined in expenses base and collate the spending into categories that are named after the
    leaf account name.
    :param expenses: account walker definition of the accounts to grab expenses for.
    :param start: when the report should start collecting data from
    :param end: when the report should stop collecting data
    :return: dictionary containing:
    categories - list of tuples (category name, value) containing the results sorted by category name
    """
    expenses = expenses or []

    accounts = parse_walker_parameters(expenses)
    start_period = PeriodStart(start)
    end_period = PeriodEnd(end)

    bucket = AccountCollate(decimal_generator, split_summation)

    for account in account_walker(**accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)

    return {'categories': sorted([[key, value] for key, value in bucket.container.iteritems()], key=itemgetter(0))}


# Calculating the quartiles based on:
# https://en.wikipedia.org/wiki/Quartile Method 1
def get_median(lst):
    lst_cnt = len(lst)
    mid_idx = int(lst_cnt / 2)
    if lst_cnt % 2 != 0:
        return lst[mid_idx]
    return (lst[mid_idx-1] + lst[mid_idx]) / 2


def get_lower_half(lst):
    mid_idx = int(math.floor(len(lst) / 2))
    return lst[0:mid_idx]


def get_upper_half(lst):
    mid_idx = int(math.ceil(len(lst) / 2))
    return lst[mid_idx:]
