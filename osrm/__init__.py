# -*- coding: utf-8 -*-
__version__ = '0.11'
"""
Python wrapper for osrm API
---------------------------
Wrap OSRM functions 'match', 'locate', 'nearest', 'table' and partially
'viaroute'.
Allow calculation of time matrix between differents origin-destination
using OSRM 'table' function.
Allow geometry decoding for 'viaroute' and 'match' functions.
"""

from osrm.core import (
    match, simple_viaroute, locate, nearest, table, table_OD, get_error_id,
    light_table
    )
