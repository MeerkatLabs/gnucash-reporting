"""Common utilities."""


def load_plugins():
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
    return account_name.replace(':', '.')
