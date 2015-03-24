import urllib
import urllib.request
import xml.etree.ElementTree as ET
import json
import codecs
import re
import os
import os.path
import time
import sys
from nsb_twitter import *
import nsb_leaderboard

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

baseUrl = 'http://steamcommunity.com/stats/247080/leaderboards/'
leaderboardsurl = baseUrl + '?xml=1'


twitit = twit(os.path.expanduser(configPath + 'twitter/'))

def readConfig(file):
    f = open(os.path.expanduser(configPath + file))
    result = f.read()
    f.close()
    return result.rstrip()


STEAMKEY = readConfig('steamkey')



print('start at: ', time.strftime('%c'))


def update():
    #downloadIndex()
    root = getRoot(boardFile)

    for i in range(3, len(root)):
        name = root[i][2].text
        lbid = root[i][1].text
        board = nsb_leaderboard.leaderboard(name)
        if board.include():
            #downloadBoard(lbid, currPath, 1, 100)
            ids = diffingIds(lbid, board.max())
            for id in ids:
                composeMessage(id, name, tweet, True)
            if overWriteOld:
                move(lbid)
            #break


def getRoot(xmlFile):
    tree = ET.parse(xmlFile)
    return tree.getroot()

def move(lbid, path1=currPath, path2=lastPath):
    if not os.path.isdir(path2):
        print('creating ', path2)
        os.mkdir(path2)
    if not os.path.isdir(path1):
        print('source missing: ', path1)
    os.rename(path1 + lbid + '.xml', path2 + lbid + '.xml')

def getTwitterHandle(id):
    url = 'http://steamcommunity.com/profiles/' + str(id)
    response =fetchUrl(url)
    data = response.read()
    text = data.decode('utf-8')

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
            print('Catched', e, 'fetching', url, 'trying', tries, 'more times in 5 seconds')
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch', url)
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise LookupError('Failed to fetch leaderboard')


def diffingIds(lbid, maxIndex, path1=currPath, path2=lastPath):
    if not os.path.isfile(path1 + lbid + '.xml'):
        print(lbid, 'not existing in tmp')
        return []

    root1 = getRoot(path1 + lbid + '.xml')

    if not os.path.isfile(path2 + lbid + '.xml'):
        print(lbid, 'not existing in last')
        return []
    root2 = getRoot(path2 + lbid + '.xml')

    ids = []

    #assume entries is at the same index in both files
    #incorrent assumption, the field 'resultCount'
    #is removed when a leaderboard gets more than 100 entries
    index = getEntryIndex(root1)
    index2 = getEntryIndex(root2)
    for i in range(0, min(maxIndex, len(root1[index]))):
        entry = root1[index][i]
    #for entry in root1[index]:
        steamid, score, rank = extractEntry(entry)
        found = False
        for entry in root2[index2]:
            steamid2, score2, rank2 = extractEntry(entry)
            if steamid == steamid2:
                found = True
                if score != score2:
                    ids.append([steamid, score, score2, rank, rank2])
                break
        if found == False:
            ids.append([steamid, score, -1, rank, -1])


    return ids

def nth(i):
    if i == 1:
        return 'st'
    elif i == 2:
        return 'nd'
    elif i == 3:
        return 'rd'
    else:
        return 'th'

def composeMessage(person, board, tweet=False, debug=True):
    steamid = person[0]
    score = person[1]
    prevScore = person[2]
    rank = person[3]
    prevRank = person[4]
    name = steamname(steamid)
    if board.toofzSupport:
        url = board.toofzUrl
    else:
        url = ''

    if board.mode == 'speed':
        time = scoreAsMilliseconds(score)
        prevTime = scoreAsMilliseconds(prevScore) if prevScore != -1 else -1

        relTime = relativeTime(time, prevTime)
        strScore = formatTime(time) + relTime
    elif board.mode == 'deathless':
        relScore = relativeProgress(score, prevScore)
        strScore = formatProgress(score) + relScore
    else:
        relScore = relativeScore(score, prevScore)
        strScore = str(score) + relScore + ' gold'


    if rank != prevRank:
        inter1 = ' claims rank '
        inter2 = relativeRank(rank, prevRank) + ' in '
        inter3 = ' with '
    else:
        inter1 = ', '
        inter2 = nth(rank) + ' in '
        inter3 = ', improves '
        relRank = ''
        if board.mode == 'score':
            inter3 += 'to '
        elif board.mode == 'speed':
            inter3 += 'time to '
        elif board.mode == 'deathless':
            inter3 += 'streak to '




    tag = ' #necrodancer'
    twitterHandle = getTwitterHandle(steamid)
    if twitterHandle:
        name = '.@' + twitterHandle

    message = name + inter1 + str(rank) + inter2 + str(board) + inter3 + strScore + ' ' + url + tag
    if tweet:
        twitit.postTweet(message)
    if debug:
        print(message)


