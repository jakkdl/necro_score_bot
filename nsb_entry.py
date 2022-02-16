import urllib
import json
from typing import Optional

import nsb_leaderboard
import nsb_steam
from nsb_config import options


class Entry:
    def __init__(
        self,
        data: nsb_leaderboard.BoardEntry,
        board: nsb_leaderboard.Leaderboard,
        template: str,
        hist_data: Optional[nsb_leaderboard.BoardEntry] = None,
    ):
        self.steam_id: str = data.steam_id

        self.linked_accounts: dict[str, str] = self._fetch_linked_handles()

        self.score = data
        self.prev_score = hist_data

        self.board: nsb_leaderboard.Leaderboard = board
        self.template: str = template

    def __str__(self) -> str:
        if "steam_name" in self.linked_accounts:
            return self.linked_accounts["steam_name"]
        return str(self.steam_id)

    def necrolab_player(self) -> dict[str, dict[str, str]]:
        url = f"https://api.necrolab.com/players/player?steamid={self.steam_id}"
        obj = nsb_steam.fetch_json(url)

        return obj["data"]["linked"]  # type: ignore

    def _fetch_linked_handles(self) -> dict[str, str]:
        handles = {}
        if options["necrolab"]:
            try:
                data = self.necrolab_player()
                handles["steam_name"] = data["steam"]["personaname"]
                handles["discord_id"] = data["discord"]["id"]
                handles["twitter_handle"] = data["twitter"]["name"]
            except (
                urllib.error.URLError,
                json.decoder.JSONDecodeError,
            ):
                pass

        if "steam_name" not in handles and options["steam_key"]:
            handles["steam_name"] = nsb_steam.fetch_steamname(self.steam_id)

        if "twitter_handle" not in handles and options["steam_key"]:
            twitter_handle = nsb_steam.get_twitter_handle(self.steam_id)
            if twitter_handle:
                handles["twitter_handle"] = twitter_handle

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
