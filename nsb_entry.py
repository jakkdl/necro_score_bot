import urllib
import json
from typing import Optional

import nsb_leaderboard
import nsb_steam
from nsb_config import options


class Entry:
    def __init__(self, data, board, template, hist_data=None):
        self.steam_id: int = data["steam_id"]

        self.linked_accounts: dict = self._fetch_linked_handles()

        self.score: dict = {
            "points": data["points"],
            "rank": data["rank"],
            "details": data["details"],
        }
        self.prev_score: Optional[dict] = None
        if hist_data is not None:
            self.prev_score: dict = {
                "points": hist_data["points"],
                "rank": hist_data["rank"],
                "details": hist_data["details"],
            }

        self.board: nsb_leaderboard.Leaderboard = board
        self.template: str = template

    def __str__(self):
        if "steam_name" in self.linked_accounts:
            return self.linked_accounts["steam_name"]
        return self.steam_id

    def necrolab_player(self):
        url = f"https://api.necrolab.com/players/player?steamid={self.steam_id}"
        obj = nsb_steam.fetch_json(url)

        return obj["data"]["linked"]

    def _fetch_linked_handles(self) -> dict:
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

        # if discord
        return handles

    def report(self):
        # Check for public report
        if self.score["rank"] <= options["public_report_rank_diff"]:
            return True

        if (
            "discord_id" in self.linked_accounts
            or "twitter_handle" in self.linked_accounts
        ):
            # TODO: bother checking options?
            return True

        return False
