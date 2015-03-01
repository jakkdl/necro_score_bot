import urllib
import urllib.request
import xml.etree.ElementTree as ET
import json
import codecs
import twitter
import os
import time



basePath = '/home/hatten/Var/cotn/'
boardfile = basePath + 'leaderboards.xml'
lastPath = basePath + 'last/'
currPath = basePath + 'tmp/'
configPath = '/home/hatten/.config/cotn/'

baseUrl = 'http://steamcommunity.com/stats/247080/leaderboards/'
leaderboardsurl = baseUrl + '?xml=1'


def readConfig(file):
    f = open(configPath + file)
    result = f.read()
    f.close()
    return result.rstrip()


steamkey = readConfig('steamkey')
consumer_key = readConfig('consumer_key')
consumer_secret = readConfig('consumer_secret')


print('start at: ', time.strftime('%c'))






def includeBoard(name):
    characters = ['Cadence', 'Melody', 'Aria', 'Dorian', 'Eli', 'Monk', 'Dove', 'Bolt', 'Bard', 'All Chars'] #'Coda'
    exclude = ['CO-OP', 'CUSTOM', 'SEEDED', '/']
    for j in exclude:
        if j.lower() in name.lower():
            return False
    if 'speedrun' in name.lower() and 'deathless' in name.lower():
        return False
    for j in characters:
        if j.lower() in name.lower():
            return True
    return False

def update():
    tree = ET.parse(boardfile)
    root = tree.getroot()

    for i in range(3, len(root)):
        name = root[i][2].text
        lbid = root[i][1].text
        if includeBoard(name):
            downloadBoard(lbid, currPath)
            ids = diffingIds(lbid)
            for id in ids:
                composeMessage(id, name)
            if ids:
                move(lbid)


def move(lbid, path1=currPath, path2=lastPath):
    os.rename(path1 + lbid + '.xml', path2 + lbid + '.xml')


def postTweet(text):
    MY_TWITTER_CREDS = os.path.expanduser(configPath + 'twitter_credentials')
    oauth_token, oauth_secret = twitter.read_token_file(MY_TWITTER_CREDS)
    t = twitter.Twitter(auth=twitter.OAuth(
        oauth_token, oauth_secret, consumer_key, consumer_secret))
    t.statuses.update(status=text)


def diffingIds(lbid, path1=currPath, path2=lastPath):
    tree1 = ET.parse(path1 + lbid + '.xml')
    root1 = tree1.getroot()
    tree2 = ET.parse(path2 + lbid + '.xml')
    root2 = tree2.getroot()

    ids = []

    #assume entries is at the same index in both files
    index = -1
    for i in range(len(root1)):
        if root1[i].tag == 'entries':
            index = i
    for i in range(len(root1[index])):
        steamid, score, rank = extractEntry(root1[index][i])
        found = False
        for entry in root2[index]:
            steamid2, score2, rank2 = extractEntry(entry)
            if steamid == steamid2:
                found = True
                if score != score2:
                    ids.append([steamid, score, rank, rank2])
        if found == False:
            ids.append([steamid, score, rank, -1])


    return ids


def composeMessage(person, board):
    name = steamname(person[0])
    if person[2] != person[3]:
        tmp = ' rose to rank ' + person[2]
    else:
        tmp = ' still on rank ' + person[2] + ' but now'
    if 'SPEEDRUN' in board:
        score = ' with time ' + scoreToTime(person[1])
    elif 'DEATHLESS' in board:
        score = ' with score ' + scoreToProgress(person[1])
    else:
        score = ' with score ' + person[1]

    postTweet(name + tmp + score + ' on ' + board + ' #necrodancer')
    print(name + tmp + score + ' on ' + board)


def downloadBoard(lbid, path=basePath, start=1, end=10):
    leaderboardurl=baseUrl + lbid + '/?xml=1&start=' + str(start) + '&end=' + str(end)
    urllib.request.urlretrieve(leaderboardurl, path + lbid + '.xml')

def downloadIndex():
    urllib.request.urlretrieve(leaderboardsurl, boardfile)

def steamname(id):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' + steamkey + '&steamids=' + id
    response = urllib.request.urlopen(url)
    reader = codecs.getreader('utf-8')
    obj = json.load(reader(response))
    return obj['response']['players'][0]['personaname']

def printPlayer(name, rank, score):
    print('rank', rank)
    print('name', name)
    print('score', score)

def getLeaderboard(lbid, start, end):
    downloadBoard(lbid, start, end)
    tree = ET.parse('/home/hatten/Var/cotn/' + lbid + '.xml')
    root = tree.getroot()
    return root

#Extract steamid, score, rank
def extractEntry(entry):
    return entry[0].text, entry[1].text, entry[2].text

def getEntryIndex(root):
    index = -1
    for i in range(len(root)):
        if root[i].tag == 'entries':
            index = i
    return index

def printBoard(lbid, start=1, end=10):
    root = getLeaderboard(lbid, start, end)
    index = getEntryIndex(root)

    for entry in root[index]:
        steamid, score, rank = extractEntry(root1[index][i])
        name = steamname(steamid)
        printPlayer(name, rank, score)

def scoreToProgress(score):
    intscore = int(score)
    wins = intscore // 100
    zone = ( intscore // 10 ) % 10 + 1
    level = intscore % 10 + 1
    return str(wins) + '-' + str(zone) + '-' + str(level)


def scoreToTime(score):
    copy = 100000000 - int(score)
    msec = copy % 1000
    copy //= 1000
    sec = copy % 60
    copy //= 60
    min = copy  % 60
    copy //= 60
    hour = copy
    result = ""

    mfill=1
    sfill=1
    if hour != 0:
        result += str(hour) + ":"
        mfill=2
    if min != 0 or mfill == 2:
        result += str(min).zfill(mfill) + ":"
        sfill=2
    result += str(sec).zfill(sfill) + "." + str(msec).zfill(3)
    return result

#leaderboardurl='http://steamcommunity.com/stats/247080/leaderboards/?xml=1'


#printTop10('695404')



#postTweet("Hello again")
update()
#print(diff('695473'))
