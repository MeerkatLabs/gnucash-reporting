"""
Load the expense categories from the configuration file and provide a means to query the category name from the account
that it is stored in.
"""

_expense_categories = dict()
_reverse = dict()
_default_category = 'OTHER'


def configure(json_dictionary):
    """
    Will configure the expenses categories for the transactions provided.
    :param json_dictionary:
    :return:
    """
    global _expense_categories, _reverse
    _expense_categories = json_dictionary

    for category, accounts in json_dictionary.iteritems():
        for account in accounts:
            _reverse[account] = category


def get_category_for_account(account_name):
    """
    Look up the category for a given account.
    :param account_name:
    :return:
    """
    return _reverse.get(account_name, _default_category)
