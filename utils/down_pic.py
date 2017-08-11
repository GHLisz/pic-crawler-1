import os
import sys
import time
import urllib.request
import requests
import pymongo
from configs import database_name, host_url, pic_root_folder

TIMEOUTSEC = 300


def save_pic_from_url_wrapper(pic_url, root_folder=pic_root_folder):
    if False:
        pass
    else:
        pic_path = root_folder + pic_url
        pic_folder = os.path.dirname(pic_path)
        os.makedirs(pic_folder, exist_ok=True)
        if os.path.exists(pic_path):
            return
        print('Downloading: ' + pic_url)
        save_pic_from_url(host_url + pic_url, pic_path)


def save_pic_from_url(pic_url, pic_path, ref=host_url):
    try:
        f = open(pic_path, 'wb')
        content = requests.get(pic_url,
                               headers={'referer': ref},
                               timeout=TIMEOUTSEC).content
        f.write(content)
        f.close()
    except urllib.error.HTTPError as err:
        if err.code in [403, 404, 503, 504]:
            print(sys.exc_info())
        else:
            time.sleep(5)
            print(sys.exc_info())
            return False
    except:
        time.sleep(5)
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


def update_db_according_to_file_complete():
    client = pymongo.MongoClient('localhost', 27017)
    db = client[database_name]
    cursor = db['pics'].find(no_cursor_timeout=True)
    for i in cursor:
        url = i['url']
        print(url)
        file_name = pic_root_folder + url
        if os.path.isfile(file_name):
            i['filePath'] = 1
        else:
            i['filePath'] = None
            print('Not Found')
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
        save_pic_from_url_wrapper(url)
        print('{}/{}, {}% complete. Finished downloading: {}'.format(
            cur + 1, total, format((cur+1)/total*100, '0.2f'), url))

    cursor = db['pics'].find({'filePath': None})
    pic_url_list = [i['url'] for i in cursor]
    total = len(pic_url_list)
    print('Total urls: ' + str(total))
    for cur, url in enumerate(pic_url_list):
        save_pic_from_url_wrapper(url)
        print('{}/{}, {}% complete. Finished downloading: {}'.format(
            cur + 1, total, format((cur+1)/total*100, '0.2f'), url))

    update_db_according_to_file()

if __name__ == '__main__':
    # update_db_according_to_file_complete()
    pass
