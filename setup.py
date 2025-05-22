from setuptools import setup, find_packages

setup(
    name="cardo-python-utils",
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True
)
