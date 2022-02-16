import pickle
from nsb_config import options
import nsb_steam
import nsb_database


class Index:
    def __init__(self, source: str = "fetch"):
        self.path = options["data"] + "leaderboards.xml"
        if source == "fetch":
            self.data = self._fetch()
        elif source == "pickle":
            with open(self.path, "rb") as file:
                self.data = pickle.load(file)
        elif source == "read_xml":
            self.data = nsb_database.xml_to_list(self.path, response_type="index")
        else:
            raise ValueError("source must be one of 'fetch', 'pickle', 'read_xml'")

    @staticmethod
    def _fetch() -> list[dict[str, str]]:
        url = nsb_steam.leaderboard_url()
        response = nsb_steam.fetch_url(url)
        return nsb_database.xml_to_list(response=response, response_type="index")

    def write(self) -> None:
        with open(self.path, "wb") as file:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.data, file, pickle.HIGHEST_PROTOCOL)

    def entries(self) -> list[dict[str, str]]:
        return self.data
