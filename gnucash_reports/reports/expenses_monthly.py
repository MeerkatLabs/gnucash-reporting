"""
Gathers up all of the expenses and breaks down the values by month.
"""
import time
from operator import itemgetter

import numpy as np

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

    return dict(low=np.percentile(results, 0),
                high=np.percentile(results, 100),
                q1=np.percentile(results, 25),
                q2=np.percentile(results, 50),
                q3=np.percentile(results, 75),)


def expenses_categories(definition):
    expense_accounts = parse_walker_parameters(definition.get('expenses_base', []))
    start_period = PeriodStart(definition.get('period_start', PeriodStart.this_month_year_ago))
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
