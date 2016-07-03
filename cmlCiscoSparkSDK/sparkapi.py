"""@cmlccie Cisco Spark Python SDK."""

from datetime import datetime

import pytz

from jsondata import JSONData, READ_ONLY, READ_WRITE
from restapi import RESTfulAPI


# Module constants
DEFAULT_API_URL = 'https://api.ciscospark.com/v1/'
PEOPLE_URL = 'people'
ROOMS_URL = 'rooms'
MEMBERSHIPS_URL = 'memberships'
MESSAGES_URL = 'messages'
TEAMS_URL = 'teams'
TEAM_MEMBERSHIPS_URL = 'team/memberships'
WEBHOOKS_URL = 'webhooks'
GET_EXPECTED_STATUS_CODE = 200
POST_EXPECTED_STATUS_CODE = 200
PUT_EXPECTED_STATUS_CODE = 200
DELETE_EXPECTED_STATUS_CODE = 204


# Helper functions
def spark_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')\
                    .replace(tzinfo=pytz.utc)


# Helper classes
class SparkDateTime(object):
    def __init__(self, name, internal_attr_name=None):
        self.name = name
        if internal_attr_name:
            self.internal_attr_name = internal_attr_name
        else:
            self.internal_attr_name = '_' + name

    def __get__(self, instance, _):
        if instance is None:
            return self
        return getattr(instance, self.internal_attr_name)

    def __set__(self, instance, value):
        value = spark_datetime(value)
        setattr(instance, self.internal_attr_name, value)


# Module exceptions
class CMLSparkException(Exception):
    pass


class CiscoSparkException(CMLSparkException):
    # TODO: Map Cisco Spark response codes to descriptive errors
    pass


# Cisco Spark data objects
class SparkDataObject(JSONData):
    def __init__(self, json_data, **kwargs):
        # Process kwargs for SparkDataObjects
        self._api = kwargs.pop('api', None)
        # Process JSONData kwargs setting defaults for SparkDataObjects
        kwargs['init_values'] = kwargs.get('init_values', True)
        kwargs['default_access'] = kwargs.get('default_access', READ_ONLY)
        super(SparkDataObject, self).__init__(json_data, **kwargs)


class Room(SparkDataObject):
    id = None
    title = None
    created = SparkDateTime("created")
    lastActivity = SparkDateTime("lastActivity")
    isLocked = None


class Person(SparkDataObject):
    id = None
    emails = None
    displayName = None
    avatar = None
    created = SparkDateTime("created")


class Membership(SparkDataObject):
    id = None
    personId = None
    personEmail = None
    personDisplayName = None
    roomId = None
    isModerator = None
    isMonitor = None
    created = SparkDateTime("created")


class Message(SparkDataObject):
    id = None
    roomId = None
    text = None
    personId = None
    personEmail = None
    created = SparkDateTime("created")


class Team(SparkDataObject):
    id = None
    name = None
    created = SparkDateTime("created")


class TeamMembership(SparkDataObject):
    id = None
    teamId = None
    personEmail = None
    personDisplayName = None
    isModerator = None
    created = SparkDateTime("created")


class Webhook(SparkDataObject):
    id = None
    name = None
    resource = None
    event = None
    filter = None
    data = None


