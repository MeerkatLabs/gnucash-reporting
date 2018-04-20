"""
Base of the configuration parsing plugins.  Each of these will need to provide a method that will be executed with a
copy of the configuration global object from core.json.
"""

_plugins = []


def register_configuration_plugin(_callable):
    """
    Register a callable that will be used to configure a sub component of the application.
    :param _callable: that will be provided the configuration details.
    """
    global _plugins
    _plugins.append(_callable)


def configure_application(configuration):
    """
    Iterate through all of the configuration plugins and configure based on the provided configuration values.
    :param configuration: dictionary containing the configuration.
    """
    for plugin in _plugins:
        plugin(configuration.copy())
