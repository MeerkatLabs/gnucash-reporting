"""
Iterate through all of the accounts provided and give a categorized record of the expenses that have been charged to
that account.
"""
from decimal import Decimal
from operator import itemgetter

from gnucash_reports.collate.bucket import CategoryCollate
from gnucash_reports.collate.store import split_summation
from gnucash_reports.periods import PeriodStart, PeriodEnd
from gnucash_reports.reports.base import Report, generate_results_package
from gnucash_reports.wrapper import account_walker, get_splits, parse_walker_parameters


class AccountUsageCategories(Report):
    report_type = 'account_usage_categories'

    def __init__(self, name, **kwargs):
        super(AccountUsageCategories, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return account_usage_categories(self.name, None, self.kwargs)


def account_usage_categories(name, description, definition):
    start_of_trend = PeriodStart(definition.get('period_start', PeriodStart.this_month))
    end_of_trend = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))

    accounts = parse_walker_parameters(definition.get('accounts'))

    data_values = CategoryCollate(lambda: Decimal('0.0'), split_summation)

    for account in account_walker(**accounts):
        for split in get_splits(account, start_of_trend.date, end_of_trend.date, credit=False):

            transaction = split.transaction

            for transaction_split in [s for s in transaction.splits if s.account.fullname != account.fullname]:
                data_values.store_value(transaction_split)

    return generate_results_package(name, 'account_usage_categories', description,
                                    categories=sorted([[k, v] for k, v in data_values.container.iteritems()],
                                                      key=itemgetter(0)))
