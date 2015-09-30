from decimal import Decimal
from dateutil.rrule import rrule, MONTHLY
from datetime import date

def monthly(start, end):

    def generate_buckets():
        results = dict()
        for dt in rrule(MONTHLY, dtstart=start, until=end):
            results[date(dt.year, dt.month, 1)] = Decimal('0.0')

        return results

    return generate_buckets
