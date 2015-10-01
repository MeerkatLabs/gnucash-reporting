#!/usr/bin/env python
"""
This is the main execution program for the reporting library.
"""
import argparse
import sys
import os
import simplejson as json
import glob
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.getcwd()))

from gnu_reporting.wrapper import initialize
from gnu_reporting.reports import register_core_reports, get_report

register_core_reports()

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', dest='configuration', default='core.json',
                    help='core configuration details of the application')

args = parser.parse_args()

with open(args.configuration) as file_pointer:
    configuration = json.load(file_pointer)

    session = initialize(configuration['gnucash_file'], configuration.get('account_with_currency', None))
    output_location = configuration.get('output_directory', 'output')
    report_location = configuration.get('report_definitions', 'reports')


if not os.path.exists(output_location):
    os.makedirs(output_location)

all_reports = []

reports_list = glob.glob(os.path.join(report_location, '*.json'))
for infile in sorted(reports_list):

    try:
        print 'Processing: %s' % infile
        with open(infile) as report_configuration_file:
            report_configuration = json.load(report_configuration_file)

            result_definition = dict(name=report_configuration.get('page_name', 'Unnamed Page'),
                                     reports=[])

            for report_definition in report_configuration['definitions']:

                name = report_definition.get('name', 'Unnamed Report')
                report_type = report_definition.get('type', 'UNDEFINED_REPORT')
                definition = report_definition.get('definition', dict())

                print '  Running: %s' % name

                report = get_report(report_type)
                if report:
                    _report = report(name, **definition)
                    payload = _report()

                    result_definition['reports'].append(payload)

            output_file_name = os.path.split(infile)[-1]

            with open(os.path.join(output_location, output_file_name), 'w') as output_file:
                json.dump(result_definition, output_file)
                all_reports.append(dict(name=result_definition.get('name'), file=output_file_name))

    except Exception as e:
        print 'Exception caught: %s' % e

with open(os.path.join(output_location, '__reports.json'), 'w') as all_report_file:
    json.dump(all_reports, all_report_file)

session.end()
