import json
from .fields import BaseField, IntegerField, CharField


class BaseModel(type):
    def __new__(cls, name, bases, attrs):
        fields = {k: v for k, v in attrs.items() if isinstance(v, BaseField)}
        attrs['_fields'] = fields
        return type.__new__(cls, name, bases, attrs)


class Model(object, metaclass=BaseModel):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        field = self._fields[key]
        field.set(value)
        super(Model, self).__setattr__(key, field.deserialize())

    def set_data(self, data, is_json=False):
        if is_json:
            data = json.loads(data)
        print(self._fields)
        for name, field in self._fields:
            key = field.source or name
            if key in data:
                setattr(self, name, data.get(key))

    def save(self):
        return True


class ModelCollection:
    def __init__(self, model=Model):
        self.items = None
        self.model = model

    def list(self):
        if self.items is None:
            # Download items
            self.items = []
        return self.items

    def get(self, **kwargs):
        pass

    def add(self, item):
        if isinstance(item, self.model):
            self.items.append(item)
        else:
            print("Item is not of type: {}".format(self.model))


class API:
    def __init__(self, token):
        self.token = token
        self.repos = ModelCollection(model=Repository)


class User(Model):
    name = CharField()

    def __repr__(self):
        return self.name


class Repository(Model):
    name = CharField()
    collaborators = ModelCollection(model=User)

    def __repr__(self):
        return self.name
