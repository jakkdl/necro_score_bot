import urllib
import urllib.request
import os
import codecs
import json
import re
import time

from nsb_config import options
from nsb_twitter import twitter


def fetchUrl(url, path=None):
    tries = 3
    while True:
        try:
            if path:
                urllib.request.urlretrieve(url, path)
            else:
                return urllib.request.urlopen(url)
            break
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            tries -= 1
            print(
                f'Catched "{e}" fetching {url} trying {tries} more times in 5 seconds',
            )
            if tries == 0:
                raise e
            time.sleep(5)


def boardUrl(lbid, start, end):
    return (
        f'http://steamcommunity.com/stats/247080/leaderboards/'
        f'{lbid}/?xml=1&start={start}&end={end}'
    )


def leaderboardUrl():
    return 'http://steamcommunity.com/stats/247080/leaderboards/?xml=1'


def decodeResponse(response, re_codec='utf-8'):
    data = response.read()
    text = data.decode(re_codec)
    return text


def fetchJson(url):
    response = fetchUrl(url)
    reader = codecs.getreader('utf-8')
    return json.load(reader(response))


def downloadIndex(path):
    boardFile = path + 'leaderboards.xml'
    # fetchUrl(leaderboardsurl, boardFile)
    fetchUrl(leaderboardUrl(), boardFile)


def fetch_steamname(steam_id):
    url = (
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={options['steam_key']}&steamids={steam_id}"
    )
    obj = fetchJson(url)
    return obj['response']['players'][0]['personaname']


def getTwitterHandle(steam_id):
    url = f'http://steamcommunity.com/profiles/{steam_id}'
    text = decodeResponse(fetchUrl(url), 'latin-1')

    match = re.search(r"twitter\.com\\/(?P<handle>\w+)\\\"", text)
    if match is None:
        return match

    handle = match.group('handle')

    if not twitter:
        print('Warning: unverified handle')
        return handle
    if twitter.checkTwitterHandle(handle):
        return handle

    print(f"{handle} in steam profile but not valid")
    return None


def known_cheater(steam_id):
    file = 'known_cheaters.txt'
    if not os.path.isfile(file):
        file = os.path.dirname(os.path.realpath(__file__)) + '/' + file

    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if int(line) == steam_id:
                return True
    return False