# Cisco Spark API methods container class
class CiscoSparkAPI(RESTfulAPI):
    def __init__(self, authentication_token, api_url=DEFAULT_API_URL,
                 timeout=None):
        super(CiscoSparkAPI, self).__init__(api_url)
        self.authentication_token = authentication_token
        self.request_args['timeout'] = timeout
        self.request_args['headers'] = {
            'Authorization': 'Bearer ' + self.authentication_token}

    def delete(self, url, **request_args):
        response = super(CiscoSparkAPI, self).delete(url, **request_args)
        if response.status_code != DELETE_EXPECTED_STATUS_CODE:
            response.raise_for_status()

    def _format_return(self, json_dict, return_type):
        if issubclass(return_type, SparkDataObject):
            return return_type(json_dict, api=self)
        elif issubclass(return_type, JSONData):
            return return_type(json_dict)
        elif issubclass(return_type, dict):
            return json_dict
        else:
            raise NotImplementedError("return_type: %r" % return_type)

    def get_json(self, url, params=None):
        response = self.get(url, params=params)
        if response.status_code != GET_EXPECTED_STATUS_CODE:
            response.raise_for_status()
        else:
            json_data = response.json()
            return json_data

    def get_json_items(self, url, params=None):
        responses = self.get_iter(url, params=params)
        for response in responses:
            items = []
            if response.status_code != GET_EXPECTED_STATUS_CODE:
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

    def post_json(self, url, json_dict):
        response = self.post(url, json=json_dict)
        if response.status_code != POST_EXPECTED_STATUS_CODE:
            response.raise_for_status()
        else:
            return response.json()

    def put_json(self, url, json_dict):
        response = self.put(url, json=json_dict)
        if response.status_code != PUT_EXPECTED_STATUS_CODE:
            response.raise_for_status()
        else:
            return response.json()

    def get_people(self, email=None, displayName=None, max=None,
                   return_type=Person):
        params = {}
        if email:
            params['email'] = email
        elif displayName:
            params['displayName'] = displayName
        else:
            raise CMLSparkException('')
        if max:
            params['max'] = max
        people_items = self.get_json_items(PEOPLE_URL, params=params)
        for item in people_items:
            yield self._format_return(item, return_type)

    def get_person(self, id, return_type=Person):
        json_dict = self.get_json(PEOPLE_URL + '/' + id)
        return self._format_return(json_dict, return_type)

    def get_person_me(self, return_type=Person):
        json_dict = self.get_json(PEOPLE_URL + '/me')
        return self._format_return(json_dict, return_type)

    def get_rooms(self, showSipAddress=False, max=None, return_type=Room):
        params = {'showSipAddress': showSipAddress}
        if max:
            params['max'] = max
        room_items = self.get_json_items(ROOMS_URL, params=params)
        for item in room_items:
            yield self._format_return(item, return_type)

    def create_room(self, title, return_type=Room):
        json_payload_dict = {'title': title}
        json_dict = self.post_json(ROOMS_URL, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def get_room(self, id, showSipAddress=False, return_type=Room):
        params = {}
        if showSipAddress:
            params['showSipAddress'] = showSipAddress
        json_dict = self.get_json(ROOMS_URL+'/'+id, params)
        return self._format_return(json_dict, return_type)

    def update_room(self, id, return_type=Room, **attributes):
        assert attributes
        json_payload_dict = attributes
        json_dict = self.put_json(ROOMS_URL+'/'+id, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def delete_room(self, id):
        self.delete(ROOMS_URL+'/'+id)

    def get_memberships(self, roomId, personId=None, personEmail=None,
                        max=None, return_type=Membership):
        params = {'roomId': roomId}
        if personId:
            params['personId'] = personId
        elif personEmail:
            params['personEmail'] = personEmail
        if max:
            params['max'] = max
        membership_items = self.get_json_items(MEMBERSHIPS_URL, params)
        for item in membership_items:
            yield self._format_return(item, return_type)

    def create_membership(self, roomId, personId=None, personEmail=None,
                          isModerator=False, return_type=Membership):
        json_payload_dict = {'roomId': roomId, 'isModerator': isModerator}
        if personId:
            json_payload_dict['personId'] = personId
        elif personEmail:
            json_payload_dict['personEmail'] = personEmail
        else:
            raise CMLSparkException
        json_dict = self.post_json(MEMBERSHIPS_URL, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def get_membership(self, id, return_type=Membership):
        json_dict = self.get_json(MEMBERSHIPS_URL+'/'+id)
        return self._format_return(json_dict, return_type)

    def update_membership(self, id, return_type=Membership, **attributes):
        assert attributes
        json_payload_dict = attributes
        json_dict = self.put_json(MEMBERSHIPS_URL+'/'+id, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def delete_membership(self, id):
        self.delete(MEMBERSHIPS_URL+'/'+id)

    def get_messages(self, roomId, before=None, beforeMessage=None, max=None,
                     return_type=Message):
        params = {'roomId': roomId}
        if before:
            params['before'] = before
        if beforeMessage:
            params['beforeMessage'] = beforeMessage
        if max:
            params['max'] = max
        message_items = self.get_json_items(MESSAGES_URL, params)
        for item in message_items:
            yield self._format_return(item, return_type)

    def create_message(self, roomId=None, text=None, files=None,
                       toPersonId=None, toPersonEmail=None,
                       return_type=Message):
        json_payload_dict = {}
        if roomId:
            json_payload_dict['roomId'] = roomId
        elif toPersonId:
            json_payload_dict['toPersonId'] = toPersonId
        elif toPersonEmail:
            json_payload_dict['toPersonEmail'] = toPersonEmail
        else:
            raise CMLSparkException
        if not text and not files:
            raise CMLSparkException
        if text:
            json_payload_dict['text'] = text
        if files:
            json_payload_dict['files'] = files
        json_dict = self.post_json(MESSAGES_URL, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def get_message(self, id, return_type=Message):
        json_dict = self.get_json(MESSAGES_URL+'/'+id)
        return self._format_return(json_dict, return_type)

    def delete_message(self, id):
        self.delete(MESSAGES_URL+'/'+id)

    def get_teams(self, max=None, return_type=Team):
        params = {}
        if max:
            params['max'] = max
        team_items = self.get_json_items(TEAMS_URL, params=params)
        for item in team_items:
            yield self._format_return(item, return_type)

    def create_team(self, name, return_type=Team):
        json_payload_dict = {'name': name}
        json_dict = self.post_json(TEAMS_URL, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def get_team(self, id, return_type=Team):
        json_dict = self.get_json(TEAMS_URL+'/'+id)
        return self._format_return(json_dict, return_type)

    def update_team(self, id, return_type=Team, **attributes):
        assert attributes
        json_payload_dict = attributes
        json_dict = self.put_json(TEAMS_URL+'/'+id, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def delete_team(self, id):
        self.delete(TEAMS_URL+'/'+id)

    def get_team_memberships(self, teamId, max=None,
                             return_type=TeamMembership):
        params = {'teamId': teamId}
        if max:
            params['max'] = max
        membership_items = self.get_json_items(TEAM_MEMBERSHIPS_URL, params)
        for item in membership_items:
            yield self._format_return(item, return_type)

    def create_team_membership(self, teamId, personId=None, personEmail=None,
                               isModerator=False, return_type=TeamMembership):
        json_payload_dict = {'teamId': teamId, 'isModerator': isModerator}
        if personId:
            json_payload_dict['personId'] = personId
        elif personEmail:
            json_payload_dict['personEmail'] = personEmail
        else:
            raise CMLSparkException
        json_dict = self.post_json(TEAM_MEMBERSHIPS_URL, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def get_team_membership(self, id, return_type=TeamMembership):
        json_dict = self.get_json(TEAM_MEMBERSHIPS_URL + '/' + id)
        return self._format_return(json_dict, return_type)

    def update_team_membership(self, id, return_type=TeamMembership,
                               **attributes):
        assert attributes
        json_payload_dict = attributes
        json_dict = self.put_json(TeamMembership+'/'+id, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def delete_team_membership(self, id):
        self.delete(TEAM_MEMBERSHIPS_URL + '/' + id)

    def get_webhooks(self, max=None, return_type=Webhook):
        params = {}
        if max:
            params['max'] = max
        webhook_items = self.get_json_items(WEBHOOKS_URL, params)
        for item in webhook_items:
            yield self._format_return(item, return_type)

    def create_webhook(self, name, targetUrl, resource, event, filter,
                       return_type=Webhook):
        json_payload_dict = {'name': name,
                             'targetUrl': targetUrl,
                             'resource': resource,
                             'event': event,
                             'filter': filter}
        json_dict = self.post_json(WEBHOOKS_URL, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def get_webhook(self, id, return_type=Webhook):
        json_dict = self.get_json(WEBHOOKS_URL+'/'+id)
        return self._format_return(json_dict, return_type)

    def update_webhook(self, id, return_type=Webhook, **attributes):
        assert attributes
        json_payload_dict = attributes
        json_dict = self.put_json(WEBHOOKS_URL+'/'+id, json_payload_dict)
        return self._format_return(json_dict, return_type)

    def delete_webhook(self, id):
        self.delete(WEBHOOKS_URL+'/'+id)
