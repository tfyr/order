import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='order',
    version='0.1.1.3',
    packages=['order'],
    include_package_data=True,
    license='',  # example license
    description='',
    long_description=README,
    url='',
    author='Nail Sharipov',
    author_email='nash34@gmail.com',
    classifiers=[
    ],
)
