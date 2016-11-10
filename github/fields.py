class BaseField:
    """Class for defining the base model field

        All other fields inherit from BaseField
    """
    default_value = None

    def __init__(self, **kwargs):
        self.data = self.default_value

    def set(self, data=None):
        """Set field value
        :param data: data to set
        """
        self.data = data

    def serialize(self, data):
        """Returns a serialized field representation
        :param data: data to serialize
        :return: serialized data
        """
        return data

    def deserialize(self):
        """Returns a python object field representation
        :param data: data to deserialize
        :return: deserialized data
        """
        return self.data


class CharField(BaseField):
    """Class for a string field"""
    default_value = ""

    def deserialize(self):
        if self.data is None:
            return self.default_value
        else:
            return str(self.data)


class BooleanField(BaseField):
    """Class for a boolean field"""
    default_value = False

    def deserialize(self):
        if isinstance(self.data, str):
            return self.data.strip().lower() == 'true'
        if isinstance(self.data, int):
            return self.data > 0
        return bool(self.data)


class IntegerField(BaseField):
    """Class for a integer field"""
    default_value = 0

    def deserialize(self):
        if self.data is None:
            return self.default_value
        else:
            return int(self.data)


class FloatField(BaseField):
    """Class for a float field"""
    default_value = 0

    def deserialize(self):
        if self.data is None:
            return self.default_value
        else:
            return float(self.data)


class WrappedObjectField(BaseField):
    """Class for a wrapped object"""
    def __init__(self, wrapped_class, related_name=None, **kwargs):
        self._wrapped_class = wrapped_class
        self._related_name = related_name
        self._related_obj = None
        BaseField.__init__(self, **kwargs)


class ModelField(WrappedObjectField):
    """Class for a field that contains a model object"""
    def deserialize(self):
        if isinstance(self.data, self._wrapped_class):
            obj = self.data
        else:
            obj = self._wrapped_class.from_dict(self.data or {})
        # Set the related object to the related field
        if self._related_name is not None:
            setattr(obj, self._related_name, self._related_obj)
        return obj
