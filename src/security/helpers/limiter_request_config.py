class LimiterRequestConfig:
    def __init__(self, level=1, seconds=60, request=10):
        self._level = level
        self._seconds = seconds
        self._request = request

    @property
    def level(self):
        """The level property."""
        return self._level

    @property
    def seconds(self):
        """The seconds' property."""
        return self._seconds

    @property
    def max_request(self):
        """The max_request property."""
        return self._request