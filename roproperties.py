"""Read-Only-Properties module."""


class ROProperty(object):
    def __init__(self, name=None, internal_attr_name=None):
        self.name = name
        if name and not internal_attr_name:
            self.internal_attr_name = '_' + name
        else:
            self.internal_attr_name = internal_attr_name

    def __get__(self, instance, _):
        if instance is None:
            return self
        if not self.name or not self.internal_attr_name:
            raise AttributeError("Uninitialized ROProperty.")
        return getattr(instance, self.internal_attr_name)

    def __set__(self, instance, value):
        if not self.name or not self.internal_attr_name:
            raise AttributeError("Uninitialized ROProperty.")
        if hasattr(instance, self.internal_attr_name):
            raise AttributeError("Cannot assign value:  %r.%s is an "
                                 "ROProperty with an existing value." %
                                 (instance, self.name))
        else:
            setattr(instance, self.internal_attr_name, value)


class ROPropertiesMeta(type):
    def __new__(mcs, class_name, base_classes, class_dict):
        for attribute_name, value in class_dict.items():
            if isinstance(value, ROProperty):
                value.name = attribute_name
                value.internal_attr_name = '_' + attribute_name
        cls = type.__new__(mcs, class_name, base_classes, class_dict)
        return cls


class ROProperties(object):
    __metaclass__ = ROPropertiesMeta

    @classmethod
    def new_ro_property(cls, name):
        new_property = ROProperty(name)
        setattr(cls, name, new_property)
        return new_property
