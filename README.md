
# github_api


```python
import github
```

We initialize the API object by adding an access token:


```python
api = github.API(token="...")
```

If we want to list all repositories which the authenticated user has access to, we do it with the following command, which returns a list of Repository objects.


```python
api.repositories.list()
```




    [QuicksilverMachine/github_api]



If we want the names of these repositories:


```python
[repository.full_name for repository in api.repositories.list()]
```




    ['QuicksilverMachine/github_api']



More detailed information about specific repositories we get with the get function.


```python
repository = api.repositories.get("QuicksilverMachine/github_api")
repository.description
```




    'A small python library to interface with Github API. - changed with api'



Save command is used to save the changes on a repository.


```python
repository.description = "A small python library to interface with Github API. - changed with api"
repository.save()
```

GitHub api has a limit on a number of requests that can be made to it. The rate_limits property returns a dictionary with detailed information about request limits.


```python
api.rate_limits
```




    {'rate': {'limit': 5000, 'remaining': 4934, 'reset': 1478858765},
     'resources': {'core': {'limit': 5000, 'remaining': 4934, 'reset': 1478858765},
      'graphql': {'limit': 200, 'remaining': 200, 'reset': 1478861545},
      'search': {'limit': 30, 'remaining': 30, 'reset': 1478858005}}}



Only the standard request remaining count:


```python
api.standard_requests_remaining
```




    4934



The next_rate_limit_reset property returns a datetime object with the time of the next rate_limit count reset.


```python
api.next_rate_limit_reset
```




    datetime.datetime(2016, 11, 11, 11, 6, 5)



Every repository has a list of collaborators, whose usernames are retrieved with:


```python
[user.login for user in repository.collaborators.list()]
```




    ['QuicksilverMachine']



Repository owner is retrieved with:


```python
user = repository.owner
```

The add function causes an invitation to be sent to a user for them to be added to a repository collaborator list, however in this case we can't add the owner of the repository as a collaborator, so the libraty raises an exception with the error message from the GitHub response.


```python
repository.collaborators.add(user)
```


    ---------------------------------------------------------------------------

    ResponseError                             Traceback (most recent call last)

    <ipython-input-12-015e66a41f03> in <module>()
    ----> 1 repository.collaborators.add(user)
    

    /home/dejan/Desktop/seven/github_api/github/models.py in add(self, collaborator)
        242         )
        243         if response.status_code != HTTPStatus.OK:
    --> 244             API.raise_response_error(response)
        245 
        246 


    /home/dejan/Desktop/seven/github_api/github/models.py in raise_response_error(response)
         39             errors = [r['message'] for r in response_dict['errors']]
         40             message += " - " + ', '.join(errors)
    ---> 41         raise exceptions.ResponseError(message)
         42 
         43     @staticmethod


    ResponseError: Validation Failed - Repository owner cannot be a collaborator



```python

```
