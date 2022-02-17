"This file contains the class for a normal Steam, Crypt of the NecroDancer leaderboard."

import datetime
import xml.etree.ElementTree as ET
from typing import Optional

import requests

import nsb_leaderboard
import nsb_entry
from nsb_config import options
from nsb_abc import NsbError, BoardEntry

##character
# All-Char DLC, All-Char, story mode, Aria, Bard, Bolt, Cadence, Coda, Diamond,
# Dorian, Dove, Eli, Mary, Melody, Monk, Nocturna, Tempo, None

##Mode
# Speed, Score, Deathless, Daily, None

##dlc
# True, False

##seeded
# True, False

##coop
# True, False

##customMusic
# True, False

##extras
extras = ["no return", "hard", "phasing", "mystery", "randomizer"]

names = [
    "all chars dlc",
    "all char",
    "story mode",
    "aria",
    "bard",
    "bolt",
    "coda",
    "dorian",
    "dove",
    "eli",
    "melody",
    "monk",
    "nocturna",
    "diamond",
    "tempo",
    "mary",
]

toofz_character_diffs = {
    "all char": "all-characters",
    "all chars dlc": "all-characters-amplified",
    "story mode": "story-mode",
}

xml_conversion_table = (
    ("steamid", "uid"),
    ("score", "points"),
    ("rank", "rank"),
)


class SteamBoard(nsb_leaderboard.Leaderboard):
    def __init__(self, url: str, name: str, display_name: str):
        super().__init__(name)

        self.display_name: str = display_name
        self._url: str = url
        self.mode: str = self._extract_mode()

    def fetch(self) -> None:
        # url = nsb_steam.board_url(self.lbid, 1, 100)
        # response = nsb_steam.fetch_url(self._url)
        response = requests.get(self._url)
        text = response.text
        xml = ET.fromstring(text)
        for index, element in enumerate(xml):
            if element.tag == "entries":
                break
        else:
            raise NsbError(f"No entries in steam board {self.name}")

        for entry in xml[index]:
            values: dict[str, int] = {}
            for field, target in xml_conversion_table:
                data_entry = entry.find(field)
                if data_entry is None:
                    raise ValueError(f"Failed to find entry {field} for board {entry}")
                if data_entry.text is None:
                    raise NsbError(f"no value for {field} in board {entry}")
                values[target] = int(data_entry.text)
            self.data.append(BoardEntry(**values))

    def __str__(self) -> str:
        return self.display_name

    def _extract_mode(self) -> str:
        if "/" in self.name:
            return "daily"
        if "speedrun" in self.name and "deathless" in self.name:
            return ""
        if "deathless" in self.name:
            return "deathless"
        if "speedrun" in self.name:
            return "speedrun"
        if "hardcore" in self.name:
            return "score"
        print(f"unknown mode in board {self.name}")
        return ""

    def _extra_modes(self) -> list[str]:
        extra_modes = []
        for mode in extras:
            if mode == "hard":
                if ("coda" in self.name) & ("hard mode" in self.name):
                    extra_modes.append(mode)
                elif "hard_prod" in self.name:
                    extra_modes.append(mode)
            elif mode in self.name:
                extra_modes.append(mode)
        return extra_modes

    def _character(self) -> str:
        for i in names:
            if i in self.name:
                return i

        # doing a fancy check is more likely to break than just assuming
        # that we're left with cadence
        return "cadence"

    def _date(self) -> datetime.date:
        assert self.mode == "daily"
        name = self.name
        name = name.replace("_dev", "")
        name = name.replace("_prod", "")
        name = name.split()[0]
        split = name.split("/")
        return datetime.date(int(split[2]), int(split[1]), int(split[0]))

    # def maxLeaderboardEntries(self):
    #    # if self._custom_music:
    #    # return 1
    #    if "coop" in self.name:
    #        return 3
    #    if "seeded" in self.name:
    #        return 5
    #    if self.mode in ("deathless", "score", "speed", "daily"):
    #        return 5
    #    if self.mode == "daily":
    #        return 3
    #    return None

    # def maxCompareEntries(self):
    #    return 100

    def impossible_score(self, data: BoardEntry) -> bool:
        return self.mode == "score" and data.points > options["impossible_score"]

    def pretty_url(self, person: Optional[nsb_entry.Entry] = None) -> str:
        def toofz_support() -> bool:
            if "coop" in self.name or "custom_music" in self.name:
                return False
            if not self.mode:
                return False
            if len(self._extra_modes()) > 1:
                print("toofz doesnt support >1 extra modes")
                return False
            return True

        def toofz_url() -> str:
            base = "https://crypt.toofz.com/leaderboards/"
            dlc = ""
            if "dlc" in self.name:
                dlc = "amplified/"

            if self.mode == "daily":
                return f"{base}{dlc}daily?date={self._date().strftime('%Y-%m-%d')}"
            # https://crypt.toofz.com/leaderboards/daily?date=2015-05-27

            seeded = ""
            extra_modes = ""

            char = self._character()
            char = toofz_character_diffs.get(char, char)

            if "seeded" in self.name:
                seeded = "seeded-"
            if self._extra_modes():
                extra_modes = "/" + self._extra_modes()[0].replace(" ", "-")

            return f"{base}{dlc}{char}{seeded}{self.mode}{extra_modes}"

        if not toofz_support():
            return ""

        url = toofz_url()
        if person is None:
            return url

        if self.mode == "daily":
            return url
        return f"{url}?id={person.steam_id}"
