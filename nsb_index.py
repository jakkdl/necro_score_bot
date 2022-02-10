import pickle
from nsb_config import options
import nsb_steam
import nsb_database


class index:
    def __init__(self):  # , saveToFile=True):
        self.path = options['data'] + 'leaderboards.xml'
        self.data = None

    def fetch(self):
        url = nsb_steam.leaderboardUrl()
        response = nsb_steam.fetchUrl(url)
        self.data = nsb_database.xmlToList(response=response, responseType='index')

    def read_pickle(self):
        with open(self.path, 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.data = pickle.load(f)

    def read_xml(self):
        self.data = nsb_database.xmlToList_file(self.path, responseType='index')

    def write(self):
        with open(self.path, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def entries(self):
        if self.data is None:
            raise Exception('Read or fetch data first')
        return self.data
