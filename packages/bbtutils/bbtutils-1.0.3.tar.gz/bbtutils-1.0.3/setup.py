# setup.py

from setuptools import find_packages, setup

setup(
    name='bbtutils',
    version='1.0.3',
    packages = find_packages(exclude=['tests']),
    install_requires=[
        "cachetools", "requests",
        "pytz",
    ],
    author='bbt',
    author_email='bbt@example.com',
    description='private uitls', 
)

