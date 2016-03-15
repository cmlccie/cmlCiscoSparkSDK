import json

from roproperties import ROProperties, ROProperty


def _getattr(obj, name, **kwargs):
    """Get attribute from obj ignoring descriptor protocol."""
    for o in [obj] + obj.__class__.mro():
        if name in o.__dict__:
            return o.__dict__[name]
    if 'default' in kwargs.keys():
        return kwargs['default']
    else:
        raise AttributeError


class JSONDataObj(ROProperties):
    def __init__(self, **kwargs):
        for attr_name, attr_value in kwargs.items():
            if not hasattr(self, attr_name):
                if not isinstance(_getattr(self, attr_name, default=None),
                                  ROProperty):
                    self.new_ro_property(attr_name)
                setattr(self, attr_name, attr_value)

    @classmethod
    def from_json(cls, json_str):
        json_data = json.loads(json_str)
        return cls(**json_data)
