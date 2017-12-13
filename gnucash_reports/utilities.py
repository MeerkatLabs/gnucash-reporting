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