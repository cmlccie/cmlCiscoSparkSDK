"""Read-Only Properties module.

CLASSES
    ROProperty       - Provides read-only descriptor properties.
    ROPropertiesMeta - Meta-class simplifies use of ROProperties in classes.
    ROProperties     - Mixin class for classes leveraging ROProperties.

MODULE EXCEPTIONS
    ROPropertyError  - Base class for exceptions in this module.
    ROInitError      - Raised when accessing an uninitialized ROProperty.
    ROReadError      - Raised when reading from a ROProperty fails.
    ROWriteError     - Raised when writing to a ROProperty fails.
"""


class ROProperty(object):
    def __init__(self, name=None, internal_attr_name=None):
        self.name = name
        if name and not internal_attr_name:
            self.internal_attr_name = '_' + name
        else:
            self.internal_attr_name = internal_attr_name

    def _fix_init(self, instance=None, owner=None):
        owner = owner if owner else instance.__class__
        if not self.name:
            for obj in owner.__mro__:
                for attr_name, attr_value in obj.__dict__.items():
                    if attr_value is self:
                        self.name = attr_name
        if self.name and not self.internal_attr_name:
            self.internal_attr_name = '_' + self.name
        if not self.name or not self.internal_attr_name:
            raise ROInitError(self)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if not self.name or not self.internal_attr_name:
            self._fix_init(instance=instance, owner=owner)
        try:
            return getattr(instance, self.internal_attr_name)
        except AttributeError:
            raise ROReadError(instance, self)

    def __set__(self, instance, value):
        if not self.name or not self.internal_attr_name:
            self._fix_init(instance=instance)
        try:
            getattr(instance, self.name)
        except ROReadError:
            setattr(instance, self.internal_attr_name, value)
        else:
            raise ROWriteError(value, instance, self)

    def __repr__(self):
        if not self.name and not self.internal_attr_name:
            return '%s()' % self.__class__.__name__
        elif self.internal_attr_name == '_'+self.name:
            return '%s("%s")' % (self.__class__.__name__, self.name)
        else:
            return '%s(name="%s", internal_attr_name="%s")' % \
                   (self.__class__.__name__, self.name,
                    self.internal_attr_name)


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
    def new_ro_property(cls, name, internal_attr_name=None):
        new_property = ROProperty(name, internal_attr_name)
        setattr(cls, name, new_property)


# Module exceptions
class ROPropertyError(AttributeError):
    """Base clase for exceptions in this module."""
    pass


class ROInitError(ROPropertyError):
    """Raised when attempting to use an uninitialized ROProperty."""
    def __init__(self, ro_property):
        """Uninitialized 'ro_property'."""
        super(ROPropertyError, ROReadError).__init__(self, ro_property)
        self.ro_property = ro_property

    def __str__(self):
        return "uninitialized ROProperty '%s'" % self.ro_property


class ROReadError(ROPropertyError):
    """Raised when attempting to read from a ROProperty with no value set."""
    def __init__(self, instance, ro_property):
        """Error attempting to read 'ro_property' from 'instance'."""
        super(ROPropertyError, ROReadError).__init__(self, instance,
                                                     ro_property)
        self.ro_property = ro_property
        self.instance = instance

    def __str__(self):
        return "no value set for ROProperty '%r.%s'" % \
               (self.instance, self.ro_property.name)


class ROWriteError(ROPropertyError):
    """Raised when attempting to set a value to an initialized ROProperty."""
    def __init__(self, value, instance, ro_property):
        """Error attempting to set 'value' to 'instance'.'ro_property'."""
        super(ROPropertyError, ROReadError).__init__(self, value, instance,
                                                     ro_property)
        self.value = value
        self.ro_property = ro_property
        self.instance = instance

    def __str__(self):
        return "cannot set value '%s' to ROProperty '%r.%s'" \
               % (self.value, self.instance, self.ro_property.name)
