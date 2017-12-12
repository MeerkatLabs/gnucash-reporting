from setuptools import setup, find_packages

setup(
    name='gnucash-reports',
    version='0.2.0.dev',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='Generate JSON reports for rendering in a viewer.',
    install_requires=['numpy==1.9.3',
                      'dateutils==0.6.6',
                      'simplejson==3.8.0',
                      'pyaml==15.8.2',
                      'piecash==0.13.0',
                      'enum34==1.1.6',
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
