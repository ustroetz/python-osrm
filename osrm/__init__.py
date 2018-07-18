# -*- coding: utf-8 -*-
"""
Python wrapper for osrm API v5
------------------------------
Wrap OSRM services 'route', 'nearest', 'table', 'match' and 'trip'.
Allow geometry decoding for 'viaroute', 'match' and 'trip' functions.
"""
from collections import namedtuple
import base64
import sys

__version__ = '0.11.1'


class DefaultRequestConfig:
    def __init__(self):
        self.host = "http://localhost:5000"
        self.profile = "driving"
        self.version = "v1"
        self.auth = None

    def __str__(self):
        return("/".join([self.host, '*', self.version, self.profile]))

    def __repr__(self):
        return("/".join([self.host, '*', self.version, self.profile]))

    @staticmethod
    def __call__(addr=None, basic_auth=None):
        cla = DefaultRequestConfig()

        if addr:
            tmp = addr.split('/')
            cla.host = tmp[0]
            i = len(tmp)
            cla.version = tmp[i-2]
            cla.profile = tmp[i-1]

        if basic_auth:
            user, password = basic_auth

            encoded = '{}:{}'.format(user, password)
            encoded = encoded.encode('utf8') if sys.version_info[0] >= 3 else encoded
            encoded = base64.b64encode(encoded).decode('utf8')
            cla.auth = 'Basic {}'.format(encoded)

        return cla

RequestConfig = DefaultRequestConfig()

Point = namedtuple("Point", ("longitude", "latitude"))

from .core import match, simple_route, nearest, table, trip, _chain
from .extra import AccessIsochrone
