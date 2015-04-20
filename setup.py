from setuptools import setup

setup(
    name='forestcost',
    version='0.1',
    author="Ulric Stroetz",
    author_email="ustroetz@gmail.com",
    packages=['python-osrm'],
    install_requires=[
      'requests',
      'polyline'],
      )
