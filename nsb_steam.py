import urllib
import urllib.request
import os
import codecs
import json
import re
import time
import sys

baseUrl = 'http://steamcommunity.com/stats/247080/leaderboards/'
leaderboardsurl = baseUrl + '?xml=1'

debugPath = False
overWriteOld = False
tweet = False

if not debugPath:
    basePath = '/home/hatten/Var/cotn/'
else:
    basePath = '/home/hatten/Var/cotn_debug/'

boardFile = basePath + 'leaderboards.xml'
lastPath = basePath + 'last/'
currPath = basePath + 'tmp/'
configPath = '~/.config/cotn/'

def readConfig(file):
    f = open(os.path.expanduser(configPath + file))
    result = f.read()
    f.close()
    return result.rstrip()


STEAMKEY = readConfig('steamkey')


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
            print('Catched "' + str(e) + '" fetching', url, 'trying', tries, 'more times in 5 seconds')
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch', url)
        except:
            tries -= 1
            print('Catched unexpected error: "' + str(sys.exc_info()[0]) + '" fetching', url, 'trying', tries, 'more times in 5 seconds')
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch leaderboard at ' + url)


def boardUrl(lbid, start, end):
    return baseUrl + str(lbid) + '/?xml=1&start=%d&end=%d'%(start, end)

def decodeResponse(response):
    data = response.read()
    text = data.decode('utf-8')
    return text

def downloadIndex():
    fetchUrl(leaderboardsurl, boardFile)

def getTwitterHandle(id, twitit):
    url = 'http://steamcommunity.com/profiles/' + str(id)
    text = decodeResponse(fetchUrl(url))

    match = re.search(r"twitter\.com\\/(?P<handle>\w+)\\\"", text)
    if match is None:
        return match
    else:
        handle = match.group('handle')

    if twitit.checkTwitterHandle(handle):
        return handle
    else:
        print(handle, 'in steam profile but not valid')
        return None

def steamname(steam_id):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=%s&steamids=%d'%(STEAMKEY, steam_id)
    response = fetchUrl(url)
    reader = codecs.getreader('utf-8')
    obj = json.load(reader(response))
    return obj['response']['players'][0]['personaname']

