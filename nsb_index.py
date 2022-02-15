import pickle
from nsb_config import options
import nsb_steam
import nsb_database


class Index:
    def __init__(self):  # , saveToFile=True):
        self.path = options["data"] + "leaderboards.xml"
        self.data = None

    def fetch(self):
        url = nsb_steam.leaderboard_url()
        response = nsb_steam.fetch_url(url)
        self.data = nsb_database.xml_to_list(response=response, response_type="index")

    def read_pickle(self):
        with open(self.path, "rb") as file:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.data = pickle.load(file)

    def read_xml(self):
        self.data = nsb_database.xml_to_list(self.path, response_type="index")

    def write(self):
        with open(self.path, "wb") as file:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.data, file, pickle.HIGHEST_PROTOCOL)

    def entries(self):
        if self.data is None:
            raise Exception("Read or fetch data first")
        return self.data
