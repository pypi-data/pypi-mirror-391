###############################################################################
# This file is part of the lib-maxiv-loopfinder project.
#
# Copyright Lund University
#
# Distributed under the GNU GPLv3 license. See LICENSE file for more info.
###############################################################################

from setuptools import setup, find_packages


setup(
    name="loopfinder",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="A library for loop centring in MX crystallography",
    author="KITS",
    author_email="isak.lindhe@maxiv.lu.se",
    license="GPL-3.0-or-later",
    url="https://gitlab.maxiv.lu.se/kits-maxiv/lib-maxiv-loopfinder",
    packages=find_packages(exclude=("tests", "tests.*")),
    python_requires=">=3.10",
    install_requires=["opencv-python-headless", "numpy"],
    extras_require={
        "tests": ["pytest", "pytest-cov"],
    },
)
