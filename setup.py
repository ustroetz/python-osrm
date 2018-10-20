from setuptools import setup
#from osrm import __version__


with open("requirements.txt") as f:
    requirements = f.read().split('\n')

setup(
    author="Ulric Stroetz, mthh",
    author_email="ustroetz@gmail.com",
    description="A Python wrapper around the OSRM API"
    install_requires=requirements
    name='osrm',
    packages=['osrm'],
    test_suite="tests",
    version='0.11.2',
)
