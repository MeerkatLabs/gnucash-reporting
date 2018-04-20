from decimal import Decimal

from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.periods import PeriodStart
from gnucash_reports.wrapper import get_balance_on_date, account_walker, parse_walker_parameters


def savings_goal(savings=None, goal='0.0', as_of=PeriodStart.today, contributions=None):
    """
    Report that shows progress towards a savings goal.
    :param savings: account walker parameters for the accounts that should have their balance count towards the goal
    :param goal: the amount that should be in the account for the goal to be met (in currency)
    :param as_of: when should the balance be looked up for
    :param contributions: list of additional contributions towards the goal which are not apart of the account
    :return: dictionary containing:
    balance - balance of the account and the contributions
    goal - the goal for the account to be at
    """
    savings = savings or []

    walker_params = parse_walker_parameters(savings)

    goal_amount = Decimal(goal)

    as_of = PeriodStart(as_of)
    contributions = contributions or []

    if not isinstance(contributions, list):
        contributions = [contributions]

    total_balance = Decimal('0.0')
    currency = get_currency()

    for account in account_walker(**walker_params):
        balance = get_balance_on_date(account, as_of.date, currency)
        total_balance += balance

    for contribution in contributions:
        total_balance += Decimal(contribution)

    return {'balance': total_balance, 'goal': goal_amount}
