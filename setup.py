from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='gnucash-reports',
    version='0.2.0',
    packages=find_packages(),
    url='https://github.com/MeerkatLabs/gnucash-reports',
    license='MIT',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='Generate JSON reports for rendering in a viewer.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['dateutils==0.6.6',
                      'simplejson==3.8.0',
                      'pyaml==15.8.2',
                      'piecash==0.13.0',
                      'enum34==1.1.6',
                      'requests==2.18.4'
                      ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial',
    ],
    entry_points={
        'console_scripts': [
            'gnucash_reports=gnucash_reports.commands.reports:main',
            'gnucash_update_prices=gnucash_reports.commands.update_prices:main',
        ],
        'gnucash_reports_reports': [
            'core_reports=gnucash_reports.configuration.register_core:register_core_reports'
        ],
        'gnucash_reports_configuration': [
            'core_configuration=gnucash_reports.configuration.register_core:register_core_configuration_plugins'
        ]
    }
)
