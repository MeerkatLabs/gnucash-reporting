"""
Gathers up all of the expenses and breaks down the values by month.
"""
import time
import math
from operator import itemgetter

from gnucash_reports.collate.bucket import PeriodCollate, CategoryCollate, AccountCollate
from gnucash_reports.collate.bucket_generation import decimal_generator, integer_generator
from gnucash_reports.collate.store import split_summation, count
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters


def expenses_period(definition):
    expense_accounts = parse_walker_parameters(definition.get('expenses_base', []))
    start_period = PeriodStart(definition.get('period_start', PeriodStart.this_month_year_ago))
    end_period = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))
    period_size = PeriodSize(definition.get('period_size', PeriodSize.month))
    show_record_count = definition.get('show_record_count', False)

    bucket = PeriodCollate(start_period.date, end_period.date, decimal_generator, split_summation,
                           frequency=period_size.frequency, interval=period_size.interval)
    record_count = PeriodCollate(start_period.date, end_period.date, integer_generator, count,
                                 frequency=period_size.frequency, interval=period_size.interval)

    for account in account_walker(**expense_accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)
            record_count.store_value(split)

    sorted_results = []
    sorted_count_results = []

    for key, value in bucket.container.iteritems():
        sorted_results.append(dict(date=time.mktime(key.timetuple()), value=value))

    for key, value in record_count.container.iteritems():
        sorted_count_results.append(dict(date=time.mktime(key.timetuple()), value=value))

    data_set = {
        'expenses': sorted(sorted_results, key=lambda s: s['date'])
    }

    if show_record_count:
        data_set['count'] = sorted(sorted_count_results, key=lambda s: s['date'])

    return data_set


def expenses_box(definition):
    expense_accounts = parse_walker_parameters(definition.get('expenses_base', []))
    start_period = PeriodStart(definition.get('period_start', PeriodStart.this_month_year_ago))
    end_period = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))
    period_size = PeriodSize(definition.get('period_size', PeriodSize.month))

    bucket = PeriodCollate(start_period.date, end_period.date, decimal_generator, split_summation,
                           frequency=period_size.frequency, interval=period_size.interval)

    for account in account_walker(**expense_accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)

    results = []

    for key, value in bucket.container.iteritems():
        results.append(float(value))

    results = sorted(results)

    return dict(low=results[0],
                high=results[-1],
                q1=get_median(get_lower_half(results)),
                q2=get_median(results),
                q3=get_median(get_upper_half(results)),)


def expenses_categories(definition):
    expense_accounts = parse_walker_parameters(definition.get('expenses_base', []))
    start_period = PeriodStart(definition.get('period_start', PeriodStart.this_month))
    end_period = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))

    bucket = CategoryCollate(decimal_generator, split_summation)

    for account in account_walker(**expense_accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)

    return dict(categories=sorted([[key, value] for key, value in bucket.container.iteritems()], key=itemgetter(0)))


def expense_accounts(definition):
    accounts = parse_walker_parameters(definition.get('expenses_base', []))
    start_period = PeriodStart(definition.get('period_start', PeriodStart.this_month_year_ago))
    end_period = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))

    bucket = AccountCollate(decimal_generator, split_summation)

    for account in account_walker(**accounts):
        for split in get_splits(account, start_period.date, end_period.date):
            bucket.store_value(split)

    return dict(categories=sorted([[key, value] for key, value in bucket.container.iteritems()], key=itemgetter(0)))


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
