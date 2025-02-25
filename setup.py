from setuptools import setup, find_packages

setup(
    name="beautiful-captions",
    version="0.1.4",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.8",
) 