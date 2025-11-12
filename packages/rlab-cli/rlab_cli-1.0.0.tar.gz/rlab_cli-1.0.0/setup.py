#!/usr/bin/env python3
"""
RLab CLI Setup Script (for backward compatibility)
"""

from setuptools import setup, find_packages

setup(
    name="rlab-cli",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)