def downloadBoard(lbid, path=basePath, start=1, end=10):
    if not os.path.isdir(path):
        print('creating', path)
        os.mkdir(path)
    leaderboardurl=baseUrl + lbid + '/?xml=1&start=%d&end=%d'%(start, end)
    fetchUrl(leaderboardurl, path + lbid + '.xml')


def downloadIndex():
    fetchUrl(leaderboardsurl, boardFile)

def steamname(steam_id):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=%s&steamids=%d'%(STEAMKEY, steam_id)
    response = fetchUrl(url)
    reader = codecs.getreader('utf-8')
    obj = json.load(reader(response))
    return obj['response']['players'][0]['personaname']

def printPlayer(name, rank, score):
    print('rank', rank)
    print('name', name)
    print('score', score)

#Extract steamid, score, rank
def extractEntry(entry):
    return int(entry[0].text), int(entry[1].text), int(entry[2].text)

def getEntryIndex(root):
    for index, value in enumerate(root):
        if value.tag == 'entries':
            return index
    return -1

def printBoard(lbid, path=currPath, start=1, end=10):
    downloadBoard(lbid, currPath, start, end)
    root = getRoot(path + lbid + '.xml')
    index = getEntryIndex(root)
    for entry in root[index]:
        steamid, score, rank = extractEntry(entry)
        name = steamname(steamid)
        printPlayer(name, rank, score)

def scoreToProgress(score):
    wins = score // 100
    zone = ( score // 10 ) % 10 + 1
    level = score % 10 + 1
    return wins, zone, level

def formatProgress(score):
    wins, zone, level = scoreToProgress(score)
    return '%d wins, dying on %d-%d'%(wins, zone, level)

def relativeProgress(newScore, prevScore):
    if prevScore == -1 or newScore == prevScore:
        return ''
    else:
        wins, zone, level = scoreToProgress(prevScore)
        return ' (up from %d-%d-%d)'%(wins, zone, level)

def scoreAsMilliseconds(score):
    return 100000000 - score

def formatTime(milliseconds):
    """ Takes in a time (in milliseconds) and returns a formatted string.
        examples:
            1000    -> '01.00'
            100293  -> '01:40.29'
            100298  -> '01:40.30'
            4100298 -> '1:08:20.30'
    """
    hours, milliseconds = divmod(milliseconds, 60*60*1000)
    minutes, milliseconds = divmod(milliseconds, 60*1000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    milliseconds = round(milliseconds / 10.0) # Change precision from 3 to 2

    result = ''

    minutePad='%d:'
    if hours:
        result += '%d:'%(hours)
        minutePad='%02d:'
    if minutes or hours:
        result += minutePad%(minutes)

    result += '%02d.%02d'%(seconds, milliseconds)

    return result

def relativeRank(newRank, prevRank):
    if prevRank == -1 or newRank == prevRank:
        return ''
    else:
        return ' (+%d)'%(prevRank - newRank)

def relativeTime(newTime, prevTime):
    """ newTime and prevTime should be given in milliseconds
    """
    if prevTime == -1 or newTime == prevTime:
        return ''
    else:
        return ' (-%s)'%(formatTime(prevTime - newTime))

def relativeScore(newScore, prevScore):
    if prevScore == -1 or newScore == prevScore:
        return ''
    else:
        return ' (+%d)'%(newScore - prevScore)


#leaderboardurl='http://steamcommunity.com/stats/247080/leaderboards/?xml=1'


#printTop10('695404')

if not os.path.isdir(basePath):
    os.mkdir(basePath)


#postTweet('Hello again')
update()
#print(getTwitterHandle('76561198074553183'))
#print(getTwitterHandle('76561197975956199'))
#rat
#print(getTwitterHandle(76561198089674311))
#print(getTwitterHandle(76561197998362244))
#printBoard('470749', currPath)
#printBoard('386753', currPath)
#prit(diff('695473'))
