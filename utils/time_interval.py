import random


class TimeInterval:
    call_count = 0

    def __init__(self, download_interval=5, rest_interval=60, rest_freq=100):
        self._download_interval = download_interval
        self._rest_interval = rest_interval
        self._rest_freq = rest_freq

    def get_interval(self):
        if self.call_count <= self._rest_freq:
            self.call_count += 1
            if self._download_interval <= 2:
                return 0
            else:
                return random.randint(self._download_interval - 2, self._download_interval + 2)
        else:
            self.call_count = 0
            return random.randint(self._rest_interval - 20, self._rest_interval + 20)