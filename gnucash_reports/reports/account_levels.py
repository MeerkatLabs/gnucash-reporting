"""
Collection of reports that will warn when the level of an account gets to be low.
"""
from gnucash_reports.periods import PeriodStart
from gnucash_reports.wrapper import get_account, get_balance_on_date


def account_levels(definition):
    """
    Build a simple stacked bar chart that shows a progress bar of the data.
    :param definition:
    :return:
    """
    account_name = definition['account']
    when = PeriodStart(definition.get('when', PeriodStart.today))

    balance = get_balance_on_date(get_account(account_name), when.date)

    return dict(balance=balance,
                good_value=definition.get('good_value', 5000),
                warn_value=definition.get('warn_value', 2500),
                error_value=definition.get('error_value', 1000))
