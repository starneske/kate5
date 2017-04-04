#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['KATE5_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['KATE5_MONGOALCHEMY_SERVER'] = ''
    os.environ['KATE5_MONGOALCHEMY_PORT'] = ''
    os.environ['KATE5_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.kate5 import kate5
    from qube.src.services.kate5service import kate5Service
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, kate5ServiceError


class Testkate5Service(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.kate5Service = kate5Service(context)
        self.kate5_api_model = self.createTestModelData()
        self.kate5_data = self.setupDatabaseRecords(self.kate5_api_model)
        self.kate5_someoneelses = \
            self.setupDatabaseRecords(self.kate5_api_model)
        self.kate5_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.kate5_someoneelses.save()
        self.kate5_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.kate5_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.kate5_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, kate5_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            kate5_data = kate5(name='test_record')
            for key in kate5_api_model:
                kate5_data.__setattr__(key, kate5_api_model[key])

            kate5_data.description = 'my short description'
            kate5_data.tenantId = "23432523452345"
            kate5_data.orgId = "987656789765670"
            kate5_data.createdBy = "1009009009988"
            kate5_data.modifiedBy = "1009009009988"
            kate5_data.createDate = str(int(time.time()))
            kate5_data.modifiedDate = str(int(time.time()))
            kate5_data.save()
            return kate5_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_kate5(self, *args, **kwargs):
        result = self.kate5Service.save(self.kate5_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.kate5_api_model['name'])
        kate5.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_kate5(self, *args, **kwargs):
        self.kate5_api_model['name'] = 'modified for put'
        id_to_find = str(self.kate5_data.mongo_id)
        result = self.kate5Service.update(
            self.kate5_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.kate5_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_kate5_description(self, *args, **kwargs):
        self.kate5_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.kate5_data.mongo_id)
        result = self.kate5Service.update(
            self.kate5_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.kate5_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_kate5_item(self, *args, **kwargs):
        id_to_find = str(self.kate5_data.mongo_id)
        result = self.kate5Service.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_kate5_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(kate5ServiceError):
            self.kate5Service.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_kate5_list(self, *args, **kwargs):
        result_collection = self.kate5Service.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.kate5_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.kate5_data.mongo_id)
        with self.assertRaises(kate5ServiceError) as ex:
            self.kate5Service.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.kate5_data.mongo_id)
        self.kate5Service.auth_context.is_system_user = True
        self.kate5Service.delete(id_to_delete)
        with self.assertRaises(kate5ServiceError) as ex:
            self.kate5Service.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.kate5Service.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.kate5_someoneelses.mongo_id)
        with self.assertRaises(kate5ServiceError):
            self.kate5Service.delete(id_to_delete)
