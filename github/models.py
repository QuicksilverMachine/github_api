import json
import requests
from .fields import BaseField, CharField, ModelField
from . import settings


class APIModelCollection:
    def __init__(self, model, api, list_url, get_url):
        self._items = None
        self._model = model
        self._api = api
        self._list_url = list_url
        self._get_url = get_url

    def list(self):
        if self._list_url is not None:
                items = API.authenticated_get_request(
                    request_url=self._list_url,
                    token=self._api.token
                )
                item_dicts = items.json()
                self._items = []
                for item_dict in item_dicts:
                    obj = self._model(api=self._api)
                    obj.set_data(data=item_dict)
                    self._items.append(obj)
        else:
            self._items = []
        return self._items

    def get(self, **kwargs):
        if self._get_url is not None:
            keys = {key: value for key, value in kwargs.items()}
            self._get_url = self._get_url.format(**keys)
            item = API.authenticated_get_request(
                    request_url=self._get_url,
                    token=self._api.token
            )
            item_dict = item.json()
            obj = self._model(api=self._api)
            obj.set_data(data=item_dict)
            return obj
        else:
            return None

    def add(self, item):
        if isinstance(item, self._model):
            self._items.append(item)
        else:
            print("Item is not of type: {}".format(self._model))


class APICollaboratorCollection(APIModelCollection):
    def get(self, login):
        if self._list_url is not None and self._get_url is not None:
            self._get_url = self._get_url.format(login=login)

            if self._items is None:
                self._items = self.list()

            if login in [collaborator.login for collaborator in self._items]:
                item = API.authenticated_get_request(
                        request_url=self._get_url,
                        token=self._api.token
                )
                item_dict = item.json()
                obj = self._model(api=self._api)
                obj.set_data(data=item_dict)
                return obj
        return None


class API:
    def __init__(self, token):
        self.token = token

    @staticmethod
    def auth_headers(token):
        return {'access_token': token}

    @staticmethod
    def authenticated_get_request(request_url, token):
        headers = API.auth_headers(token)
        response = requests.get(request_url, params=headers)
        return response

    @property
    def limit(self):
        limit = API.authenticated_get_request(settings.RATE_LIMIT_URL,
                                              self.token)
        return limit.content

    @property
    def repos(self):
        return APIModelCollection(
            model=Repository,
            api=self,
            list_url=settings.CURRENT_USER_REPOSITORIES_URL,
            get_url=settings.REPOSITORY_URL)


class BaseModel(type):
    def __new__(cls, name, bases, attrs):
        fields = {k: v for k, v in attrs.items() if isinstance(v, BaseField)}
        attrs['_fields'] = fields
        return type.__new__(cls, name, bases, attrs)


class Model(object, metaclass=BaseModel):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        if key in self._fields:
            field = self._fields[key]
            field.set(value)
            field._related_obj = self
            super(Model, self).__setattr__(key, field.deserialize())
        else:
            super(Model, self).__setattr__(key, value)

    def set_data(self, data, is_json=False):
        if is_json:
            data = json.loads(data)
        for key in self._fields:
            if key in data:
                setattr(self, key, data.get(key))

    def save(self):
        return True


class APIModel(Model):
    api = ModelField(API)


class User(APIModel):
    login = CharField()

    def __repr__(self):
        return self.login


class Repository(APIModel):
    full_name = CharField()
    description = CharField()

    @property
    def collaborators(self):
        return APICollaboratorCollection(
            model=User,
            api=self.api,
            list_url=settings.COLLABORATORS_LIST_URL.format(
                full_name=self.full_name),
            get_url=settings.COLLABORATOR_URL)

    def __repr__(self):
        return self.full_name
