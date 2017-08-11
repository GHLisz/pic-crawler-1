import unittest

from utils.web import get_soup_from_url
from utils.db import read_existing_data_in_db, write_unique_to_db
from site.pic import Pic
from configs import database_name


class GeneralSet:
    def __init__(self, url, post_time, view_count, soup=None, database_name=database_name):
        self._url = str(url)
        self._soup = soup
        self._post_time = post_time
        self._view_count = view_count
        self._data = None
        self._database_name = database_name

    def soup(self):
        if self._soup is not None:
            return self._soup

        self._soup = get_soup_from_url(self._url)
        return self._soup

    def data(self):
        if self._data is not None:
            return self._data
        soup = self.soup()

        # test if set is available, eg: '/TouTiao/xinrou.html'
        set_available = len(soup.select('div.img > p > img')) > 0 or len(soup.select('div.imga > p > img')) > 0

        # test if page contains downloadable pic package or video
        contains_download = len(soup.select('div.page > a')) == 0 \
            and len(soup.select('div.img > p > a')) > 0 \
            and (not soup.select('div.img > p > a')[0].get('href').startswith('/')) \
            and set_available    # '/TouTiao/rushentehuiheji.html'

        _type = 'pic'
        _format, _size, download_provider, download_url, download_password = None, None, None, None, None
        if contains_download:
            is_video = '视频' in soup.select('div.img > p:nth-of-type(2)')[0].get_text()
            if is_video:
                _type = 'dVideo'
                _format = soup.select('div.img > p:nth-of-type(2)')[0].get_text().replace('视频格式：', '')
                _size = soup.select('div.img > p:nth-of-type(3)')[0].get_text().replace('视频大小：', '')
                download_provider = soup.select('div.img > p:nth-of-type(4)')[0].get_text().replace('下载方式：', '')
                download_url = soup.select('div.img > p > a')[0].get('href')
                download_password = soup.select('div.img > p:nth-of-type(5)')[0].get_text().split('密码：')[1]
            else:
                _type = 'dPic'
                _format = soup.select('div.img > p:nth-of-type(3)')[0].get_text().replace('文件格式：', '')
                _size = soup.select('div.img > p:nth-of-type(2)')[0].get_text().replace('文件大小：', '')
                download_provider = None
                download_url = soup.select('div.img > p > a')[0].get('href')
                # download_password = soup.select('div.img > p:nth-of-type(5)')[0].get_text().split('密码：')[1]
                try:
                    download_password = soup.find_all(text=download_url)[0].parent.parent.text.split('密码：')[1]
                except IndexError:
                    download_password = soup.text.split(download_url)[1].split('密码：')[1][0:4]
                # print(download_password)

        # get model name
        intro = soup.select('div.ina > p')[0].get_text().strip() \
            if soup.select('div.ina > p') \
            else soup.select('div.ina').get_text()
        try:
            model_name = soup.select('div.ina a:nth-of-type(2) > b')[0].get_text()
        except IndexError:
            try:
                model_name = intro.split('出镜模特：')[1]  # pic_set_url = '/Tgod/chan.html'
            except:
                model_name = soup.find_all(text=self._url)[0].parent.text

        cover_img_url = soup.select('td[width="215"] > img')[0].get('src')

        self._data = {
            'url': self._url,
            'coverImgUrl': cover_img_url,
            'channelUrl': '/{}/'.format(self._url.split('/')[1]),
            'title': self.soup().select('div.title')[0].get_text(),
            'subTitle': self.soup().select('tr[height="18"] > td[bgcolor="dbdbdb"]')[0].get_text().strip(),
            'modelName': model_name,
            'viewCount': self._view_count,
            'postTime': self._post_time,
            'intro': intro,  # original ends here
            'format': _format,
            'size': _size,
            'downloadProvider': download_provider,
            'downloadUrl': download_url,
            'downloadPassword': download_password,
            'type': _type,
        }
        return self._data

    def sub_page_urls(self):
        url_list = sorted(set([i.get('href') for i in self.soup().select('div.page > a')]))
        return url_list if url_list else [self._url, ]

    def children_data_list(self):
        pic_urls = []
        pic_data_list = []
        for page_url in self.sub_page_urls():
            soup = get_soup_from_url(page_url)
            pic_urls_data = soup.select('div.img > p > img')
            if not pic_urls_data:  # special case for /Ugirls_App/
                pic_urls_data = soup.select('div.imga > p > img')
            pic_urls.extend([i.get('src') for i in pic_urls_data])
        for pic_url in pic_urls:
            if pic_url:
                pic_data = Pic(pic_url, self._url).data()
                pic_data_list.append(pic_data)
        return pic_data_list

    def write_unique_children_data_to_db(self):
        existing_pic_sets_in_pic_collection = read_existing_data_in_db('pics', 'setUrl', self._database_name)
        if self._url not in existing_pic_sets_in_pic_collection:
            data_list = self.children_data_list()
            write_unique_to_db('pics', 'url', data_list, self._database_name)
        pass


class PicSetTestCase(unittest.TestCase):
    from datetime import datetime
    set_url = '/Ugirls_App/xiaoxiao_300f3bf5.html'  # pic
    # set_url = '/Beautyleg/Beautyleg-xiezhen-0001-qi.html'  # dPic
    # set_url = '/108TV/linmeichen.html'  # dVideo
    # set_url = '/TouTiao/xinxin.html'
    # set_url = '/TouTiao/xinrou.html'  # 下架资源
    # set_url = '/MiiTao/Gina.html'  # 单页但不是下架资源
    # set_url = '/Beautyleg/Beautyleg-xiezhen-0051-qi.html' # 密码位置不对
    # set_url = '/TouTiao/dadandan.html'   # 另一种密码位置
    # set_url = '/TouTiao/rushentehuiheji.html'  # 是否可下载判断错误

    pic_set = GeneralSet(set_url, datetime.now(), 1234, database_name='unittestdb')

    def setUp(self):
        pass

    def test_data(self):
        data = self.pic_set.data()
        print(data)
        return
        url = data['url']
        self.assertEqual(url, self.set_url)
        channel_url = data['channelUrl']
        self.assertEqual(channel_url, '/Ugirls_App/')
        model_name = data['modelName']
        self.assertEqual(model_name, '潇潇')

    # @unittest.skip
    def test_write_unique_children_data_to_db(self):
        self.pic_set.write_unique_children_data_to_db()
        self.existing_pic_urls = read_existing_data_in_db('pics', 'url', 'unittestdb')
        self.existing_pic_set_url = sorted(set(read_existing_data_in_db('pics', 'setUrl', 'unittestdb')))
        self.assertEqual(len(self.existing_pic_urls), 40)
        self.assertEqual(len(self.existing_pic_set_url), 1)
        self.assertEqual(self.existing_pic_set_url[0], self.set_url)

    def tearDown(self):
        import pymongo
        self.client = pymongo.MongoClient('localhost', 27017)
        self.client.drop_database('unittestdb')
        self.client.close()

if __name__ == '__main__':
    unittest.main()

