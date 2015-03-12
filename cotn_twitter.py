import urllib
import urllib.request
import xml.etree.ElementTree as ET
import json
import codecs
import twitter
import os
import os.path
import time
import sys

debug = False
overWriteOld = True

if not debug:
    basePath = '/home/hatten/Var/cotn/'
else:
    basePath = '/home/hatten/Var/cotn_debug/'

boardFile = basePath + 'leaderboards.xml'
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


def getBoardMax(name):
    if 'deathless' in name.lower():
        return 5
    if 'seeded' in name.lower():
        return 3
    return 10

def formatBoardName(name):
    if 'DEATHLESS' in name:
        #Remove hardcore from the name
        name = name.replace('HARDCORE ','')
    name = name.replace('DOVE', 'Dove')
    name = name.replace('Pacifist', 'Dove')
    name = name.replace('All Char', 'All-Char')
    name = name.replace('DEATHLESS', 'Deathless')
    name = name.replace('SPEEDRUN', 'Speed')
    name = name.replace('HARDCORE', 'Score')
    name = name.split()
    if len(name) == 2 and 'Deathless' not in name:
        name[0], name[1] = name[1], name[0]
    if len(name) == 1:
        name.append(name[0])
        name[0] = 'Cadence'
    return name[0] + ' ' + name[1]


def includeBoard(name):
    modes = ['hardcore', 'speedrun', 'deathless']
    exclude = ['CO-OP', 'CUSTOM', '/', 'Pacifist', 'Thief', 'Ghost', 'Coda', 'seeded']
    for j in exclude:
        if j.lower() in name.lower():
            return False
    
    #Don't want the boards 'speedrun deathless'
    if 'speedrun' in name.lower() and 'deathless' in name.lower():
        return False
    
    for i in modes:
        if i in name.lower():
            return True
    
    return False

def update():
    downloadIndex()
    root = getRoot(boardFile)

    for i in range(3, len(root)):
        name = root[i][2].text
        lbid = root[i][1].text
        if includeBoard(name):
            maxIndex = getBoardMax(name)
            downloadBoard(lbid, currPath, 1, 100)
            ids = diffingIds(lbid, maxIndex)
            for id in ids:
                composeMessage(id, name, not debug, True)
            if overWriteOld:
                move(lbid)


def getRoot(xmlFile):
    tree = ET.parse(xmlFile)
    return tree.getroot()

def move(lbid, path1=currPath, path2=lastPath):
    if not os.path.isdir(path2):
        print("creating ", path2)
        os.mkdir(path2)
    if not os.path.isdir(path1):
        print("source missing: ", path1)
    os.rename(path1 + lbid + '.xml', path2 + lbid + '.xml')


def getTwitterHandle(id):
    url = 'http://steamcommunity.com/profiles/' + str(id)
    time.sleep(1)
    response = urllib.request.urlopen(url) #handle exceptions
    data = response.read()
    text = data.decode('utf-8')
    if 'twitter' not in text:
        return None
    start = text.find('twitter')+13
    end = text.find('\\', start, start+16)
    handle = text[start:end]
    MY_TWITTER_CREDS = os.path.expanduser(configPath + 'twitter_credentials')
    oauth_token, oauth_secret = twitter.read_token_file(MY_TWITTER_CREDS)
    t = twitter.Twitter(auth=twitter.OAuth(
        oauth_token, oauth_secret, consumer_key, consumer_secret))
    try:
        t.users.show(screen_name=handle)
        return handle
    except:
        print(handle, "in steam profile but not valid")
        return None


def postTweet(text):
    MY_TWITTER_CREDS = os.path.expanduser(configPath + 'twitter_credentials')
    oauth_token, oauth_secret = twitter.read_token_file(MY_TWITTER_CREDS)
    t = twitter.Twitter(auth=twitter.OAuth(
        oauth_token, oauth_secret, consumer_key, consumer_secret))
    t.statuses.update(status=text)


