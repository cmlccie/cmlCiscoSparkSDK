"""@cmlccie Cisco Spark Python SDK."""

from datetime import datetime
import json

import pytz
import requests

from jsondata import JSONData, JSONProp
from restapi import RESTfulAPI
from roproperties import ROProperty


# Module constants
DEFAULT_API_URL = 'https://api.ciscospark.com/v1/'
PEOPLE_URL = 'people'
ROOMS_URL = 'rooms'
MEMBERSHIPS_URL = 'memberships'
MESSAGES_URL = 'messages'
WEBHOOKS_URL = 'webhooks'


# Helper functions
def _spark_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')\
                    .replace(tzinfo=pytz.utc)


# Helper classes
class ROSparkDateTime(JSONProp):
    def __set__(self, instance, value):
        dt = _spark_datetime(value)
        super(ROSparkDateTime, self).__set__(instance, dt)


# Module exceptions
class CMLSparkException(Exception):
    pass


class CiscoSparkException(CMLSparkException):
    # TODO: Map Cisco Spark response codes to descriptive errors
    pass


# Cisco Spark API methods container class
class CiscoSparkAPI(RESTfulAPI):
    authentication_token = ROProperty()

    def __init__(self, authentication_token, api_url=DEFAULT_API_URL,
                 timeout=None):
        super(CiscoSparkAPI, self).__init__(api_url)
        self.authentication_token = authentication_token
        self.request_args['timeout'] = timeout
        self.request_args['headers'] = {
            'Authorization': "Bearer " + self.authentication_token}

    def delete(self, url, **request_args):
        response = super(CiscoSparkAPI, self).delete(url, **request_args)
        if response.status_code != 204:
            response.raise_for_status()

    def get_json(self, url, params=None):
        response = self.get(url, params=params)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            json_data = response.json()
            return json_data

    def get_json_items(self, url, params=None):
        responses = self.get_iter(url, params=params)
        for response in responses:
            items = []
            if response.status_code != 200:
                response.raise_for_status()
            else:
                json_data = response.json()
                if json_data.get('items'):
                    items = json_data.get('items')
                else:
                    raise CMLSparkException("'items' object not found in JSON"
                                            "data: %r" % json_data)
            if items:
                for item in items:
                    yield item
            else:
                raise StopIteration

    def post_json(self, url, json_data):
        response = self.post(url, json=json_data)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            return response.json()

    def put_json(self, url, json_data):
        response = self.put(url, json=json_data)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            return response.json()

    def get_people(self, email=None, displayName=None, max=None):
        params = {}
        if email:
            params['email'] = email
        elif displayName:
            params['displayName'] = displayName
        else:
            raise CMLSparkException
        if max:
            params['max'] = max
        people_items = self.get_json_items(PEOPLE_URL, params=params)
        for item in people_items:
            yield Person(item)

    def get_person(self, id):
        json_data = self.get_json(PEOPLE_URL + '/' + id)
        return Person(json_data)

    def get_person_me(self):
        json_data = self.get_json(PEOPLE_URL + '/me')
        return Person(json_data)

    def get_rooms(self, showSipAddress=False, max=None):
        params = {'showSipAddress': showSipAddress}
        if max:
            params['max'] = max
        room_items = self.get_json_items(ROOMS_URL, params=params)
        for item in room_items:
            yield Room(item)

    def create_room(self, title):
        json_data = {'title': title}
        room_item = self.post_json(ROOMS_URL, json_data)
        return Room(room_item)

    def get_room(self, id, showSipAddress=False):
        params = {'showSipAddress': showSipAddress}
        json_data = self.get_json(ROOMS_URL+'/'+id, params)
        return Room(json_data)

    def update_room(self, id, **kwargs):
        assert kwargs and isinstance(kwargs, dict)
        json_data = kwargs
        room_item = self.put_json(ROOMS_URL+'/'+id, json_data)
        return Room(room_item)

    def delete_room(self, id):
        self.delete(ROOMS_URL+'/'+id)

    def get_memberships(self, roomId, personId=None, personEmail=None,
                        max=None):
        params = {'roomId': roomId}
        if personId:
            params['personId'] = personId
        elif personEmail:
            params['personEmail'] = personEmail
        if max:
            params['max'] = max
        membership_items = self.get_json_items(MEMBERSHIPS_URL, params)
        for item in membership_items:
            yield Membership(item)

    def create_membership(self, roomId, personId=None, personEmail=None,
                          isModerator=False):
        json_data = {'roomId': roomId, 'isModerator': isModerator}
        if personId:
            json_data['personId'] = personId
        elif personEmail:
            json_data['personEmail'] = personEmail
        else:
            raise CMLSparkException
        membership_item = self.post_json(MEMBERSHIPS_URL, json_data)
        return Membership(membership_item)

    def get_membership(self, id):
        json_data = self.get_json(MEMBERSHIPS_URL+'/'+id)
        return Membership(json_data)

    def update_membership(self, id, **kwargs):
        assert kwargs and isinstance(kwargs, dict)
        json_data = kwargs
        membership_item = self.put_json(MEMBERSHIPS_URL+'/'+id, json_data)
        return Membership(membership_item)

    def delete_membership(self, id):
        self.delete(MEMBERSHIPS_URL+'/'+id)

    def get_messages(self, roomId, before=None, beforeMessage=None, max=None):
        params = {'roomId': roomId}
        if before:
            params['before'] = before
        if beforeMessage:
            params['beforeMessage'] = beforeMessage
        if max:
            params['max'] = max
        message_items = self.get_json_items(MESSAGES_URL, params)
        for item in message_items:
            return Message(item)

    def create_message(self, roomId=None, text=None, files=None,
                       toPersonId=None, toPersonEmail=None):
        json_data = {}
        if roomId:
            json_data['roomId'] = roomId
        elif toPersonId:
            json_data['toPersonId'] = toPersonId
        elif toPersonEmail:
            json_data['toPersonEmail'] = toPersonEmail
        else:
            raise CMLSparkException
        if not text and not files:
            raise CMLSparkException
        if text:
            json_data['text'] = text
        if files:
            json_data['files'] = files
        message_item = self.post_json(MESSAGES_URL, json_data)
        return Message(message_item)

    def get_message(self, id):
        json_data = self.get_json(MESSAGES_URL+'/'+id)
        return Message(json_data)

    def delete_message(self, id):
        self.delete(MESSAGES_URL+'/'+id)

    def get_webhooks(self, max=None):
        params = {}
        if max:
            params['max'] = max
        webhook_items = self.get_json_items(WEBHOOKS_URL, params)
        for item in webhook_items:
            yield Membership(item)

    def create_webhook(self, name, targetUrl, resource, event, filter):
        json_data = {'name': name,
                     'targetUrl': targetUrl,
                     'resource': resource,
                     'event': event,
                     'filter': filter}
        webhook_item = self.post_json(WEBHOOKS_URL, json_data)
        return Webhook(webhook_item)

    def get_webhook(self, id):
        webhook_item = self.get_json(WEBHOOKS_URL+'/'+id)
        return Webhook(webhook_item)

    def update_webhook(self, id, **kwargs):
        assert kwargs and isinstance(kwargs, dict)
        json_data = kwargs
        webhook_item = self.put_json(WEBHOOKS_URL+'/'+id, json_data)
        return Webhook(webhook_item)

    def delete_webhook(self, id):
        self.delete(WEBHOOKS_URL+'/'+id)


