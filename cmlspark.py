"""@cmlccie Cisco Spark Python SDK."""

from datetime import datetime

import pytz
import requests

from jsondata import JSONDataObj
from roproperties import ROProperty


# Module constants
DEFAULT_API_URL = 'https://api.ciscospark.com/v1'
PEOPLE_API = '/people'
ROOMS_API = '/rooms'
MEMBERSHIPS_API = '/memberships'
MESSAGES_API = '/messages'
WEBHOOKS_API = '/webhooks'


# Helper functions
def _spark_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')\
                    .replace(tzinfo=pytz.utc)


# Helper classes
class RODateTime(ROProperty):
    def __set__(self, instance, value):
        dt = _spark_datetime(value)
        super(RODateTime, self).__set__(instance, dt)


# Module exceptions
class CMLSparkException(Exception):
    pass


class CiscoSparkException(CMLSparkException):
    # TODO: Map Cisco Spark response codes to descriptive errors
    pass


# Cisco Spark API methods container class
class CiscoSparkAPI(object):
    content_type = 'application/json'

    def __init__(self, authentication_token, url=DEFAULT_API_URL,
                 timeout=None):
        self.at = authentication_token
        self.url = url
        self.people_url = url + PEOPLE_API
        self.rooms_url = url + ROOMS_API
        self.memberships_url = url + MEMBERSHIPS_API
        self.messages_url = url + MESSAGES_API
        self.webhooks_url = url + WEBHOOKS_API
        self.timeout = timeout
        self.headers = {"Authorization": "Bearer " + self.at,
                        "Content-type": self.content_type}

    def get(self, url, params):
        response = requests.get(url, params=params,
                                headers=self.headers, timeout=self.timeout)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            return response.text

    def post(self, url, data):
        response = requests.post(url, data=data,
                                 headers=self.headers, timeout=self.timeout)
        if response.status_code != 200:
            response.raise_for_status()

    def put(self, url, data):
        response = requests.put(url, data=data,
                                headers=self.headers, timeout=self.timeout)
        if response.status_code != 200:
            response.raise_for_status()

    def delete(self, url):
        response = requests.delete(url, headers=self.headers,
                                   timeout=self.timeout)
        if response.status_code != 204:
            response.raise_for_status()

    def get_json(self, url, params=None):
        response = requests.get(url, params=params,
                                headers=self.headers, timeout=self.timeout)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            json_data = response.json()
            return json_data

    def get_json_items(self, url, params=None):
        initial_url = url
        response = requests.get(initial_url, params=params,
                                headers=self.headers, timeout=self.timeout)
        while True:
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
            if response.links.get('next'):
                next_url = response.links.get('next').get('url')
                response = requests.get(next_url, headers=self.headers,
                                        timeout=self.timeout)
            else:
                raise StopIteration

    def post_json(self, url, json_data):
        response = requests.post(url, json=json_data,
                                 headers=self.headers, timeout=self.timeout)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            return response.json()

    def put_json(self, url, json_data):
        response = requests.put(url, json=json_data,
                                headers=self.headers, timeout=self.timeout)
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
        people_items = self.get_json_items(self.people_url, params=params)
        for item in people_items:
            yield Person(item)

    def get_person(self, id):
        json_data = self.get_json(self.people_url + '/' + id)
        return Person(json_data)

    def get_person_me(self):
        json_data = self.get_json(self.people_url + '/me')
        return Person(json_data)

    def get_rooms(self, showSipAddress=False, max=None):
        params = {'showSipAddress': showSipAddress}
        if max:
            params['max'] = max
        room_items = self.get_json_items(self.rooms_url, params=params)
        for item in room_items:
            yield Room(item)

    def create_room(self, title):
        json_data = {'title': title}
        room_item = self.post_json(self.rooms_url, json_data)
        return Room(room_item)

    def get_room(self, id, showSipAddress=False):
        params = {'showSipAddress': showSipAddress}
        json_data = self.get_json(self.rooms_url+'/'+id, params)
        return Room(json_data)

    def update_room(self, id, **kwargs):
        assert kwargs and isinstance(kwargs, dict)
        json_data = kwargs
        room_item = self.put_json(self.rooms_url+'/'+id, json_data)
        return Room(room_item)

    def delete_room(self, id):
        self.delete(self.rooms_url+'/'+id)

    def get_memberships(self, roomId, personId=None, personEmail=None,
                        max=None):
        params = {'roomId': roomId}
        if personId:
            params['personId'] = personId
        elif personEmail:
            params['personEmail'] = personEmail
        if max:
            params['max'] = max
        membership_items = self.get_json_items(self.memberships_url, params)
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
        membership_item = self.post_json(self.memberships_url, json_data)
        return Membership(membership_item)

    def get_membership(self, id):
        json_data = self.get_json(self.memberships_url+'/'+id)
        return Membership(json_data)

    def update_membership(self, id, **kwargs):
        assert kwargs and isinstance(kwargs, dict)
        json_data = kwargs
        membership_item = self.put_json(self.memberships_url+'/'+id, json_data)
        return Membership(membership_item)

    def delete_membership(self, id):
        self.delete(self.memberships_url+'/'+id)

    def get_messages(self, roomId, before=None, beforeMessage=None, max=None):
        params = {'roomId': roomId}
        if before:
            params['before'] = before
        if beforeMessage:
            params['beforeMessage'] = beforeMessage
        if max:
            params['max'] = max
        message_items = self.get_json_items(self.messages_url, params)
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
        message_item = self.post_json(self.messages_url, json_data)
        return Message(message_item)

    def get_message(self, id):
        json_data = self.get_json(self.messages_url+'/'+id)
        return Message(json_data)

    def delete_message(self, id):
        self.delete(self.messages_url+'/'+id)

    def get_webhooks(self, max=None):
        params = {}
        if max:
            params['max'] = max
        webhook_items = self.get_json_items(self.webhooks_url, params)
        for item in webhook_items:
            yield Membership(item)

    def create_webhook(self, name, targetUrl, resource, event, filter):
        json_data = {'name': name,
                     'targetUrl': targetUrl,
                     'resource': resource,
                     'event': event,
                     'filter': filter}
        webhook_item = self.post_json(self.webhooks_url, json_data)
        return Webhook(webhook_item)

    def get_webhook(self, id):
        webhook_item = self.get_json(self.webhooks_url+'/'+id)
        return Webhook(webhook_item)

    def update_webhook(self, id, **kwargs):
        assert kwargs and isinstance(kwargs, dict)
        json_data = kwargs
        webhook_item = self.put_json(self.webhooks_url+'/'+id, json_data)
        return Webhook(webhook_item)

    def delete_webhook(self, id):
        self.delete(self.webhooks_url+'/'+id)


