import os

host_url = ''
database_name = 'testdb'
pic_root_folder = 'Z:/sppic'

channel_blacklist = [
    '/',  # host root
    '/XiuRen.html',  # A super channel, all its sub_channels are already included.
    '/meinvshipin.html',  # A super channel, which contains items not found in the index page.
]

current_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_path, 'log', 'log.txt')
error_list_path = os.path.join(current_path, 'log', 'error_list.txt')

if not os.path.exists(os.path.join(current_path, 'log')):
    os.makedirs(os.path.join(current_path, 'log'))
