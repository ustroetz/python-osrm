from setuptools import setup
#from osrm import __version__


with open("requirements.txt") as f:
    requirements = f.read().split('\n')

setup(
    author_email="ustroetz@gmail.com",
    author="Ulric Stroetz, mthh",
    description="A Python wrapper around the OSRM API",
    install_requires=requirements,
    name='osrm',
    packages=['osrm'],
    test_suite="tests",
    url="https://github.com/ustroetz/python-osrm",
    version='0.11.3'
)
