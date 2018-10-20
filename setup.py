from setuptools import setup
#from osrm import __version__


with open("requirements.txt") as f:
    requirements = f.read().split('\n')

setup(
    name='osrm',
    version='0.11.2',
    author="Ulric Stroetz, mthh",
    author_email="ustroetz@gmail.com",
    packages=['osrm'],
    test_suite="tests",
    install_requires=requirements
)
