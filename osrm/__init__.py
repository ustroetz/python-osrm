# -*- coding: utf-8 -*-
__version__ = '0.11-m'
"""
Python wrapper for osrm API v5
------------------------------
Wrap OSRM services 'route', 'nearest', 'table', 'match' and 'trip'.
Allow geometry decoding for 'viaroute', 'match' and 'trip' functions.
"""

from osrm.core import match, simple_route, nearest, table, trip
from osrm.extra import access_isocrone