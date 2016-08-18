from setuptools import setup
#from osrm import __version__

setup(
    name='osrm',
    version='0.11.1',
    author="Ulric Stroetz, mthh",
    author_email="ustroetz@gmail.com",
    packages=['osrm'],
    test_suite="tests",
    install_requires=[
        'polyline',
        'GDAL',
        'numpy',
        'pandas',
        'geopandas',
        'matplotlib',
        'shapely']
    )
