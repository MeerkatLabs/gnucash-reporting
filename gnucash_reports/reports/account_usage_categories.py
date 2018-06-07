"""
Report that will show the amount of money that is used between periods.

It further breaks down the amount spent into categories as defined in the configuration expense_categories configuration
object.
"""
from operator import itemgetter

from gnucash_reports.collate.bucket import CategoryCollate
from gnucash_reports.collate.bucket_generation import decimal_generator
from gnucash_reports.collate.store import split_summation
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.wrapper import account_walker, get_splits, parse_walker_parameters


def account_usage_categories(start=PeriodStart.this_month, end=PeriodEnd.this_month, accounts=None):
    """
    Walk through the accounts defined, and find calculate how money is spent based on the categories that the
    transaction split belongs to.
    :param start: date value to be used to filter down the data.
    :param end: date value to be used to filter down the data.
    :param accounts: walker parameters for the accounts that should be used to find how spending occurs.
    :return: dictionary containing
    - categories - tuple containing category name, and the amount that is spent in that category.
    """
    start_of_trend = PeriodStart(start)
    end_of_trend = PeriodEnd(end)

    accounts = parse_walker_parameters(accounts)

    data_values = CategoryCollate(decimal_generator, split_summation)

    for account in account_walker(**accounts):
        for split in get_splits(account, start_of_trend.date, end_of_trend.date, credit=False):

            transaction = split.transaction

            for transaction_split in [s for s in transaction.splits if s.account.fullname != account.fullname]:
                data_values.store_value(transaction_split)

    return {
        'categories': sorted([[k, v] for k, v in data_values.container.items()], key=itemgetter(0))
    }