# Cisco Spark data objects
class Room(JSONDataObj):
    id = ROProperty()
    title = ROProperty()
    created = RODateTime()
    lastActivity = RODateTime()

    def __init__(self, *args, **kwargs):
        if args and not kwargs and isinstance(args[0], dict):
            kwargs = args[0]
        elif not kwargs:
            raise TypeError
        super(Room, self).__init__(**kwargs)


class Person(JSONDataObj):
    id = ROProperty()
    emails = ROProperty()
    displayName = ROProperty()
    avatar = ROProperty()
    created = RODateTime()

    def __init__(self, *args, **kwargs):
        if args and not kwargs and isinstance(args[0], dict):
            kwargs = args[0]
        elif not kwargs:
            raise TypeError
        super(Person, self).__init__(**kwargs)


class Membership(JSONDataObj):
    id = ROProperty()

    def __init__(self, *args, **kwargs):
        if args and not kwargs and isinstance(args[0], dict):
            kwargs = args[0]
        elif not kwargs:
            raise TypeError
        super(Membership, self).__init__(**kwargs)


class Message(JSONDataObj):
    id = ROProperty()

    def __init__(self, *args, **kwargs):
        if args and not kwargs and isinstance(args[0], dict):
            kwargs = args[0]
        elif not kwargs:
            raise TypeError
        super(Message, self).__init__(**kwargs)


class Webhook(JSONDataObj):
    id = ROProperty()

    def __init__(self, *args, **kwargs):
        if args and not kwargs and isinstance(args[0], dict):
            kwargs = args[0]
        elif not kwargs:
            raise TypeError
        super(Webhook, self).__init__(**kwargs)
