import urllib
import urllib.request
import os
import codecs
import json
import re
import time
from typing import Any, Optional

from nsb_config import options
from nsb_twitter import twitter


def fetch_url(url: str, path: Optional[str] = None) -> Any:
    tries = 3
    while True:
        try:
            if path:
                urllib.request.urlretrieve(url, path)
            else:
                return urllib.request.urlopen(url)
            break
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            tries -= 1
            print(
                f'Catched "{exc}" fetching {url} trying {tries} more times in 5 seconds',
            )
            if tries == 0:
                raise exc
            time.sleep(5)


# def board_url(lbid: int, start: int, end: int) -> str:
#    return (
#        f"http://steamcommunity.com/stats/247080/leaderboards/"
#        f"{lbid}/?xml=1&start={start}&end={end}"
#    )


def leaderboard_url() -> str:
    return "http://steamcommunity.com/stats/247080/leaderboards/?xml=1"


def decode_response(response: Any, re_codec: str = "utf-8") -> Any:
    data = response.read()
    text = data.decode(re_codec)
    return text


def fetch_json(url: str) -> Any:
    response = fetch_url(url)
    reader = codecs.getreader("utf-8")
    return json.load(reader(response))


# def download_index(path: str) -> None:
#    board_file = path + "leaderboards.xml"
#    # fetch_url(leaderboardsurl, board_file)
#    fetch_url(leaderboard_url(), board_file)


def fetch_steamname(steam_id: str) -> str:
    url = (
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={options['steam_key']}&steamids={steam_id}"
    )
    obj = fetch_json(url)
    name = obj["response"]["players"][0]["personaname"]
    assert isinstance(name, str)
    return name


def get_twitter_handle(steam_id: str) -> Optional[str]:
    url = f"http://steamcommunity.com/profiles/{steam_id}"
    text = decode_response(fetch_url(url), "latin-1")

    match: Optional[re.Match[str]] = re.search(
        r"twitter\.com\\/(?P<handle>\w+)\\\"", text
    )
    if match is None:
        return match

    handle = match.group("handle")

    if not twitter:
        print("Warning: unverified handle")
        return handle
    if twitter.check_twitter_handle(handle):
        return handle

    print(f"{handle} in steam profile but not valid")
    return None


def known_cheater(steam_id: str) -> bool:
    filename = "known_cheaters.txt"
    if not os.path.isfile(filename):
        filename = os.path.dirname(os.path.realpath(__file__)) + "/" + filename

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if int(line) == int(steam_id):
                return True
    return False
