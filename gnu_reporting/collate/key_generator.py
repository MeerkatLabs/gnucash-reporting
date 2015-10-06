from datetime import date, datetime
from gnu_reporting.configuration.expense_categories import get_category_for_account
from dateutil.rrule import rrule, MONTHLY


def monthly(data_key):
    """
    Returns the bucket that the hash value should be stored into based on the data key that is provided.
    :param data_key: data key value.
    :return: hash key value.
    """
    split_date = datetime.fromtimestamp(data_key.parent.GetDate())
    return date(split_date.year, split_date.month, 1)


def period(start, end, frequency=MONTHLY, interval=1):

    intervals = rrule(frequency, start, interval=interval, until=end)

    def method(data_key):
        split_date = datetime.fromtimestamp(data_key.parent.GetDate())
        return intervals.before(split_date, inc=True).date()

    return method


def category_key_fetcher(data_key):
    """
    Look up the category that is associated with the account defined in the split.
    :param data_key:  split
    :return:
    """
    return get_category_for_account(data_key.GetAccount().get_full_name())
