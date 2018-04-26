import re
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime

from gnucash_reports.configuration.expense_categories import get_category_for_account
from gnucash_reports.utilities import clean_account_name


def period(start, end, frequency=MONTHLY, interval=1):
    """
    Defines a key generation method that will hash a split's transaction's post date into the appropriate bucket key
    for the period bucket that was defined.
    :param start: start date of all buckets
    :param end: end date of all buckets
    :param frequency: size of the bucket using dateutil.rrule enumeration
    :param interval: how many frequencies in a bucket
    :return: a method that will hash the incoming split value into a date key for the collator.
    """

    intervals = rrule(frequency, start, interval=interval, until=end)

    def method(data_key):
        split_date = datetime.combine(data_key.transaction.post_date, datetime.max.time())
        return intervals.before(split_date, inc=True).date()

    return method


def category_key_fetcher(data_key):
    """
    Find the category that the account name belongs to.
    :param data_key: transaction split
    :return: string
    """
    return get_category_for_account(clean_account_name(data_key.account.fullname))


def account_key_fetcher(data_key):
    """
    Return the last account name in the tree.  Account names are split on both : and . characters.
    :param data_key: transaction split
    :return: string
    """
    return re.split('[:.]', data_key.account.fullname)[-1]
