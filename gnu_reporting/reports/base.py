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
