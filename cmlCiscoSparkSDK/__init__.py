"""Pythonic classes and methods for working with the Cisco Spark service."""
from __future__ import absolute_import

from ._version import get_versions

from .sparkapi import CiscoSparkAPI, Room, Person, Membership, Message, Webhook
from .jsondata import JSONData, READ_ONLY, READ_WRITE


__author__ = 'Chris Lunsford <chrlunsf@cisco.com>'
__all__ = ['CiscoSparkAPI', 'Room', 'Person', 'Membership', 'Message',
           'Webhook', 'JSONData', 'READ_ONLY', 'READ_WRITE']

__version__ = get_versions()['version']
del get_versions
