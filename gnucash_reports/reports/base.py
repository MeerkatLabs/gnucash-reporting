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


def run_report(report_definition):
    report_type = report_definition.get('type', 'UNDEFINED_REPORT')
    _report = _reports.get(report_type, None)

    if _report:
        name = report_definition.get('name', 'UNTITLED_REPORT')
        description = report_definition.get('description', None)
        definition = report_definition.get('definition', {})

        payload = _report(definition)

        return {
            'name': name,
            'description': description,
            'type': report_type,
            'data': payload
        }

    print 'Could not find report by name: %s' % report_type
    return None


def multi_report(definition):
    report_definitions = definition.get('reports', [])

    report_results = []
    for report in report_definitions:
        _result = run_report(report)
        if _result:
            report_results.append(_result)

    return dict(reports=report_results)
