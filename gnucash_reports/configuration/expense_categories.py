"""
Load the expense categories from the configuration file and provide a means to query the category name from the account
that it is stored in.
"""
from gnucash_reports.utilities import clean_account_name

_expense_categories = dict()
_reverse = dict()
_default_category = 'OTHER'


def configure(configuration):
    """
    Load a list of all the expense categories and the accounts that implement that category.  The account definition
    is a dictionary that will be passed to the account walker method to find accounts (so can ignore and recursively
    search an account tree).
    :param configuration: configuration object.
    """
    global _expense_categories, _reverse
    from gnucash_reports.wrapper import account_walker, parse_walker_parameters

    for definition in configuration.get('expenses_categories', []):
        category = definition['name']
        accounts = parse_walker_parameters(definition.get('definition', []))

        all_accounts = set()
        for account in account_walker(**accounts):
            # print(f'loading account: {account.fullname}')
            all_accounts.add(clean_account_name(account.fullname))

        for account in all_accounts:
            _reverse[account] = category

        _expense_categories[category] = all_accounts


def get_category_for_account(account_name):
    """
    Look up the category for a given account.
    :param account_name: full account name string.
    :return: category name.
    """
    # Translate the account name to use the common formatting.
    account_name = clean_account_name(account_name)
    value = _reverse.get(account_name, _default_category)

    if value == _default_category:
        print(f'Returning: {account_name} -> {_default_category}')

    return value


def get_accounts_for_category(category_name):
    """
    Return all of the accounts associated with a specific category.
    :param category_name: string
    :return: list of account names.
    """
    return list(_expense_categories.get(category_name, []))
