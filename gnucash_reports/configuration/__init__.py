from gnucash_reports.configuration.base import register_configuration_plugin as _register_configuration_plugin, \
    configure_application

from gnucash_reports.configuration.currency import configure as _configure_currency
from gnucash_reports.configuration.inflation import configure as _configure_inflation
from gnucash_reports.configuration.tax_tables import configure_tax_tables
from gnucash_reports.configuration.expense_categories import configure as _configure_expense_categories
from gnucash_reports.configuration.investment_allocations import configure as _configure_investment_allocations


def register_core_configuration_plugins():
    """
    Register all of the core configuration plugins for the application
    :return:
    """
    _register_configuration_plugin(_configure_currency)
    _register_configuration_plugin(_configure_inflation)
    _register_configuration_plugin(configure_tax_tables)
    _register_configuration_plugin(_configure_expense_categories)
    _register_configuration_plugin(_configure_investment_allocations)
