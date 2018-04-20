"""
Report that will warn when the level of an account gets to be low.
"""
from gnucash_reports.periods import PeriodStart
from gnucash_reports.wrapper import get_account, get_balance_on_date


def account_levels(account=None, when=PeriodStart.today, goal=5000, warn_value=2500, error_value=1000):
    """
    Build a simple stacked bar chart that shows a progress bar of the data.
    :param account: full account name of which account to get the balance from.
    :param when: PeriodStart enumeration containing when to calculate the value from.
    :param goal: this is the goal for the account, any thing less than this is considered an underage, but not
    necessary warning worthy.
    :param warn_value: if balance is less than this value, it should be displayed as a "warning"
    :param error_value: if balance is less than this value, it should be displayed as an "error"
    :return: dictionary containing:
    balance - the balance of the account as of 'when'
    good_value - the goal value from configuration
    warn_value - the warn value from configuration
    error_Value - the error value from configuration
    """
    when = PeriodStart(when)

    balance = get_balance_on_date(get_account(account), when.date)

    return {
        'balance': balance,
        'goal': goal,
        'warn_value': warn_value,
        'error_value': error_value
    }
