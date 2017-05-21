import unittest

from utils.web import get_soup_from_url
from utils.logger import prj_logger
from utils.db import read_existing_data_in_db, write_unique_to_db
from site.channel import Channel
from configs import database_name, host_url, channel_blacklist


class Index:
    def __init__(self, url, sub_collection_name='channels', database_name=database_name):
        self._url = str(url)
        self._sub_collection_name = sub_collection_name
        self._database_name = database_name
        self._soup = None

    def soup(self):
        if self._soup is not None:
            return self._soup

        self._soup = get_soup_from_url(self._url, False)
        return self._soup

    def children_data_list_not_in_db(self):
        channel_urls = []
        # list all pic channels
        soup = self.soup()
        channel_url_data = soup.find_all('div', class_=['lm1', 'qttt', 'qttt1'])
        for i in channel_url_data:
            prj_logger.info(i)
            try:
                channel_url = i.contents[0].get('href')
                if not (channel_url.endswith('/') or channel_url.endswith('.html')):
                    channel_url = channel_url + '/'
                channel_urls.append(channel_url)
            except:
                pass
        # list all video channels
        video_index_page = '/meinvshipin.html'
        video_index_soup = get_soup_from_url(video_index_page)
        v_channels = [i.get('href') for i in video_index_soup.select('td[height="45"] > a')]
        channel_urls.extend(v_channels)
        # remove dup
        print(len(channel_urls))
        channel_urls = sorted(set(channel_urls))
        print(len(channel_urls))
        print(channel_urls)

        # get each channel's data not in db
        channel_list = []
        existing_channels_in_channel_collection = read_existing_data_in_db('channels', 'url', self._database_name)
        for channel_url in channel_urls:
            if (channel_url in existing_channels_in_channel_collection) or (channel_url in channel_blacklist):
                continue
            channel_data = Channel(channel_url, database_name=self._database_name)
            channel_list.append(channel_data)
        return [i.data() for i in channel_list]

    def write_unique_children_data_to_db(self):
        unique_data_list = self.children_data_list_not_in_db()
        print(*unique_data_list, sep='\n')
        write_unique_to_db(self._sub_collection_name, 'url', unique_data_list, self._database_name)


class IndexTestCase(unittest.TestCase):
    index_url = host_url
    index = Index(index_url, database_name='unittestdb')

    def test_write_unique_children_data_to_db(self):
        self.index.write_unique_children_data_to_db()
        existing_data_in_db = read_existing_data_in_db('channels', 'url', database='unittestdb')
        self.assertTrue(len(existing_data_in_db) < 50)


if __name__ == '__main__':
    unittest.main()
