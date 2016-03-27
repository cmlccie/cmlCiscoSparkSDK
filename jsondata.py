"""Represent JSON objects as native Python data objects."""

import json

from roproperties import ROProperties, ROProperty


def _hasattr_no_desc(obj, name):
    """Check if obj has an attribute or property named 'name'.

    This function ignores the descriptor protocol.
    """
    for o in [obj] + obj.__class__.mro():
        if name in o.__dict__:
            return True
    return False


# class JSONAttr(ROProperty):
#     def __init__(self, name=None):
#         self.name = name
#
#     def _fix_init(self, instance=None, owner=None):
#         owner = owner if owner else instance.__class__
#         if not self.name:
#             for obj in owner.__mro__:
#                 for attr_name, attr_value in obj.__dict__.items():
#                     if attr_value is self:
#                         self.name = attr_name
#
#     def __get__(self, instance, owner):
#         if instance is None:
#             return self
#         if not self.name:
#             self._fix_init(instance=instance, owner=owner)
#         return getattr(instance, self.name)
#
#     def __set__(self, instance, value):
#         if not self.name:
#             self._fix_init(instance=instance)
#         setattr(instance, self.name, value)


class JSONProp(ROProperty):
    pass


class JSONData(ROProperties):
    def __init__(self, json_data, **kwargs):
        if isinstance(json_data, basestring):
            json_data = json.dumps(json_data)
        if not isinstance(json_data, dict):
            raise TypeError('Argument json_data should be a dict or '
                            'valid JSON string; recieved: %r' % json_data)
        # Store JSON attributes for later serialization
        self._json_attributes = json_data.keys()
        # Create ROProperties for JSON attributes that do not exist in self
        for attr_name, attr_value in json_data.items():
            if not _hasattr_no_desc(self, attr_name):
                self.new_ro_property(attr_name)
                if isinstance(attr_value, dict):
                    # Nested JSON object
                    attr_value = JSONData(attr_value)
                setattr(self, attr_name, attr_value)

    def to_json(self):
        json_data = {}
        for attr_name in self._json_attributes:
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, JSONData):
                attr_value = attr_value.to_json()
            json_data[attr_name] = attr_value
        json_str = json.dumps(json_data)
        return json_str
