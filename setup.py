from setuptools import setup, find_packages
import sys, os

__version__ = '0.2'

setup(
    name='yourtopia',
    version=__version__,
    description='YourTopia',
    long_description='',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Open Knowledge Foundation',
    author_email='',
    url='http://openhdi.org/',
    license='mit',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False
)
