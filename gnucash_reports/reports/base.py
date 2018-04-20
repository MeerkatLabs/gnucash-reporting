"""
Definition of a report.
"""
_reports = dict()


def register_plugin(report, report_type=None):
    """
    Register the plugin class definition into the module.
    :param report: report definition class.  Must have a class variable of report_type.
    :param report_type: the type of report being identified, if none, a valid value will searched for.
    :return: None
    """
    global _reports

    if report_type:
        _reports[report_type] = report
    else:
        try:
            _reports[report.report_type] = report
        except AttributeError:
            _reports[report.func_name] = report


def run_report(type='UNDEFINED_REPORT', name='UNTITLED_REPORT', description=None, definition=None):
    """
    Execute the report as defined by arguments.
    :param type: string containing the report type.
    :param name: string containing the report name
    :param description: string containing a description
    :param definition: a dictionary containing the report configuration parameters
    :return:
    """
    definition = definition or {}

    _report = _reports.get(type, None)

    if _report:
        payload = _report(**definition)

        return {
            'name': name,
            'description': description,
            'type': type,
            'data': payload
        }

    print 'Could not find report by name: %s' % type
    return None


def multi_report(reports=None):
    """
    Report that will calculate multiple reports and store the results.
    :param reports: list of reports to execute
    :return: dictionary containing
    reports - results of the reports that were executed
    """
    report_definitions = reports or []

    report_results = []
    for report in report_definitions:
        _result = run_report(**report)
        if _result:
            report_results.append(_result)

    return dict(reports=report_results)
