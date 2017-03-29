import nsb_entry


class board:
    def __init__(self, name, url):
        self._name = name
        self._url = url

        self._data = None
        self._history = None
        self._path = None

    def _get_common(self, num, data):
        if data == None:
            raise Exception('Data unavailable')
        num = min(num, len(data))
        return nsb_entry.generate_entries(data[:num])


    def get_top(self, num=10):
        return _get_common(num, self._data)

    def get_top_history(self, num=10):
        return _get_common(num, self._history)

