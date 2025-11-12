# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['databricks_industrial_automation_suite',
 'databricks_industrial_automation_suite.certificate_management',
 'databricks_industrial_automation_suite.integrations',
 'databricks_industrial_automation_suite.models',
 'databricks_industrial_automation_suite.utils']

package_data = \
{'': ['*']}

install_requires = \
['asyncio',
 'asyncua',
 'cryptography',
 'lxml',
 'python-dateutil',
 'pytz',
 'tabulate']

setup_kwargs = {
    'name': 'databricks-industrial-automation-suite',
    'version': '0.0.2',
    'description': 'A comprehensive library designed to support all major industrial automation protocols within the Databricks ecosystem.',
    'long_description': 'None',
    'author': 'Irfan Ghat',
    'author_email': 'irfanghat@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
