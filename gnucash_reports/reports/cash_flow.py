"""
Cash flow report for an account and it's children.
"""
import time

from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.collate.bucket_generation import debit_credit_generator
from gnucash_reports.collate.store import store_credit_debit
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.reports.base import Report, generate_results_package
from gnucash_reports.wrapper import get_splits, account_walker, parse_walker_parameters


class MonthlyCashFlow(Report):
    report_type = 'cash_flow_chart'

    def __init__(self, name, **kwargs):
        super(MonthlyCashFlow, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return cash_flow(self.name, None, self.kwargs)


def cash_flow(name, description, definition):

    accounts = parse_walker_parameters(definition.get('accounts', []))
    period_start = PeriodStart(definition.get('period_start', PeriodStart.this_month_year_ago))
    period_end = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))
    period_size = PeriodSize(definition.get('period_size', PeriodSize.month))

    bucket = PeriodCollate(period_start.date, period_end.date, debit_credit_generator,
                           store_credit_debit, frequency=period_size.frequency, interval=period_size.interval)

    for account in account_walker(**accounts):
        for split in get_splits(account, period_start.date, period_end.date):
            bucket.store_value(split)

    credit_values = []
    debit_values = []
    difference_value = []

    for key, value in bucket.container.iteritems():
        credit_values.append(dict(date=time.mktime(key.timetuple()), value=value['credit']))
        debit_values.append(dict(date=time.mktime(key.timetuple()), value=value['debit']))
        difference_value.append(dict(date=time.mktime(key.timetuple()), value=value['credit'] + value['debit']))

    return generate_results_package(name, 'cash_flow_chart', description,
                                    credits=sorted(credit_values, key=lambda s: s['date']),
                                    debits=sorted(debit_values, key=lambda s: s['date']),
                                    gross=sorted(difference_value, key=lambda s: ['date']))
