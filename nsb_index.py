import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Literal
from os.path import join

import requests

from nsb_config import options
import nsb_steam_board

Sources = Literal["fetch", "pickle", "read"]


@dataclass
class Index:  # pylint: disable=too-few-public-methods
    def __init__(self, source: Sources = "fetch"):
        self.boards: list[nsb_steam_board.SteamBoard] = []

        if source == "fetch":
            self._fetch()
        elif source == "read":
            self._read()
        elif source == "pickle":
            with open(join(options["data"], "leaderboards.pickle"), "rb") as file:
                self.boards = pickle.load(file)

    def _read(self) -> None:
        tree = ET.parse(join(options["data"] + "leaderboards.xml"))
        root = tree.getroot()
        self._parse_xml(root)

    def _fetch(self) -> None:
        url = "http://steamcommunity.com/stats/247080/leaderboards/?xml=1"
        response = requests.get(url)
        text = response.text
        xml_data = ET.fromstring(text)
        self._parse_xml(xml_data)

    def _parse_xml(self, xml_data: ET.Element) -> None:

        for entry in xml_data[3:]:
            values: dict[str, str] = {}

            for key in "url", "name", "display_name":
                data_entry = entry.find(key)
                if data_entry is None:
                    raise ValueError(f"Failed to find entry {key} for board {entry}")
                value = data_entry.text
                if not isinstance(value, str):
                    raise TypeError(
                        f"Invalid type {type(value)}, value {value} for {key}, expected str"
                    )
                values[key] = value

            self.boards.append(nsb_steam_board.SteamBoard(**values))

    def write(self) -> None:
        with open(join(options["data"], "leaderboards.pickle"), "wb") as file:
            pickle.dump(self.boards, file, pickle.HIGHEST_PROTOCOL)
