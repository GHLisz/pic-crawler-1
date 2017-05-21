from configs import database_name
import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client[database_name]
pic_sets = db['picSets']

pics = db['pics']

print(pics.count())
