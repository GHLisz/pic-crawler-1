import pymongo
from datetime import datetime
from configs import database_name

last_download_time = datetime(2017, 5, 17)

db_client = pymongo.MongoClient('localhost', 27017)
db = db_client[database_name]
pic_sets = db['picSets']

for data in pic_sets.find():
    if data['postTime'] > last_download_time:
        if data['type'] == 'dPic' and False:
            print(data['title'])
            print(data['postTime'])
            print(data['downloadUrl'] + '  ----  ' + data['downloadPassword'])
        if data['type'] == 'dVideo':
            print(data['title'])
            print(data['postTime'])
            print(data['downloadUrl'] + '  ----  ' + data['downloadPassword'])
