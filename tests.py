import unittest
from github import models


class TestAPIObject(unittest.TestCase):
    token = "12345"

    def test_api_object_creation(self):
        api = models.API(token=self.token)
        self.assertEqual(api.token, self.token)

    def test_api_reference(self):
        api = models.API(token=self.token)
        repository_collection = models.APIRepositoryCollection(api)

        api.token = "54321"
        self.assertEqual(api.token, repository_collection._api.token)


if __name__ == '__main__':
    unittest.main()
