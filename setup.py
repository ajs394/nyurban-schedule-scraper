from setuptools import setup, find_packages

setup(
    name='nyurban-schedule-scraper',
    version='1.02-SNAPSHOT',
    description='Web Scraper',
    #scripts =['ov_examples/*.py'],
    #packages=['ov_apis', 'ov_client', 'ov_util', 'ov_cail', 'ov_test', 'ov_examples'],
    packages = find_packages(exclude=[]),
    #install_requires=['openpyxl==2.4.8', 'pandas==0.23.4', 'xlrd==1.1.0', 'requests==2.18.3', 'nose==1.3.7', 'nose_htmloutput==0.6.0'],
    #'nose==1.3.7', 'nose_htmloutput==0.6.0' only for tests
    #'locustio==0.8.1' only for loadtest. brings others like greenlet, gevent
    #'Flask==1.0.2' for running REST server
    #'Flask-Cors==3.0.4' for REST server with Oneview GUI
    include_package_data = True
)
