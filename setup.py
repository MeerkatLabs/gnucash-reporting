from setuptools import setup, find_packages

setup(
    name='gnucash-reports',
    version='',
    packages=find_packages(),
    url='',
    license='BSD-3-Clause',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='Generate JSON reports for rendering in a viewer.',
    install_requires=['numpy==1.9.3',
                      'dateutils==0.6.6',
                      'simplejson==3.8.0',
                      'pyaml==15.8.2'],
    entry_points={
        'console_scripts': [
            'gnucash_reports=gnucash_reports.commands.gnucash_reports:main'
        ],
        'gnucash_reports_reports': [
            'core_reports=gnucash_reports.configuration.register_core:register_core_reports'
        ],
        'gnucash_reports_configuration': [
            'core_configuration=gnucash_reports.configuration.register_core:register_core_configuration_plugins'
        ]
    }
)
