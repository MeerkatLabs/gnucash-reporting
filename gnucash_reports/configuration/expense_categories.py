"""
Load the expense categories from the configuration file and provide a means to query the category name from the account
that it is stored in.
"""
from gnucash_reports.wrapper import account_walker

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

    for definition in json_dictionary.get('expenses_categories', []):
        category = definition['name']
        accounts = definition['accounts']
        recursive = definition.get('recursive', False)

        if recursive:
            all_accounts = []
            for account in account_walker(accounts, place_holders=True):
                # print 'loading account: %s' % account.fullname
                all_accounts.append(account.fullname)
        else:
            all_accounts = accounts

        for account in all_accounts:
            _reverse[account] = category

        _expense_categories[category] = all_accounts


def get_category_for_account(account_name):
    """
    Look up the category for a given account.
    :param account_name:
    :return:
    """
    value = _reverse.get(account_name, _default_category)

    if value == _default_category:
        print 'Returning: %s -> %s' % (account_name, _default_category)

    return value


def get_accounts_for_category(category_name):
    """
    Return all of the accounts associated with a specific category.
    :param category_name:
    :return:
    """
    return _expense_categories.get(category_name, [])
