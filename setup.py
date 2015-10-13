from distutils.core import setup

setup(
    name='gnucash-reports',
    version='',
    packages=['gnu_reporting',
              'gnu_reporting.collate', 'gnu_reporting.reports', 'gnu_reporting.reports.credit',
              'gnu_reporting.configuration'],
    url='',
    license='MIT',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='Generate JSON reports for rendering in a viewer.',
    scripts=['bin/gnucash_reports'],
    install_requires=['numpy==1.9.3',
                      'dateutils==0.6.6',
                      'simplejson==3.8.0',
                      'pyaml==15.8.2']
)
