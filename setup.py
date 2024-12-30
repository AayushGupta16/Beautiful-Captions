from setuptools import setup, find_packages

setup(
    name="beautiful-captions",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
) 