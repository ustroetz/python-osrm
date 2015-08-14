from setuptools import setup
import osrm

setup(
    name='osrm',
    version=osrm.__version__,
    author="Ulric Stroetz, mthh",
    author_email="ustroetz@gmail.com",
    packages=['osrm'],
    install_requires=[
        'requests',
        'polyline',
        'GDAL',
        'numpy',
        'pandas']
    )
