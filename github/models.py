import json
import requests
from .fields import BaseField, CharField, ModelField
from . import settings


class API:
    """Class that defines the API endpoint

        Sets the token value during initialization and uses it to perform
        requests on the Github API
    """
    def __init__(self, token):
        self.token = token

    @staticmethod
    def auth_headers(token):
        """Returns authentication headers for requests
        :param token: user access token
        :return: dictionary containing the authentication headers
        """
        return {'access_token': token}

    @staticmethod
    def authenticated_get_request(request_url, token):
        """Performs a get request and returns the response
        :param request_url: url to send the request to
        :param token: user access token
        :return: get request response
        """
        headers = API.auth_headers(token)
        response = requests.get(request_url, params=headers)
        return response

    @staticmethod
    def authenticated_put_request(request_url, token, data=None):
        """Performs a put request and returns the response
        :param request_url: url to send the request to
        :param token: user access token
        :param data: data to be sent
        :return: get request response
        """
        headers = API.auth_headers(token)
        response = requests.put(url=request_url, data=data, params=headers)
        return response

    @staticmethod
    def authenticated_patch_request(request_url, token, data=None):
        """Performs a patch request and returns the response
        :param request_url: url to send the request to
        :param token: user access token
        :param data: data to be sent
        :return: get request response
        """
        headers = API.auth_headers(token)
        response = requests.patch(url=request_url, data=data, params=headers)
        return response

    @property
    def limit(self):
        """Gets the remaining api request uses
        :return: remaining uses
        """
        response = API.authenticated_get_request(settings.RATE_LIMIT_URL,
                                              self.token)
        return response.content

    @property
    def repos(self):
        """Returns list of repositories the authenticated user has access to
        :return: repository collection object
        """
        return APIRepositoryCollection(api=self, parent=self)


class APIModelCollection:
    """Class that defines a model collection

        Contains collection items, a reference to the api object
        and a reference to the parent object
    """
    def __init__(self, api, parent=None):
        self._items = []
        self._api = api
        self.parent = parent


class APIRepositoryCollection(APIModelCollection):
    """Class that defines a repository model collection"""

    def list(self):
        """

        :return:
        """
        response = API.authenticated_get_request(
            request_url=settings.CURRENT_USER_REPOSITORIES_URL,
            token=self._api.token
        )
        item_dicts = response.json()
        self._items = []
        for item_dict in item_dicts:
            obj = Repository(api=self._api)
            obj.set_data(data=item_dict)
            self._items.append(obj)
        return self._items

    def get(self, full_name):
        """

        :param full_name:
        :return:
        """
        get_url = settings.REPOSITORY_URL.format(full_name=full_name)
        response = API.authenticated_get_request(
                request_url=get_url,
                token=self._api.token
        )
        item_dict = response.json()
        obj = Repository(api=self._api)
        obj.set_data(data=item_dict)
        return obj


class APICollaboratorCollection(APIModelCollection):
    """
    """
    def list(self):
        """

        :return:
        """
        response = API.authenticated_get_request(
            request_url=settings.COLLABORATORS_LIST_URL.format(
                full_name=self.parent.full_name),
            token=self._api.token
        )
        item_dicts = response.json()
        self._items = []
        for item_dict in item_dicts:
            obj = User(api=self._api)
            obj.set_data(data=item_dict)
            self._items.append(obj)
        return self._items

    def get(self, login):
        """

        :param login:
        :return:
        """
        get_url = settings.COLLABORATOR_URL.format(
            full_name=self.parent.full_name,
            login=login
        )
        if len(self._items) is 0:
            self._items = self.list()
        if login in [collaborator.login for collaborator in self._items]:
            response = API.authenticated_get_request(
                    request_url=get_url,
                    token=self._api.token
            )
            item_dict = response.json()
            obj = User(api=self._api)
            obj.set_data(data=item_dict)
            return obj
        return None

    def add(self, item):
        """

        :param item:
        :return:
        """
        if item in self._items:
            add_url = settings.COLLABORATOR_ADD_URL.format(
                full_name=self.parent.full_name,
                login=item.login)
            response = API.authenticated_put_request(
                    request_url=add_url,
                    token=self._api.token
            )


class BaseModel(type):
    """

    """
    def __new__(cls, name, bases, attrs):
        fields = {k: v for k, v in attrs.items() if isinstance(v, BaseField)}
        attrs['_fields'] = fields
        return type.__new__(cls, name, bases, attrs)


class Model(object, metaclass=BaseModel):
    """

    """
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

    def to_dict(self):
        """

        :return:
        """
        return dict((key, self._fields[key].serialize(getattr(self, key)))
                    for key in self._fields.keys() if hasattr(self, key))

    def to_json(self):
        """

        :return:
        """
        return json.dumps(self.to_dict())

    def set_data(self, data, is_json=False):
        """

        :param data:
        :param is_json:
        :return:
        """
        if is_json:
            data = json.loads(data)
        for key in self._fields:
            if key in data:
                setattr(self, key, data.get(key))


class APIModel(Model):
    """

    """
    api = ModelField(API)

    def _save(self, save_url):
        """

        :param save_url:
        :return:
        """
        response = API.authenticated_patch_request(save_url,
                                                   token=self.api.token,
                                                   data=self.to_json())


class User(APIModel):
    """

    """
    login = CharField()

    def save(self):
        """

        :return:
        """
        self._save(settings.AUTHENTICATED_USER)

    def __repr__(self):
        return self.login


class Repository(APIModel):
    name = CharField()
    full_name = CharField()
    description = CharField()

    def save(self):
        """

        :return:
        """
        self._save(settings.REPOSITORY_URL.format(full_name=self.full_name))

    @property
    def collaborators(self):
        """

        :return:
        """
        return APICollaboratorCollection(api=self.api, parent=self)

    def __repr__(self):
        return self.full_name




