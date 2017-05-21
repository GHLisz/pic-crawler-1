import logging

from configs import log_path, error_list_path


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(file_handler)
    l.addHandler(stream_handler)

setup_logger('prj_logger', log_path)
setup_logger('error_list', error_list_path)
prj_logger = logging.getLogger('prj_logger')
error_list_logger = logging.getLogger('error_list')