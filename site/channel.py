import unittest

from datetime import datetime
from utils.web import get_soup_from_url
from site.general_set import GeneralSet
from utils.db import read_existing_data_in_db, write_unique_to_db
from configs import database_name


class Channel:
    def __init__(self, url, soup=None, database_name=database_name, sub_collection_name='picSets'):
        self._url = url
        self._soup = soup
        self._data = None
        self._database_name = database_name
        self._sub_collection_name = sub_collection_name

    def soup(self):
        if self._soup is not None:
            return self._soup

        self._soup = get_soup_from_url(self._url)
        return self._soup

    def data(self):
        if self._data is not None:
            return self._data

        self._data = {
            'url': self._url,
            'title': self.soup().select('td[style="font-size:14px;"] > b > a')[1].get_text(),
            'intro': self.soup().select('p.list')[0].get_text().strip(),
        }
        return self._data

    def sub_page_urls(self):
        page_urls = []
        pages = self.soup().select('div.page > a')

        if pages[-1].get_text() == "尾页":
            last_page_index = pages[-1].get('href').split('index')[1].split('.')[0]
            page_urls = ['{}index{}.html'.format(self._url, str(index)) for index in range(2, int(last_page_index)+1)]
            page_urls.append(self._url)
        else:
            page_urls = sorted(set([i.get('href') for i in self.soup().select('div.page > a')]))

        return page_urls

    def children_data_list_not_in_db(self):
        existing_set_in_db = read_existing_data_in_db(self._sub_collection_name, 'url', self._database_name)
        set_list = []
        for page_url in self.sub_page_urls():
            soup = self.soup() if page_url == self._url else get_soup_from_url(page_url)
            pic_set_data_in_this_page = soup.select('div.biank1')
            for i in pic_set_data_in_this_page:
                pic_set_url = i.find('a').get('href')
                if pic_set_url in existing_set_in_db:
                    continue

                text_list = i.text.replace('HOT:', '更新:').split('更新:')
                post_time = datetime.strptime(text_list[1], '%Y年%m月%d日')
                view_count = int(text_list[2])
                pic_set = GeneralSet(pic_set_url, post_time, view_count)
                set_list.append(pic_set)
        return [i.data() for i in set_list]

    def write_unique_children_data_to_db(self):
        unique_data_list = self.children_data_list_not_in_db()
        write_unique_to_db(self._sub_collection_name, 'url', unique_data_list, self._database_name)


class ChannelTestCase(unittest.TestCase):
    channel_url = '/YouMi/'
    # channel_url = '/108TV/'
    # channel_url = '/Beautyleg/'
    # channel_url = '/YouWu/'
    channel = Channel(channel_url, database_name='unittestdb')
    pic_sets_data = [{
        'postTime': 11,
        'channelUrl': '/YouMi/',
        'title': 'title',
        'intro': 'intro',
        'viewCount': 1059,
        'url': '/YouMi/zhouyanlin_dd8c708f.html',
        'modelName': 'modelName',
        'subTitle': 'subTitle'
    }, {
        'postTime': 11,
        'channelUrl': '/YouMi/',
        'title': 'title',
        'intro': 'intro',
        'viewCount': 1059,
        'url': '/YouMi/yingxiaobai.html',
        'modelName': 'modelName',
        'subTitle': 'subTitle'
    }]
    write_unique_to_db('picSets', 'url', pic_sets_data, 'unittestdb')

    def setUp(self):
        pass

    def test_data(self):
        data = self.channel.data()
        print(data)
        url = data['url']
        self.assertEqual(url, self.channel_url)
        title = data['title']
        self.assertEqual(title, '尤蜜荟')

    def test_sub_page_urls(self):
        page_urls = self.channel.sub_page_urls()
        print(page_urls)
        self.assertTrue(len(page_urls) >= 2)
        self.assertTrue('/YouMi/' in page_urls)

    def test_children_data_list_not_in_db(self):
        children_data_list_not_in_db = self.channel.children_data_list_not_in_db()
        print(*children_data_list_not_in_db, sep='\n')
        for data in children_data_list_not_in_db:
            self.assertTrue(data['url'] not in [i['url'] for i in self.pic_sets_data])

    def test_write_unique_children_data_to_db(self):
        self.channel.write_unique_children_data_to_db()
        self.existing_pic_set_url = sorted(set(read_existing_data_in_db('picSets', 'url', 'unittestdb')))
        self.assertTrue(len(self.existing_pic_set_url) > 2)

    # @unittest.skip
    def tearDown(self):
        import pymongo
        self.client = pymongo.MongoClient('localhost', 27017)
        self.client.drop_database('unittestdb')
        self.client.close()

if __name__ == '__main__':
    unittest.main()
