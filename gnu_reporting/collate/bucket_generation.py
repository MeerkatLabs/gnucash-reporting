from decimal import Decimal
from dateutil.rrule import rrule, MONTHLY
from datetime import date


def decimal_generator():
    return Decimal('0.0')


def debit_credit_generator():
    return dict(debit=Decimal('0.0'), credit=Decimal('0.0'))


def monthly_buckets(start, end, default_value_generator=decimal_generator):

    def generate_buckets():
        results = dict()
        for dt in rrule(MONTHLY, dtstart=start, until=end):
            results[date(dt.year, dt.month, 1)] = default_value_generator()

        return results

    return generate_buckets


