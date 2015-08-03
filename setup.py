from setuptools import setup

setup(
    name='osrm',
    version='0.11',
    author="Ulric Stroetz, mthh",
    author_email="ustroetz@gmail.com",
    package_dir={'': 'src'},
    packages=['osrm'],
    install_requires=[
      'requests',
      'polyline',
      'GDAL',
      'numpy',
      'pandas']
      )
