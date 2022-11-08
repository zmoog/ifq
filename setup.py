from setuptools import setup
import os

VERSION = "0.3.0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="ifq",
    description="Library to download www.ilfattoquotidiano.it issues in PDF",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Maurizio Branca",
    url="https://github.com/zmoog/ifq",
    project_urls={
        "Issues": "https://github.com/zmoog/ifq/issues",
        "CI": "https://github.com/zmoog/ifq/actions",
        "Changelog": "https://github.com/zmoog/ifq/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["ifq"],
    entry_points="""
        [console_scripts]
    """,
    install_requires=[
        "lxml >= 4.9.1",
        "requests >= 2.28.1",
    ],
    extras_require={
        "test": [
            "pytest",
            "safety",
            "wheel >= 0.38.3",
        ],
    },
    python_requires=">=3.7",
)
