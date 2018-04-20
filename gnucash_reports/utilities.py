"""Common utilities."""
from operator import itemgetter
import time


def load_plugins():
    """
    Load in the report and configuration values from defined entry points.
    :return:
    """
    import pkg_resources

    # Register the reports
    for ep in pkg_resources.iter_entry_points(group='gnucash_reports_reports'):
        loader = ep.load()
        loader()

    # Register the configuration
    for ep in pkg_resources.iter_entry_points(group='gnucash_reports_configuration'):
        loader = ep.load()
        loader()


def clean_account_name(account_name):
    """Replace account names with colons as separators with periods as separators."""
    # TODO: Move this to a configuration value.
    return account_name.replace(':', '.')


def identity(x):
    """Return argument"""
    return x


def time_series_dict_to_list(dictionary, key=lambda x: time.mktime(x.timetuple()), value=identity):
    """
    Convert the incoming dictionary of keys to a list of sorted tuples.
    :param dictionary: dictionary to retrieve data from
    :param key: expression used to retrieve the time_series key from the key
    :param value: expression used to retrieve the time_series value from the value
    :return: list of tuples where index 0 is seconds since epoch, and index 1 is value
    """
    if key is None:
        key = identity

    if value is None:
        value = identity

    time_series = [[key(k), value(v)] for k, v in dictionary.iteritems()]
    return sorted(time_series, key=itemgetter(0))
