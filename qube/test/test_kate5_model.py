#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class Testkate5Model(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_kate5_model(self):
        from qube.src.models.kate5 import kate5
        kate5_data = kate5(name='testname')
        kate5_data.tenantId = "23432523452345"
        kate5_data.orgId = "987656789765670"
        kate5_data.createdBy = "1009009009988"
        kate5_data.modifiedBy = "1009009009988"
        kate5_data.createDate = str(int(time.time()))
        kate5_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            kate5_data.save()
            self.assertIsNotNone(kate5_data.mongo_id)
            kate5_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
