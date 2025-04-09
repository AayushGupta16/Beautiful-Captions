from setuptools import setup, find_packages

setup(
    name="beautiful-captions",
    version="0.1.58",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "beautiful_captions": ["**/*.py", "fonts/*", "**/*.ttf"],
    },
    python_requires=">=3.8",
) 