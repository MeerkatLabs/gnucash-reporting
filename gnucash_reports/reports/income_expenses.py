"""
Chart that will show the cash flow from income accounts to expense accounts.
"""
import time

from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.collate.bucket_generation import debit_credit_generator
from gnucash_reports.collate.store import store_credit_debit
from gnucash_reports.periods import PeriodEnd, PeriodStart, PeriodSize
from gnucash_reports.reports.base import Report, generate_results_package
from gnucash_reports.wrapper import account_walker, get_splits, parse_walker_parameters


class IncomeVsExpense(Report):
    report_type = 'income_vs_expense'

    def __init__(self, name, **kwargs):
        super(IncomeVsExpense, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return income_vs_expenses(self.name, None, self.kwargs)


def income_vs_expenses(name, description, definition):
    income_accounts = parse_walker_parameters(definition.get('income_accounts', []))
    expense_accounts = parse_walker_parameters(definition.get('expense_accounts', []))

    period_start = PeriodStart(definition.get('period_start', PeriodStart.this_month_year_ago))
    period_end = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))
    period_size = PeriodSize(definition.get('period_size', PeriodSize.month))

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
        credit_values.append(dict(date=time_value, value=-value['credit']))
        debit_values.append(dict(date=time_value, value=-value['debit']))
        difference_value.append(dict(date=time_value, value=-(value['debit'] + value['credit'])))

    return generate_results_package(name, 'income_vs_expense', description,
                                    expenses=sorted(credit_values, key=lambda s: s['date']),
                                    income=sorted(debit_values, key=lambda s: s['date']),
                                    net=sorted(difference_value, key=lambda s: s['date']),)
