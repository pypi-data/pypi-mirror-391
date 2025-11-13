import io
import re

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("flask/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = \'(.*?)\'", f.read()).group(1)

setup(
    name="Flask-v1.0",
    version=version,
    url="https://github.com/nottrobin/flask-v1.0",
    project_urls={
        "Documentation": "https://github.com/nottrobin/flask-v1.0/blob/main/README.md",
        "Code": "https://github.com/nottrobin/flask-v1.0"
    },
    license="BSD-3-Clause",
    author="Robin Winslow Morris",
    author_email="robin@robinwinslow.co.uk",
    description="A simple framework for building complex web applications.",
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        'Werkzeug>=0.14, <3',
        'Jinja2 >= 2.4, < 3.1',
        'itsdangerous >= 0.21, < 2.1',
        'click>=2.0',
    ],
    entry_points={"console_scripts": ["flask = flask.cli:main"]},
)
