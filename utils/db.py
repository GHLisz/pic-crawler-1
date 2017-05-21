import unittest
import pymongo
from configs import database_name


def read_existing_data_in_db(collection_name, key_name, database=database_name, return_full_doc=False):
    client = pymongo.MongoClient('localhost', 27017)
    db = client[database]
    collection = db[collection_name]
    existing_data_list = [i for i in collection.find()]
    client.close()
    if return_full_doc:
        return existing_data_list
    existing_partial_data_list = [i[key_name] for i in existing_data_list]
    return existing_partial_data_list


def write_unique_to_db(collection_name, unique_key, data_list, database=database_name):
    client = pymongo.MongoClient('localhost', 27017)
    db = client[database]
    collection = db[collection_name]
    existing_data = read_existing_data_in_db(collection_name, unique_key, database)

    for data in data_list:
        if data[unique_key] in existing_data:
            continue
        collection.insert_one(data)
    client.close()


class PicSetTestCase(unittest.TestCase):
    def setUp(self):
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client['unittestdb']
        self.collection = self.db['test_collection']
        self.collection.insert_one({
            'uniqueKey': '1',
            'trivialData': 11,
        })
        self.collection.insert_one({
            'uniqueKey': '2',
            'trivialData': 22,
        })

    def tearDown(self):
        self.client.drop_database('unittestdb')
        self.client.close()

    def test_get_existing_data(self):
        existing_data = read_existing_data_in_db('test_collection', 'uniqueKey', 'unittestdb')
        print(existing_data)
        self.assertEqual(existing_data, ['1', '2'])

    def test_write_unique_to_db(self):
        data_list = [{
            'uniqueKey': '1',
            'trivialData': 11,
        }, {
            'uniqueKey': '3',
            'trivialData': 11,
        }]
        write_unique_to_db('test_collection', 'uniqueKey', data_list, 'unittestdb')
        existing_data = read_existing_data_in_db('test_collection', 'uniqueKey', 'unittestdb')
        print(existing_data)
        self.assertEqual(existing_data, ['1', '2', '3'])


if __name__ == '__main__':
    unittest.main()
