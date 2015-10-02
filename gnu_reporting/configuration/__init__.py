from gnu_reporting.configuration.base import register_configuration_plugin as _register_configuration_plugin, \
    configure_application

from gnu_reporting.configuration.currency import configure as _configure_currency
from gnu_reporting.configuration.inflation import configure as _configure_inflation
from gnu_reporting.configuration.tax_tables import configure_tax_tables


def register_core_configuration_plugins():
    """
    Register all of the core configuration plugins for the application
    :return:
    """
    _register_configuration_plugin(_configure_currency)
    _register_configuration_plugin(_configure_inflation)
    _register_configuration_plugin(configure_tax_tables)
