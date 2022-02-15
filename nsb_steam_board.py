import datetime

import nsb_database
import nsb_steam
import nsb_leaderboard

from nsb_config import options

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

toofz_character_diffs = {"all char": "all-characters",
        "all chars dlc": "all-characters-amplified",
        "story mode": "story-mode"}

class SteamBoard(nsb_leaderboard.Leaderboard):
    def __init__(self, index_entry):
        name = index_entry["name"].lower()
        super().__init__(name)

        self.display_name = index_entry["display_name"]
        self.name = name
        self._url = index_entry["url"]
        # self._character = _extract_character(name)
        self.mode = self._extract_mode()
        # self._date = self._extract_date(name)
        # self._seeded = _check_seeded(name)
        # self._coop = _check_coop(name)
        # self._custom_music = _check_custom_music(name)
        # self._dlc = _check_dlc(name)
        # self._extra = _check_extra_modes(name)

    def fetch(self):
        # url = nsb_steam.boardUrl(self.lbid, 1, 100)
        response = nsb_steam.fetchUrl(self._url)
        self.data = nsb_database.xml_to_list(response, "leaderboard")

    def __str__(self):
        return self.display_name

    def _extract_mode(self):
        if "/" in self.name:
            return "daily"
        if "speedrun" in self.name and "deathless" in self.name:
            return None
        if "deathless" in self.name:
            return "deathless"
        if "speedrun" in self.name:
            return "speedrun"
        if "hardcore" in self.name:
            return "score"
        print(f"unknown mode in board {self.name}")
        return None

    def _extra_modes(self):
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

    def _character(self):
        for i in names:
            if i in self.name:
                return i

        # doing a fancy check is more likely to break than just assuming
        # that we're left with cadence
        return "cadence"

    def _date(self):
        if self.mode != "daily":
            return None
        name = self.name
        name = name.replace("_dev", "")
        name = name.replace("_prod", "")
        split = name.split()[0]
        split = split.split("/")
        return datetime.date(int(split[2]), int(split[1]), int(split[0]))

    #def maxLeaderboardEntries(self):
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

    #def maxCompareEntries(self):
    #    return 100




    def impossible_score(self, data):
        return self.mode == "score" and data["points"] > options["impossible_score"]

    def pretty_url(self, person=None):
        def toofz_support():
            if "coop" in self.name or "custom_music" in self.name:
                return False
            if not self.mode:
                return False
            if len(self._extra_modes()) > 1:
                print("toofz doesnt support >1 extra modes")
                return False
            return True
        def toofz_url():
            base = "https://crypt.toofz.com/leaderboards/"
            if "dlc" in self.name:
                base += "amplified/"

            if self.mode == "daily":
                # return base + 'Daily/' + self._date.strftime('%Y/%m/%d/')
                return base + "daily?date=" + self._date().strftime("%Y-%m-%d")
            # https://crypt.toofz.com/leaderboards/daily?date=2015-05-27

            char = self._character()
            char = toofz_character_diffs.get(char, char)

            mode = self.mode
            if "seeded" in self.name:
                mode = "seeded-" + mode
            if self._extra_modes():
                mode += "/" + self._extra_modes()[0].replace(" ", "-")
            return f"{base}{char}{mode}"
        if not toofz_support():
            return ""

        url = toofz_url()
        if person is None:
            return url

        if self.mode == "daily":
            return url
        return url + "?id=" + str(person["steam_id"])
