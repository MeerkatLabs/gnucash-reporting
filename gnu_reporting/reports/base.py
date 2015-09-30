"""
Definition of a report.
"""
reports = dict()


def register_plugin(report):
    global reports
    reports[report.report_type] = report


def get_report(_report_type):
    report_type = reports.get(_report_type, None)
    if not report_type:
        raise AttributeError('Unknown report type: %s' % _report_type)

    return report_type


class Report(object):

    report_type = 'unknown'

    def __init__(self, name):
        self.name = name

    def _generate_result(self):
        return dict(name=self.name, type=self.report_type, data=dict())


class MultiReport(Report):

    report_type = 'multi_report'

    def __init__(self, name, reports):
        super(MultiReport, self).__init__(name)
        self._reports = []

        for report in reports:
            name = report.get('name', 'Unnamed Report')
            report_type = report.get('type', 'UNDEFINED_REPORT')
            definition = report.get('definition', dict())

            print '  Running: %s' % name

            report_class = get_report(report_type)
            if report:
                _report = report_class(name, **definition)
                self._reports.append(_report)

    def __call__(self):

        result = self._generate_result()
        result['data']['reports'] = []

        for report in self._reports:
            result['data']['reports'].append(report())

        return result


register_plugin(MultiReport)