# Cisco Spark data objects
class Room(JSONData):
    id = JSONProp()
    title = JSONProp()
    created = ROSparkDateTime()
    lastActivity = ROSparkDateTime()

    def __init__(self, json_data):
        super(Room, self).__init__(json_data)


class Person(JSONData):
    id = JSONProp()
    emails = JSONProp()
    displayName = JSONProp()
    avatar = JSONProp()
    created = ROSparkDateTime()

    def __init__(self, json_data):
        if isinstance(json_data, basestring):
            json_data = json.dumps(json_data)
        self.id = json_data[u'id']
        self.emails = json_data[u'emails']
        self.displayName = json_data[u'displayName']
        self.avatar = json_data[u'avatar']
        self.created = json_data[u'created']
        super(Person, self).__init__(json_data)


class Membership(JSONData):
    id = JSONProp()

    def __init__(self, json_data):
        if isinstance(json_data, basestring):
            json_data = json.dumps(json_data)
        self.id = json_data[u'id']
        super(Membership, self).__init__(json_data)


class Message(JSONData):
    id = JSONProp()

    def __init__(self, json_data):
        if isinstance(json_data, basestring):
            json_data = json.dumps(json_data)
        self.id = json_data[u'id']
        super(Message, self).__init__(json_data)


class Webhook(JSONData):
    id = JSONProp()

    def __init__(self, json_data):
        if isinstance(json_data, basestring):
            json_data = json.dumps(json_data)
        self.id = json_data[u'id']
        super(Webhook, self).__init__(json_data)
