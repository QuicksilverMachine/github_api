import json
import unittest
from github import models, fields


class TestAPIObject(unittest.TestCase):
    """Class to test the API functionality"""
    token = "12345"

    def test_api_object_creation(self):
        """Test creating of an object of API class"""
        api = models.API(token=self.token)
        self.assertEqual(api.token, self.token)

    def test_api_reference(self):
        """Test if api in model instances is a reference to the caller
        api object
        """
        api = models.API(token=self.token)
        repository_collection = models.APIRepositoryCollection(api)
        api.token = "54321"
        self.assertEqual(api.token, repository_collection._api.token)


class ModelTest(unittest.TestCase):
    """Class to test the Model functionality"""
    class TestModel(models.APIModel):
        id = fields.IntegerField()

    def test_model_property_set(self):
        """Test setting of properties to model instances"""
        m = self.TestModel(id=1)
        m.id = 2
        self.assertEqual(m.id, 2)

    def test_model_dict_serialization(self):
        """Test serialization of a model to a dictionary"""
        m = self.TestModel(id=1)
        serialized = {'id': 1}
        self.assertEqual(m.serialize_to_dict(), serialized)

    def test_model_json_serialization(self):
        """Test serialization of a model to a json object"""
        m = self.TestModel(id=1)
        serialized = json.dumps({'id': 1})
        self.assertEqual(m.serialize_to_json(), serialized)

    def test_model_set_data(self):
        """Test function that sets data to model fields"""
        m = self.TestModel(id=1)
        data = {'id': 5}
        m.set_data(data=data)
        self.assertEqual(m.id, 5)

if __name__ == '__main__':
    unittest.main()
