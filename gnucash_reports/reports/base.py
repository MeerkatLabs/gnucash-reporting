"""
Definition of a report.
"""
_reports = dict()


def register_plugin(report):
    """
    Register the plugin class definition into the module.
    :param report: report definition class.  Must have a class variable of report_type.
    :return: None
    """
    global _reports
    _reports[report.report_type] = report


def get_report(_report_type):
    """
    Retrieve the report class definition from the module from the report_type string provided.
    :param _report_type: string
    :return: report class definition.
    """
    return _reports[_report_type]


def build_report(_definition):
    name = _definition.get('name', 'Unnamed Report')
    report_type = _definition.get('type', 'UNDEFINED_REPORT')
    description = _definition.get('description', None)
    definition = _definition.get('definition', dict())

    report = get_report(report_type)
    if report:
        _report = report(name, **definition)
        _report.description = description
        return _report

    return None


class Report(object):
    """
    Report Base type.
    """
    report_type = 'unknown'

    def __init__(self, name, description=None):
        self.name = name
        self.description = None

        if description:
            self.description = description

    def _generate_result(self):
        """
        Return a container with the basic details of the report populated for the subclasses.
        :return: dictionary
        """
        results = dict(name=self.name, type=self.report_type, data=dict())

        if self.description:
            results['description'] = self.description

        return results


def generate_results_package(name, report_type, description=None, data=None, **kwargs):
    if not data:
        data = dict()

    data.update(**kwargs)

    results = dict(name=name, type=report_type, data=data)
    if description:
        results['description'] = description

    return {
        'name': name,
        'type': report_type,
        'description': description,
        'data': data
    }


class MultiReport(Report):
    """
    Report that will execute multiple report definitions.
    """
    report_type = 'multi_report'

    def __init__(self, name, **kwargs):
        super(MultiReport, self).__init__(name)
        self.kwargs = kwargs

    def __call__(self):
        return generate_multi_report(self.name, None, self.kwargs)


def generate_multi_report(name, description, definition):
    report_definitions = definition.get('reports', [])
    reports = []

    for report in report_definitions:
        _report = build_report(report)
        if _report:
            reports.append(_report)

    report_results = []
    for report in reports:
        report_results.append(report())

    return generate_results_package(name, 'multi_report', description, reports=report_results)


register_plugin(MultiReport)
