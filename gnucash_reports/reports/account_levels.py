"""
Collection of reports that will warn when the level of an account gets to be low.
"""
from gnucash_reports.periods import PeriodStart
from gnucash_reports.reports.base import Report, generate_results_package
from gnucash_reports.wrapper import get_account, get_balance_on_date


class AccountLevels(Report):
    report_type = 'account_levels'

    def __init__(self, name, **kwargs):
        super(AccountLevels, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return account_levels(self.name, None, self.kwargs)


def account_levels(name, description, definition):
    """
    Build a simple stacked bar chart that shows a progress bar of the data.
    :param name:
    :param description:
    :param definition:
    :return:
    """
    account_name = definition['account']
    when = PeriodStart(definition.get('when', PeriodStart.today))

    balance = get_balance_on_date(get_account(account_name), when.date)

    return generate_results_package(name, 'account_levels', description,
                                    balance=balance,
                                    good_value=definition.get('good_value', 5000),
                                    warn_value=definition.get('warn_value', 2500),
                                    error_value=definition.get('error_value', 1000)
                                    )
