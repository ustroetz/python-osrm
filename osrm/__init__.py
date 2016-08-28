# -*- coding: utf-8 -*-
"""
Python wrapper for osrm API v5
------------------------------
Wrap OSRM services 'route', 'nearest', 'table', 'match' and 'trip'.
Allow geometry decoding for 'viaroute', 'match' and 'trip' functions.
"""
from collections import namedtuple


__version__ = '0.11.1'


class DefaultRequestConfig:
    def __init__(self):
        self.host = "http://localhost:5000"
        self.profile = "driving"
        self.version = "v1"

    def __str__(self):
        return("/".join([self.host, '*', self.version, self.profile]))

    def __repr__(self):
        return("/".join([self.host, '*', self.version, self.profile]))

    @staticmethod
    def __call__(addr=None):
        if not addr:
            return DefaultRequestConfig()
        else:
            tmp = addr.split('/')
            cla = DefaultRequestConfig()
            cla.host = tmp[0]
            i = len(tmp)
            cla.version = tmp[i-2]
            cla.profile = tmp[i-1]
            return cla

RequestConfig = DefaultRequestConfig()

Point = namedtuple("Point", ("latitude", "longitude"))

from .core import match, simple_route, nearest, table, trip, _chain
from .extra import AccessIsochrone
