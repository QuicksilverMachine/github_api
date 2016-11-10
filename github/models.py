from datetime import datetime
import json
from http import HTTPStatus
import requests
from github.fields import BaseField, CharField, ModelField
from github import settings
from github import exceptions


class API:
    """Class that defines the API endpoint

        Sets the token value during initialization and uses it to perform
        requests on the GitHub API
    """
    def __init__(self, token):
        self.token = token

    @staticmethod
    def _auth_headers(token):
        """Returns headers for requests
        :param token: user access token
        :return: dictionary containing the authentication headers
        """
        headers = settings.REQUEST_HEADERS
        headers['access_token'] = token
        return headers

    @staticmethod
    def raise_response_error(response):
        """
        Raises errors returned in response
        :param response: response object
        """
        response_dict = response.json()
        message = response_dict['message']
        if response_dict['errors'] is not None:
            errors = [r['message'] for r in response_dict['errors']]
            message += " - " + ', '.join(errors)
        raise exceptions.ResponseError(message)

    @staticmethod
    def authenticated_get_request(request_url, token):
        """Performs a get request and returns the response
        :param request_url: url to send the request to
        :param token: user access token
        :return: get request response
        """
        headers = API._auth_headers(token)
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
        headers = API._auth_headers(token)
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
        headers = API._auth_headers(token)
        response = requests.patch(url=request_url, data=data, params=headers)
        return response

    @property
    def rate_limits(self):
        """Gets the api rate limits
        :return: json rate limits
        """
        response = API.authenticated_get_request(settings.RATE_LIMIT_URL,
                                                 self.token)
        if response.status_code != HTTPStatus.OK:
            API.raise_response_error(response)
        else:
            return response.json()

    @property
    def standard_requests_remaining(self):
        """Gets the remaining standard api request uses
        :return: remaining uses count
        """
        limits = self.rate_limits
        return (limits['resources']['core']['remaining'] if limits is not None
                else None)

    @property
    def next_rate_limit_reset(self):
        """Gets the api rate limit reset time
        :return: datetime object
        """
        limits = self.rate_limits
        return (datetime.fromtimestamp(
            int(limits['resources']['core']['reset'])) if limits is not None
            else None)

    @property
    def repositories(self):
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
        Returns list of repositories
        :return: list of items
        """
        response = API.authenticated_get_request(
            request_url=settings.CURRENT_USER_REPOSITORIES_URL,
            token=self._api.token
        )
        if response.status_code != HTTPStatus.OK:
            API.raise_response_error(response)
        else:
            item_dicts = response.json()
            self._items = []
            for item_dict in item_dicts:
                obj = Repository(api=self._api)
                obj.set_data(data=item_dict)
                self._items.append(obj)
            return self._items

    def get(self, full_name):
        """
        Returns repository from list that matches the full_name parameter
        :param full_name: full_name of repository to find
        :return: found repository or None
        """
        get_url = settings.REPOSITORY_URL.format(full_name=full_name)
        response = API.authenticated_get_request(
                request_url=get_url,
                token=self._api.token
        )
        if response.status_code == HTTPStatus.OK:
            item_dict = response.json()
            obj = Repository(api=self._api)
            obj.set_data(data=item_dict)
            return obj
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return None
        else:
            API.raise_response_error(response)


class APICollaboratorCollection(APIModelCollection):
    """Class that defines a repository collaborator model collection"""
    def list(self):
        """
        Returns list of collaborators
        :return: list of items
        """
        response = API.authenticated_get_request(
            request_url=settings.COLLABORATORS_LIST_URL.format(
                full_name=self.parent.full_name),
            token=self._api.token
        )
        if response.status_code == HTTPStatus.OK:
            item_dicts = response.json()
            self._items = []
            for item_dict in item_dicts:
                obj = User(api=self._api)
                obj.set_data(data=item_dict)
                self._items.append(obj)
            return self._items
        else:
            API.raise_response_error(response)

    def get(self, login):
        """
        Returns collaborator from list that matches the login parameter
        :param login: username of a collaborator
        :return: found collaborator or None
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
            if response.status_code == HTTPStatus.OK:
                item_dict = response.json()
                obj = User(api=self._api)
                obj.set_data(data=item_dict)
                return obj
            else:
                API.raise_response_error(response)
        return None

    def add(self, collaborator):
        """Add collaborator to repository
        :param collaborator: user to add to collaborators
        """
        add_url = settings.COLLABORATOR_ADD_URL.format(
            full_name=self.parent.full_name,
            login=collaborator.login)
        response = API.authenticated_put_request(
                request_url=add_url,
                token=self._api.token
        )
        if response.status_code != HTTPStatus.OK:
            API.raise_response_error(response)


class BaseModel(type):
    """Metaclass for model definition

        Adds all model fields to _fields attribute
    """
    def __new__(mcs, name, bases, attrs):
        fields = {k: v for k, v in attrs.items() if isinstance(v, BaseField)}
        attrs['_fields'] = fields
        return type.__new__(mcs, name, bases, attrs)


class Model(object, metaclass=BaseModel):
    """Base model class

        Used to define all models
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
        """Return model's serialized dictionary representation
        :return: dictionary
        """
        return dict((key, self._fields[key].serialize(getattr(self, key)))
                    for key in self._fields.keys() if hasattr(self, key))

    def to_json(self):
        """Return model's serialized json representation
        :return: json
        """
        return json.dumps(self.to_dict())

    def set_data(self, data):
        """Sets data to model fields
        :param data: data to set
        :param is_json: is input data in json format
        """
        for key in self._fields:
            if key in data:
                setattr(self, key, data.get(key))


class APIModel(Model):
    """Base model for API objects
    """
    api = ModelField(API)

    def _save(self, save_url):
        """Update object on GitHub server
        :param save_url: url to send save request to
        """
        response = API.authenticated_patch_request(save_url,
                                                   token=self.api.token,
                                                   data=self.to_json())
        if response.status_code != HTTPStatus.OK:
            API.raise_response_error(response)


class User(APIModel):
    """User model for API calls"""
    login = CharField()

    def save(self):
        """Update authenticated user on GitHub server
        """
        self._save(settings.AUTHENTICATED_USER)

    def __repr__(self):
        return self.login


class Repository(APIModel):
    """Repository model for API calls"""
    name = CharField()
    full_name = CharField()
    description = CharField()

    def save(self):
        """Update repository on GitHub server"""
        self._save(settings.REPOSITORY_URL.format(full_name=self.full_name))

    @property
    def collaborators(self):
        """Returns list of repository collaborators
        :return: collaborator collection object
        """
        return APICollaboratorCollection(api=self.api, parent=self)

    def __repr__(self):
        return self.full_name
