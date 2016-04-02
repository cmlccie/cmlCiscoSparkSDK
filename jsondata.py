"""Represent JSON objects as native Python data objects."""


import json


# Module contants
READ_ONLY = 'read-only'
READ_WRITE = 'read-write'


class ROAttributeError(AttributeError):
    """Raised when attempting to write to an attribute marked as Read Only."""
    pass


class JSONData(object):
    def __init__(self, json_data, init_values=True, default_access=READ_WRITE):
        # Ensure json_data is a dictionary
        if isinstance(json_data, basestring):
            json_data = json.dumps(json_data)
        if not isinstance(json_data, dict):
            raise TypeError('Argument json_data should be a dict or '
                            'valid JSON string; recieved: %r' % json_data)
        # Initialize class attributes
        self.default_access = default_access
        self._json_attributes = json_data.keys()
        self._access_control = {}
        for attr in self._json_attributes:
            self.set_access_control(attr, self.default_access)
        # Set initial values, if specified
        if init_values:
            self.init_values(json_data)

    def init_values(self, json_data):
        # Initialize object with initial values from json_data
        self.refresh_data(json_data)

    def refresh_data(self, json_data):
        for attr_name, attr_value in json_data.items():
            if isinstance(attr_value, dict):
                # Nested JSON object
                attr_value = JSONData(attr_value, init_values=True,
                                      default_access=self.default_access)
            # Using super.__setattr__ to avoid recursion and access_control
            super(JSONData, self).__setattr__(attr_name, attr_value)

    def __setattr__(self, key, value):
        ac = self.get_access_control(key)
        if ac == READ_ONLY:
            raise ROAttributeError("Attempting to write to %r.%s, which has "
                                   "been marked as Read Only." % (self, key))
        else:
            # Using super.__setattr__ to avoid recursion
            super(JSONData, self).__setattr__(key, value)

    def get_access_control(self, attribute):
        if hasattr(self, '_access_control'):
            return self._access_control.get(attribute)
        else:
            return None

    def set_access_control(self, attribute, access_control):
        assert access_control == READ_ONLY or access_control == READ_WRITE
        self._access_control[attribute] = access_control

    def json_data(self):
        json_data = {}
        for attr_name in self._json_attributes:
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, JSONData):
                attr_value = attr_value.json_data()
            json_data[attr_name] = attr_value
        return json_data

    def json_str(self, pretty_print=False):
        if pretty_print:
            return json.dumps(self.json_data(), sort_keys=True, indent=4)
        else:
            return json.dumps(self.json_data())
