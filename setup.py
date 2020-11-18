""" Setup file. """

from setuptools import find_packages, setup

with open("README.md", "r") as r:
    README = r.read()

setup(
    name="dogma",
    version="0.0.1",
    description="A heliocentric social deduction game",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/daffidwilde/dogma",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    tests_require=["hypothesis", "pytest", "pytest-cov"],
)
