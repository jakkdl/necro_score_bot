""" A parsed leaderboard entry, created when nsb_leaderboard detects an entry as significant."""
from __future__ import annotations
import json
import re
from typing import Optional, cast, TYPE_CHECKING

import requests

from nsb_config import options
from nsb_twitter import twitter
from nsb_abc import BoardEntry

if TYPE_CHECKING:
    import nsb_leaderboard

# I need both the __future__ annotations and TYPE_CHECKING to avoid
# circular import. Can alternatively create an abc.py with types.


class Entry:
    def __init__(
        self,
        data: BoardEntry,
        board: nsb_leaderboard.Leaderboard,
        template: str,
        hist_data: Optional[BoardEntry] = None,
    ):
        self.steam_id: int = data.uid

        self.linked_accounts: dict[str, str] = self._fetch_linked_handles()

        self.score = data
        self.prev_score = hist_data

        self.board: nsb_leaderboard.Leaderboard = board
        self.template: str = template

    def __str__(self) -> str:
        if "steam_name" in self.linked_accounts:
            return self.linked_accounts["steam_name"]
        return str(self.steam_id)

    def fetch_steamname(self) -> str:
        url = (
            f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            f"?key={options['steam_key']}&steamids={self.steam_id}"
        )
        obj = requests.get(url).json()
        name = obj["response"]["players"][0]["personaname"]
        assert isinstance(name, str)
        return name

    def get_twitter_handle(self) -> str:
        url = f"http://steamcommunity.com/profiles/{self.steam_id}"
        try:
            text = requests.get(url).text
        except requests.exceptions.ConnectionError as error:
            print(f"failed to fetch steam profile for {self.steam_id}, caught {error}")
        # text = decode_response(fetch_url(url), "latin-1")

        match: Optional[re.Match[str]] = re.search(
            r"twitter\.com\\/(?P<handle>\w+)\\\"", text
        )
        if match is None:
            return ""

        handle = match.group("handle")

        if not twitter:
            print("Warning: unverified handle")
            return handle
        if twitter.check_twitter_handle(handle):
            return handle

        print(f"{handle} in steam profile but not valid")
        return ""

    def necrolab_player(self) -> dict[str, dict[str, str]]:
        url = f"https://api.necrolab.com/players/player?steamid={self.steam_id}"
        obj = requests.get(url).json()

        return cast(dict[str, dict[str, str]], obj["data"]["linked"])

    def _fetch_linked_handles(self) -> dict[str, str]:
        handles = {"steam_name": "", "discord_id": "", "twitter_handle": ""}
        if options["necrolab"]:
            try:
                data = self.necrolab_player()
                handles["steam_name"] = data["steam"]["personaname"]
                handles["discord_id"] = data["discord"]["id"]
                handles["twitter_handle"] = data["twitter"]["name"]
            except (
                requests.exceptions.ConnectionError,
                json.decoder.JSONDecodeError,
            ) as error:
                print(f"caught {error} fetching necrolab data for {self.steam_id}")

        if not handles["steam_name"] and options["steam_key"]:
            handles["steam_name"] = self.fetch_steamname()

        if not handles["twitter_handle"] and options["steam_key"]:
            handles["twitter_handle"] = self.get_twitter_handle()

        # if discord
        return handles

    def pretty_url(self) -> str:
        return self.board.pretty_url(self)

    def report(self) -> bool:
        # Check for public report
        if self.score.rank <= options["public_report_rank_diff"]:
            return True

        if (
            "discord_id" in self.linked_accounts
            or "twitter_handle" in self.linked_accounts
        ):
            # TODO: bother checking options?
            return True

        return False
