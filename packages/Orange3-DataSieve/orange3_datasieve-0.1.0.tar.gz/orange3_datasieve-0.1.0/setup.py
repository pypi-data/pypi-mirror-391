#!/usr/bin/env python

from os import path
from setuptools import setup, find_packages

# ----------------------------
# Basic package information
# ----------------------------
NAME = "Orange3-DataSieve"
VERSION = "0.1.0"
AUTHOR = "EL_MEHDI_BEN_RABIAA"
AUTHOR_EMAIL = "todds496@gmail.com"
URL = ""
DESCRIPTION = "This add-on includes a suite of widgets designed to extract and parse data from PDFs. It also offers advanced data cleaning features, including regex-based processing, string manipulation, and more. For collaboration or inquiries, contact Mehdi Benrabiaa at Todds496@gmail.com"
LICENSE = "BSD"

# ----------------------------
# Read long description safely
# ----------------------------
here = path.abspath(path.dirname(__file__))
try:
    with open(path.join(here, "README.pypi"), encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# ----------------------------
# Package configuration
# ----------------------------
PACKAGES = find_packages()

PACKAGE_DATA = {
    "orangecontrib.custom": ["tutorials/*.ows"],
    "orangecontrib.custom.widgets": ["icons/*"],
}

INSTALL_REQUIRES = [
    # "Orange3>=3.30",
    "PyQtWebEngine",
    "pypdfium2==5.0.0",
    "PyQtWebEngine==5.15.7",
    "PyQtWebEngine-Qt5==5.15.2",
    "camelot-py==1.0.9",
]

ENTRY_POINTS = {
    "orange3.addon": ("custom = orangecontrib.custom",),
    "orange.widgets.tutorials": ("customtutorials = orangecontrib.custom.tutorials",),
    "orange.widgets": ("Orange3-DataSieve = orangecontrib.custom.widgets",),
    "orange.canvas.help": (
        "html-index = orangecontrib.custom.widgets:WIDGET_HELP_PATH",
    ),
}

# ----------------------------
# Setup call
# ----------------------------
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    keywords=("orange3 add-on",),
    zip_safe=False,
    include_package_data=True,  # <== critical
)
