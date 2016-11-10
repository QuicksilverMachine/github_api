class BaseField:
    default_value = None

    def __init__(self, **kwargs):
        self.data = self.default_value

    def set(self, data=None):
        self.data = data

    def serialize(self, data):
        return data

    def deserialize(self):
        return self.data

    def __repr__(self):
        return str(self.data)


class CharField(BaseField):
    default_value = ""

    def deserialize(self):
        if self.data is None:
            return self.default_value
        else:
            return str(self.data)


class BooleanField(BaseField):
    default_value = False

    def deserialize(self):
        if isinstance(self.data, str):
            return self.data.strip().lower() == 'true'
        if isinstance(self.data, int):
            return self.data > 0
        return bool(self.data)


class IntegerField(BaseField):
    default_value = 0

    def deserialize(self):
        if self.data is None:
            return self.default_value
        else:
            return int(self.data)


class FloatField(BaseField):
    default_value = 0

    def deserialize(self):
        if self.data is None:
            return self.default_value
        else:
            return float(self.data)


class WrappedObjectField(BaseField):
    def __init__(self, wrapped_class, related_name=None, **kwargs):
        self._wrapped_class = wrapped_class
        self._related_name = related_name
        self._related_obj = None
        BaseField.__init__(self, **kwargs)


class ModelField(WrappedObjectField):
    def deserialize(self):
        if isinstance(self.data, self._wrapped_class):
            obj = self.data
        else:
            obj = self._wrapped_class.from_dict(self.data or {})
        # Set the related object to the related field
        if self._related_name is not None:
            setattr(obj, self._related_name, self._related_obj)
        return obj
