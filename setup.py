#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pydbisam",
    version="0.1.0",
    description="Read DBISAM database tables.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aaron Linville",
    author_email="aaron@linville.org",
    url="https://github.com/linville/pydbisam",
    py_modules=["pydbisam"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
    license="ISC",
    python_requires=">=3.7",
    setup_requires=["wheel"],
    entry_points={"console_scripts": ["pydbisam=cli:main"]},
)
