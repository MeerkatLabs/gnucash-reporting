from collections import defaultdict
from decimal import Decimal

from dateutil.rrule import rrule, MONTHLY


def decimal_generator():
    return Decimal('0.0')


def integer_generator():
    return int()


def debit_credit_generator():
    return dict(debit=Decimal('0.0'), credit=Decimal('0.0'))


def monthly_buckets(start, end, frequency=MONTHLY, interval=1, default_value_generator=decimal_generator):

    def generate_buckets():
        results = dict()
        for dt in rrule(frequency, dtstart=start, until=end, interval=interval):
            results[dt.date()] = default_value_generator()

        return results

    return generate_buckets


def category_buckets(default_value_generator):
    """
    Create a default dictionary that will generate the buckets if they are missing.
    :param default_value_generator: value generator.
    :return:
    """
    def generate_buckets():
        return defaultdict(default_value_generator)

    return generate_buckets
