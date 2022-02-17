# import urllib
# import urllib.request
# import os

# import codecs
# import json
# import re

# import time
# from typing import Optional

# import requests

# from nsb_config import options
# from nsb_twitter import twitter


# def fetch_url(url: str, path: Optional[str] = None) -> requests.Response:
#    tries = 3
#    while True:
#        try:
#            if path:
#                urllib.request.urlretrieve(url, path)
#            else:
#                return requests.get(url)
#                #return urllib.request.urlopen(url)
#            break
#        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
#            tries -= 1
#            print(
#                f'Catched "{exc}" fetching {url} trying {tries} more times in 5 seconds',
#            )
#            if tries == 0:
#                raise exc
#            time.sleep(5)


# def board_url(lbid: int, start: int, end: int) -> str:
#    return (
#        f"http://steamcommunity.com/stats/247080/leaderboards/"
#        f"{lbid}/?xml=1&start={start}&end={end}"
#    )


# def decode_response(response: requests.Response, re_codec: str = "utf-8") -> Any:
#    data = response.read()
#    text = data.decode(re_codec)
#    return text


# def fetch_json(url: str) -> Any:
#    return requests.get(url).json()
# response = fetch_url(url)
# reader = codecs.getreader("utf-8")
# return json.load(reader(response))


# def download_index(path: str) -> None:
#    board_file = path + "leaderboards.xml"
#    # fetch_url(leaderboardsurl, board_file)
#    fetch_url(leaderboard_url(), board_file)
