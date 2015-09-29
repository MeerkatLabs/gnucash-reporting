"""
Definition of a report.
"""
reports = dict()


def register_plugin(report):
    global reports
    reports[report.report_type] = report


def get_report(report_type):
    return reports.get(report_type, None)


class Report(object):

    report_type = 'unknown'

    def __init__(self, name):
        self.name = name

    def _generate_result(self):
        return dict(name=self.name, type=self.report_type, data=dict())
