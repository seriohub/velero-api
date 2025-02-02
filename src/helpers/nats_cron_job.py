class NatsCronJob:
    def __init__(self, endpoint: str,
                 credential_required: bool,
                 interval: int):
        self._endpoint = endpoint
        self._cr = credential_required
        self._interval = interval
        self.__from_last_publish_sec = interval + 1

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str):
        self._endpoint = value

    @property
    def credential(self):
        return self._cr

    @credential.setter
    def credential(self, value: bool):
        self._cr = value

    @property
    def interval(self):
        return self._interval

    @property
    def ky_key(self):
        return self._endpoint.replace("/", "_")

    @property
    def get_data(self):
        return {'endpoint': self._endpoint,
                'credential': self._cr,
                'intervals': self._interval,
                'kv_key': self.ky_key}

    @property
    def time_elapsed(self):
        return self.__from_last_publish_sec

    @time_elapsed.setter
    def time_elapsed(self, value: int):
        self.__from_last_publish_sec += value

    @property
    def is_elapsed(self):
        return self.__from_last_publish_sec > self._interval

    def reset_timer(self):
        self.__from_last_publish_sec = 0
