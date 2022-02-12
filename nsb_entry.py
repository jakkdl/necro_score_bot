from typing import Optional
import codecs
import json

import nsb_steam
from nsb_config import options


class Entry:
    def __init__(self, data):
        print(data)
        self.steam_id : int = data['steam_id']

        if options['steam_key']:
            self.name = nsb_steam.fetch_steamname(self.steam_id)

        self.discord_id : Optional[int] = None
        self.twitter_id : Optional[int] = None

        self.steam_name : str = ''
        self.twitter_handle = None

        self.score = {'points': data['points'],
                'rank': data['rank'],
                'details': data['details']}
        self.prevScore = None
        self.board = None

    def __str__(self):
        return self.steam_name

    def fetch_necrolab(self):
        if not options['necrolab']:
            return

        base = 'https://api.necrolab.com/players/player?'
        url = f"{base}steamid={self.steam_id}"
        obj = nsb_steam.fetchJson(url)

        #TODO: more
        self.steam_name = obj['data']['linked']['steam_name']

    def fetch_twitter_handle(self):
        pass

    def fetch_linked_handles(self):
        self.fetch_necrolab()
        self.fetch_steamname()
