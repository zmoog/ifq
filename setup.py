# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  # noqa: H301

with open("README.md") as f:
    long_description = f.read()

NAME = "ifq"
REQUIRES = ["lxml >= 4.5.0", "requests >= 2.22.0"]

setup(
    name=NAME,
    version="0.1.",
    description="Library to download IFQ issues",
    author_email="maurizio.branca@gmail.com",
    url="https://github.com/zmoog/ifq",
    keywords=[],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
