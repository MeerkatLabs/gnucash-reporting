from datetime import date, datetime
from gnu_reporting.configuration.expense_categories import get_category_for_account

def monthly(data_key):
    """
    Returns the bucket that the hash value should be stored into based on the data key that is provided.
    :param data_key: data key value.
    :return: hash key value.
    """
    split_date = datetime.fromtimestamp(data_key.parent.GetDate())
    return date(split_date.year, split_date.month, 1)


def category_key_fetcher(data_key):
    """
    Look up the category that is associated with the account defined in the split.
    :param data_key:  split
    :return:
    """
    return get_category_for_account(data_key.GetAccount().get_full_name())
