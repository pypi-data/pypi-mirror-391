"""
Setup script for pensity package
"""
from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    package_data={
        'pensity': ['common-endpoints.txt'],
    },
    include_package_data=True,
)
