RATE_LIMIT_URL = "https://api.github.com/rate_limit"

AUTHENTICATED_USER = "https://api.github.com/user"
CURRENT_USER_REPOSITORIES_URL = "https://api.github.com/user/repos"
REPOSITORY_URL = "https://api.github.com/repos/{full_name}"

COLLABORATORS_LIST_URL = "http://api.github.com/repos/{full_name}/" \
                         "collaborators"
COLLABORATOR_URL = "http://api.github.com/users/{login}"
COLLABORATOR_ADD_URL = "http://api.github.com/repos/{full_name}/" \
                       "collaborators/{{login}}"
