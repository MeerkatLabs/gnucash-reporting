from collections import defaultdict
from decimal import Decimal

from dateutil.rrule import rrule, MONTHLY


def decimal_generator():
    """Generates a single bucket containing a decimal object initialized to 0.0."""
    return Decimal('0.0')


def integer_generator():
    """Generates a single bucket that contains a 0 integer."""
    return int()


def debit_credit_generator():
    """Create a single bucket that contains a dictionary containing values for debit and credit values."""
    return dict(debit=Decimal('0.0'), credit=Decimal('0.0'))


def frequency_buckets(start, end, frequency=MONTHLY, interval=1, default_value_generator=decimal_generator):
    """
    Configure a method that will define all of the buckets based on stepping frequency distance between the start and
    end dates provided.
    :param start: start date for the collator.
    :param end: end date for the collator.
    :param frequency: how large of a step will the buckets contain (must be a dateutil.rrule enumeration)
    :param interval: how many steps in a bucket.
    :param default_value_generator: function used to generate the initialized value for the bucket.
    :return: function that will generate the buckets based on the period definition details created.
    """

    def generate_buckets():
        results = dict()
        for dt in rrule(frequency, dtstart=start, until=end, interval=interval):
            results[dt.date()] = default_value_generator()

        return results

    return generate_buckets


def category_buckets(default_value_generator):
    """
    Method generator that will create the collator collection.  Uses a default dictionary that will retrieve its
    initial value from the default value generator method provided.
    :param default_value_generator: function that creates the default value for the bucket.
    :return: function that will create a default dictionary using default value generator method to generate default
    values.
    """
    def generate_buckets():
        return defaultdict(default_value_generator)

    return generate_buckets
