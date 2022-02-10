import urllib
import urllib.request
import os
import codecs
import json
import re
import time
import sys

# from nsb_config import options


def fetchUrl(url, path=None):
    tries = 10
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
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch', url)
        except:
            tries -= 1
            print(
                f'Catched unexpected error: "{sys.exc_info()[0]}" fetching {url} '
                f'trying {tries} more times in 5 seconds'
            )
            print(sys.exc_info())
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch leaderboard at ' + url)


def boardUrl(lbid, start, end):
    return (f'http://steamcommunity.com/stats/247080/leaderboards/'
            f'{lbid}/?xml=1&start={start}&end={end}')


def leaderboardUrl():
    return 'http://steamcommunity.com/stats/247080/leaderboards/?xml=1'


def decodeResponse(response, re_codec='utf-8'):
    data = response.read()
    text = data.decode(re_codec)
    return text


def downloadIndex(path):
    boardFile = path + 'leaderboards.xml'
    #fetchUrl(leaderboardsurl, boardFile)
    fetchUrl(leaderboardUrl(), boardFile)


def getTwitterHandle(steam_id, twitit):
    url = f'http://steamcommunity.com/profiles/{steam_id}'
    text = decodeResponse(fetchUrl(url), 'latin-1')

    match = re.search(r"twitter\.com\\/(?P<handle>\w+)\\\"", text)
    if match is None:
        return match

    handle = match.group('handle')

    if not twitit:
        print('Warning: unverified handle')
        return handle
    if twitit.checkTwitterHandle(handle) or not twitit:
        return handle

    print(handle, 'in steam profile but not valid')
    return None


def steamname(steam_id, key):
    url = (
        f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
        f'?key={key}&steamids={steam_id}'
    )
    response = fetchUrl(url)
    reader = codecs.getreader('utf-8')
    obj = json.load(reader(response))
    return obj['response']['players'][0]['personaname']


def known_cheater(steam_id):
    file = 'known_cheaters.txt'
    if not os.path.isfile(file):
        file = os.path.dirname(os.path.realpath(__file__)) + '/' + file

    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if int(line) == steam_id:
                return True
    return False
