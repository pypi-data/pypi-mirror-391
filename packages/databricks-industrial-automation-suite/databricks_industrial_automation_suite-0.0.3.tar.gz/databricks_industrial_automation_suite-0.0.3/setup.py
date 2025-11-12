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
    'version': '0.0.3',
    'description': 'A comprehensive library designed to support all major industrial automation protocols within the Databricks ecosystem.',
    'long_description': '# Databricks Industrial Automation Suite (Databricks Free Edition Hackathon)\n\n## Overview\n\nThe **Databricks Industrial Automation Suite** is a comprehensive library designed to support all major industrial automation protocols within the Databricks ecosystem. It enables seamless integration, data exchange, and control across diverse industrial systems, helping enterprises unify and modernize their operational technology (OT) and IT workflows.\n\n---\n\n## Supported Protocols\n\n| Protocol                    | Status        |\n| --------------------------- | ------------- |\n| OPC UA                      | ✅ Supported   |\n| Matter                      | ⬜ Planned     |\n| Modbus TCP                  | ⬜ In Progress |\n| HART Communication Protocol | ⬜ Planned     |\n| MQTT                        | ⬜ Planned     |\n\n---\n\n## Getting Started\n\n### Installation (User Mode)\n\nTo install the published package:\n\n```bash\n%pip install databricks-industrial-automation-suite\n```\n\n---\n\n## Development Setup (Build & Install Locally)\n\nIf you want to **develop**, **test**, or **contribute** to the project locally, follow these steps:\n\n### Clone the repository\n\n```bash\ngit clone https://github.com/yourusername/databricks-industrial-automation-suite.git\ncd databricks-industrial-automation-suite\n```\n\n---\n\n### Install dependencies using Poetry\n\nIf you use **Poetry** (recommended):\n\n```bash\npoetry install\n```\n\nThis creates a virtual environment and installs all dependencies automatically.\n\nTo enter that environment:\n\n```bash\npoetry shell\n```\n\n---\n\n### Build the package\n\n```bash\npoetry build\n```\n\nThis generates distributable files under `dist/`:\n\n```\ndist/\n ├── databricks_industrial_automation_suite-0.1.0.tar.gz\n └── databricks_industrial_automation_suite-0.1.0-py3-none-any.whl\n```\n\n---\n\n### Install the built package locally\n\nOption 1 — Install from wheel:\n\n```bash\npip install dist/databricks_industrial_automation_suite-0.1.0-py3-none-any.whl\n```\n\nOption 2 — Editable install for live code updates:\n\n```bash\npip install -e .\n```\n\n---\n\n### Test the installation\n\nTry importing the library or running example scripts:\n\n```bash\npython\n>>> from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient\n>>> print("Library loaded successfully!")\n```\n\nOr execute one of the included examples:\n\n```bash\npython examples/browse_child_nodes.py\n```\n\n---\n\n### Rebuild cleanly (optional)\n\nIf you need a fresh build:\n\n```bash\nrm -rf dist build *.egg-info\npoetry build\n```\n\n---\n\n### (Optional) Local virtual environment test\n\nYou can also test the install in a clean environment:\n\n```bash\npython3 -m venv .venv\nsource .venv/bin/activate\npip install dist/*.whl\n```\n\n---\n\n## Usage Highlights\n\n* Native OPC UA client connection support (streaming, browsing, and security).\n* Modular, extensible architecture for upcoming industrial protocols.\n* Designed for scalability, observability, and Databricks integration.\n\n---\n\n## Contribution\n\nThis suite is under active development.\nWe welcome contributions of:\n\n* New protocol integrations\n* Documentation improvements\n* Bug fixes or performance enhancements\n\nPlease open issues or pull requests on the GitHub repository.\n\n---\n\n## Additional Resources\n\n* **Certificate Management:** Use tools like [XCA](https://hohnstaedt.de/xca/) to manage secure client certificates.\n* **Testing:** You can run an OPC UA demo server locally via Docker:\n\n  ```bash\n  docker run -d -p 4840:4840 ghcr.io/falk-werner/opcua-server:latest\n  ```',
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
