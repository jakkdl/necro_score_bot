import urllib
import urllib.request
import os
import codecs
import json
import time
import sys


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
            print('Catched "' + str(e) + '" fetching',
                  url, 'trying', tries, 'more times in 5 seconds')
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch', url)
        except Exception as e:
            tries -= 1
            print('Catched unexpected error: "' + str(sys.exc_info()[0]) +
                  '" fetching', url, 'trying', tries, 'more times in 5 seconds')
            print(sys.exc_info())
            print(e)
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch leaderboard at ' + url)


def boardUrl(lbid, start, end):
    baseUrl = 'http://steamcommunity.com/stats/247080/leaderboards/'
    return baseUrl + str(lbid) + '/?xml=1&start=%d&end=%d'%(start, end)

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

def get_linked_handles(steam_id):
    if not isinstance(steam_id, str):
        steam_id = str(steam_id)
        base = 'https://api.necrolab.com/players/player?'
        url = base + 'steamid={}'.format(steam_id)
        obj = fetchJson(url)
        return obj['data']['linked']


def known_cheater(steam_id):
    file = 'known_cheaters.txt'
    if not os.path.isfile(file):
        file = os.path.dirname(os.path.realpath(__file__)) + '/' + file


    with open(file, 'r') as f:
        for line in f:
            if int(line) == steam_id:
                return True
    return False
