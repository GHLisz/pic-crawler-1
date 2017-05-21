class Pic:
    def __init__(self, url, pic_set_url):
        self._url = url
        self._pic_set_url = pic_set_url

    def data(self):
        _data = {
            'setUrl': self._pic_set_url,
            'url': self._url,
            'filePath': None,
        }
        return _data
