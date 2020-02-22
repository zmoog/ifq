# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  # noqa: H301

with open("README.md") as f:
    long_description = f.read()

NAME = "ifq"
REQUIRES = ["lxml >= 4.5.0", "requests >= 2.23.0"]

setup(
    name=NAME,
    version="0.2.0",
    description="library to download www.ilfattoquotidiano.it issues in PDF",
    author_email="maurizio.branca@gmail.com",
    url="https://github.com/zmoog/ifq",
    keywords=[],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    classifiers=[  # https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
