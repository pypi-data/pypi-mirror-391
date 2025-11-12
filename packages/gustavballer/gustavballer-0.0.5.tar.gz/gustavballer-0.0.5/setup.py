#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package metadata
NAME = "gustavballer"
DESCRIPTION = "Gustav Baller's Python Web Framework built for learning purposes."
EMAIL = "markdavidsanders@gmail.com"
AUTHOR = "Mark Sanders"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "0.0.5"


# Required packages
REQUIRED = [
    "Jinja2==2.10.3",
    "parse==1.12.1",
    "requests==2.22.0",
    "requests-wsgi-adapter==0.4.1",
    "WebOb==1.8.5",
    "whitenoise==4.1.4"
]

# Here we are
here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long description
# NOTE: This will only work if README.md is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load __version__.py as a dictionary
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

# This is the best part
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["test_*"]),
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.6"
    ],
    setup_requires=["wheel"]
)