def diffingIds(lbid, maxIndex, path1=currPath, path2=lastPath):
    root1 = getRoot(path1 + lbid + '.xml')

    if not os.path.isfile(path2 + lbid + '.xml'):
        print(lbid, "not existing in last")
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
    return 'th'

def composeMessage(person, board, tweet=False, debug=True):
    steamid = person[0]
    score = person[1]
    prevScore = person[2]
    rank = person[3]
    prevRank = person[4]
    name = steamname(steamid)
    board = formatBoardName(board)
    url = boardToUrl(board)

    if 'Speed' in board:
        relScore = relativeTime(score, prevScore)
        strScore = scoreToTime(score) + relScore
    elif 'Deathless' in board:
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
        if 'Score' in board:
            inter3 += 'to '
        elif 'Speed' in board:
            inter3 += 'time to '
        elif 'Deathless' in board:
            inter3 += 'streak to '

    
   

    tag = ' #necrodancer'
    twitterName = getTwitterHandle(steamid)
    if twitterName:
        name = '.@' + twitterName

    message = name + inter1 + str(rank) + inter2 + board + inter3 + strScore + ' ' + url + tag
    if tweet:
        postTweet(message)
    if debug:
        print(message)


def downloadBoard(lbid, path=basePath, start=1, end=10):
    if not os.path.isdir(path):
        print("creating", path)
        os.mkdir(path)
    leaderboardurl=baseUrl + lbid + '/?xml=1&start=' + str(start) + '&end=' + str(end)
    tries = 10
    while True:
        try:
            urllib.request.urlretrieve(leaderboardurl, path + lbid + '.xml')
            break
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            tries = tries-1
            print("Catched", e, "trying", str(tries), "more times in 5 seconds")
            time.sleep(5)
            if tries == 0:
                raise LookupError('Failed to fetch leaderboard')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise LookupError('Failed to fetch leaderboard')

def downloadIndex():
    urllib.request.urlretrieve(leaderboardsurl, boardFile)

def steamname(id):
    id = str(id)
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' + steamkey + '&steamids=' + id
    response = urllib.request.urlopen(url)
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
    return str(wins) + ' wins, dying on ' + str(zone) + '-' + str(level)

def relativeProgress(score, prevScore):
    #print(score, prevScore)
    if prevScore == -1 or score - prevScore == 0:
        return ''
    wins, zone, level = scoreToProgress(prevScore)
    return ' (up from ' + str(wins) + '-' + str(zone-1) + '-' + str(level-1) + ')'

def invertTime(time):
    return 100000000 - time

def scoreToTime(score):
    copy = invertTime(score)
    msec = (copy % 1000) // 10 #only want precision of 2
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
    result += str(sec).zfill(sfill) + "." + str(msec).zfill(2)
    return result

def boardToUrl(board):
    board = board.replace('All-Chars', 'All')
    board = board.split()
    return 'http://crypt.toofz.com/Leaderboards/' + board[0] + '/' + board[1]


def relativeRank(rank, prevRank):
    if prevRank == -1 or rank == prevRank:
        return ''
    return ' (+' + str(prevRank - rank) + ')'

def relativeTime(time, prevTime):
    if prevTime == -1 or time == prevTime:
        return ''
    realTime = invertTime(time)
    realPrev = invertTime(prevTime)
    relTime = realPrev - realTime
    invertRelTime = invertTime(relTime)
    return ' (-' + scoreToTime(invertRelTime) + ')'

def relativeScore(score, prevScore):
    sum = score - prevScore
    if sum == 0 or prevScore == -1:
        return ''
    return ' (+' + str(sum) + ')'


#leaderboardurl='http://steamcommunity.com/stats/247080/leaderboards/?xml=1'


#printTop10('695404')

if not os.path.isdir(basePath):
    os.mkdir(basePath)

#postTweet("Hello again")
update()
#print(getTwitterHandle('76561198074553183'))
#print(getTwitterHandle('76561197975956199'))
#rat
#print(getTwitterHandle(76561198089674311))
#print(getTwitterHandle(76561197998362244))
#printBoard('470749', currPath)
#printBoard('386753', currPath)
#print(diff('695473'))
