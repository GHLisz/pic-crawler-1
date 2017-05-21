from site.index import Index
from site.channel import Channel
from site.general_set import GeneralSet
from configs import host_url
from utils.db import read_existing_data_in_db
from utils.logger import prj_logger, error_list_logger
from utils.down_pic import download_all_pics_incremental


def db_insert_all_channels_incremental():
    index = Index(host_url)
    index.write_unique_children_data_to_db()


def db_insert_all_pic_sets_incremental():
    channel_urls = read_existing_data_in_db('channels', 'url')

    cur, total = 0, len(channel_urls)
    for channel_url in channel_urls:
        cur += 1
        prj_logger.info('Start visiting channel: {}'.format(channel_url))
        channel = Channel(channel_url)
        try:
            channel.write_unique_children_data_to_db()
        except:
            error_list_logger.info('Error occurred processing: {} in {}'.
                                   format(host_url+channel_url, 'channel.write_unique_children_data_to_db()'))
        prj_logger.info('{}/{}, {}% complete. Finished visiting channel: {}'.format(
            cur, total, format(cur/total*100, '0.2f'), channel_url))


def db_insert_all_pics_incremental():
    set_data = read_existing_data_in_db('picSets', 'url', return_full_doc=True)
    existing_sets_in_pic_collection = read_existing_data_in_db('pics', 'setUrl')
    exe_list = [data for data in set_data if data['url'] not in existing_sets_in_pic_collection]

    cur, total = 0, len(exe_list)
    for data in exe_list:
        cur += 1
        url = data['url']
        post_time = data['postTime']
        view_count = data['viewCount']
        prj_logger.info('Start visiting set: {}'.format(url))

        _set = GeneralSet(url, post_time, view_count)
        try:
            _set.write_unique_children_data_to_db()
        except:
            error_list_logger.info('Error occurred processing: {} in {}'.
                                   format(host_url+url, 'pic_set.write_unique_children_data_to_db()'))
        prj_logger.info('{}/{}, {}% complete. Finished visiting set: {}'.format(
            cur, total, format(cur/total*100, '0.2f'), url))


if __name__ == '__main__':
    db_insert_all_channels_incremental()
    db_insert_all_pic_sets_incremental()
    db_insert_all_pics_incremental()
    download_all_pics_incremental()
