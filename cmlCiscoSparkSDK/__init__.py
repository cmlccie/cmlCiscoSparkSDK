"""Pythonic classes and methods for working with the Cisco Spark service."""


from sparkapi import CiscoSparkAPI, Room, Person, Membership, Message, Webhook
from jsondata import JSONData, READ_ONLY, READ_WRITE


__author__ = 'Chris Lunsford <chrlunsf@cisco.com>'
__version__ = '1.0.3'
__all__ = ['CiscoSparkAPI', 'Room', 'Person', 'Membership', 'Message',
           'Webhook', 'JSONData', 'READ_ONLY', 'READ_WRITE']
