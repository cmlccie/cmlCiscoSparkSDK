"""Represent JSON objects as native Python data objects."""


import json


# Module contants
READ_ONLY = 'read-only'
READ_WRITE = 'read-write'


class ROAttributeError(AttributeError):
    """Raised when attempting to write to an attribute marked as Read Only."""
    pass


def json_data_to_dict(json_data):
    # json_data must be a dictionary or JSON string
    if isinstance(json_data, dict):
        return json_data
    elif isinstance(json_data, basestring):
        return json.dumps(json_data)
    else:
        raise TypeError('json_data must be a dictionary or JSON string; '
                        'recieved: %r' % json_data)


class JSONData(object):
    def __init__(self, json_data, **kwargs):
        # Process kwargs
        init_values = kwargs.pop('init_values', True)
        default_access = kwargs.pop('_default_access', READ_WRITE)
        if kwargs:
            raise TypeError("Unexpected kwargs: %r" % kwargs)
        # Initialize class attributes
        json_dict = json_data_to_dict(json_data)
        self._json_attributes = json_dict.keys()
        self._default_access = default_access
        self._access_control = {}
        for attr in self._json_attributes:
            self._set_access_control(attr, self._default_access)
        # Set initial values, if specified
        if init_values:
            self._init_values(json_data)

    def _init_values(self, json_data):
        # Initialize object with initial values from json_data
        json_dict = json_data_to_dict(json_data)
        self._refresh_data(json_dict)

    def _refresh_data(self, json_data):
        json_dict = json_data_to_dict(json_data)
        for attr_name, attr_value in json_dict.items():
            if isinstance(attr_value, dict):
                # Nested JSON object
                attr_value = JSONData(attr_value, init_values=True,
                                      default_access=self._default_access)
            # Using super.__setattr__ to avoid recursion and access_control
            super(JSONData, self).__setattr__(attr_name, attr_value)

    def __setattr__(self, key, value):
        ac = self._get_access_control(key)
        if ac == READ_ONLY:
            raise ROAttributeError("Attempting to write to %r.%s, which has "
                                   "been marked as Read Only." % (self, key))
        else:
            # Using super.__setattr__ to avoid recursion
            super(JSONData, self).__setattr__(key, value)

    def _get_access_control(self, attribute):
        if hasattr(self, '_access_control'):
            return self._access_control.get(attribute)
        else:
            return None

    def _set_access_control(self, attribute, access_control):
        assert access_control == READ_ONLY or access_control == READ_WRITE
        self._access_control[attribute] = access_control

    def _json_dict(self):
        json_data = {}
        for attr_name in self._json_attributes:
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, JSONData):
                attr_value = attr_value._json_dict()
            json_data[attr_name] = attr_value
        return json_data

    def _json_str(self, pretty_print=False):
        if pretty_print:
            return json.dumps(self._json_dict(), sort_keys=True, indent=4)
        else:
            return json.dumps(self._json_dict())
