from setuptools import setup, find_packages

setup(
    name="pyAvaCore",
    description="Library to download and parse EAWS avalanche bulletins",
    version="0.0.0",
    url="https://gitlab.com/albina-euregio/pyAvaCore",
    license="GPL",
    author="Friedrich Mütschele",
    packages=find_packages(exclude=["tests"]),
)
