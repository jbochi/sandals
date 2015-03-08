from os.path import dirname, abspath, join, exists
from setuptools import setup

long_description = None
if exists("README.rst"):
    long_description = open("README.rst").read()

install_reqs = [req for req in open(abspath(join(dirname(__file__), 'requirements.txt')))]

setup(
    name="sandals",
    author='Juarez Bochi',
    author_email='jbochi@gmail.com',
    version="0.0.1",
    zip_safe=False,
    include_package_data=True,
    install_requires=install_reqs,
    packages=["sandals"],
    url="https://github.com/jbochi/sandals",
    description="Sandals = SQL + Pandas",
    long_description=long_description)
