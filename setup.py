from setuptools import setup

setup(
    name='osrm',
    version='0.1',
    author="Ulric Stroetz",
    author_email="ustroetz@gmail.com",
    package_dir={'': 'src'},
    packages=['osrm'],
    install_requires=[
      'requests',
      'polyline'],
      )
