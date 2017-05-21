import os
import sys
import time
import urllib.request
import pymongo
from configs import database_name, host_url, pic_root_folder
import socket

socket.setdefaulttimeout(300)


def save_pic_from_url(pic_url, root_folder=pic_root_folder):
    pic_path = root_folder + pic_url
    pic_folder = os.path.dirname(pic_path)
    if not os.path.exists(pic_folder):
        os.makedirs(pic_folder)
    if os.path.exists(pic_path):
        return
    print('Downloading: ' + pic_url)
    try:
        urllib.request.urlretrieve(host_url+pic_url, pic_path)
    except:
        time.sleep(120)
        print(sys.exc_info())


def update_db_according_to_file():
    client = pymongo.MongoClient('localhost', 27017)
    db = client[database_name]
    cursor = db['pics'].find({'filePath': None}, no_cursor_timeout=True)
    for i in cursor:
        url = i['url']
        print(url)
        file_name = pic_root_folder + url
        if os.path.isfile(file_name):
            print(url)
            i['filePath'] = 1
            db['pics'].save(i)
    cursor.close()


def download_all_pics_incremental():
    # update_db_according_to_file()

    client = pymongo.MongoClient('localhost', 27017)
    db = client[database_name]

    cursor = db['picSets'].find()
    cover_img_url_list = [i['coverImgUrl'] for i in cursor]
    total = len(cover_img_url_list)
    print('Total urls: ' + str(total))
    for cur, url in enumerate(cover_img_url_list):
        save_pic_from_url(url)
        print('{}/{}, {}% complete. Finished downloading: {}'.format(
            cur, total, format(cur/total*100, '0.2f'), url))

    cursor = db['pics'].find({'filePath': None})
    pic_url_list = [i['url'] for i in cursor]
    total = len(pic_url_list)
    print('Total urls: ' + str(total))
    for cur, url in enumerate(pic_url_list):
        if url.startswith('http'):
            continue
        save_pic_from_url(url)
        print('{}/{}, {}% complete. Finished downloading: {}'.format(
            cur, total, format(cur/total*100, '0.2f'), url))

    update_db_according_to_file()


# download_all_pics_incremental()
