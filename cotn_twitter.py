import xml.etree.ElementTree as ET
import os
import os.path
import time
import nsb_twitter
import nsb_leaderboard
import nsb_steam
import datetime

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


twitit = nsb_twitter.twitter(os.path.expanduser(configPath + 'twitter/'))


print('start at: ', time.strftime('%c'))


def update():
    nsb_steam.downloadIndex()
    root = getRoot(boardFile)

    for i in range(3, len(root)):
        board = nsb_leaderboard.leaderboard(root[i], currPath, lastPath)
        if board.include():
            board.download()
            board.read()
            board.read_hist()
            for entry in board.diffingEntries():
                message = composeMessage(entry, board)
                if tweet:
                    twitit.postTweet(message)
                if True:
                    print(message.encode('ascii', 'replace'))
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



def nth(i):
    if i == 1:
        return 'st'
    elif i == 2:
        return 'nd'
    elif i == 3:
        return 'rd'
    else:
        return 'th'

def composeMessage(person, board):
    name = nsb_steam.steamname(person.steamid)
    if board.toofzSupport():
        url = board.toofzUrl() + ' '
    else:
        url = ''

    if board.mode() == 'speed':
        time = scoreAsMilliseconds(person.score)
        prevTime = scoreAsMilliseconds(person.prevScore) if person.hasHist else -1

        relTime = relativeTime(time, prevTime)
        strScore = formatTime(time) + relTime
    elif board.mode() == 'deathless':
        strScore = formatProgress(person.score)
        if person.hasHist:
            strScore += relativeProgress(person.score, person.prevScore)
    else:
        strScore = str(person.score)
        if person.hasHist:
            strScore += relativeScore(person.score, person.prevScore)
        strScore += ' gold'


    if person.rank != person.prevRank:
        inter1 = ' claims rank '
        if person.hasHist:
            inter2 = relativeRank(person.rank, person.prevRank) + ' in '
        else:
            inter2 = ' in '
        inter3 = ' with '
    else:
        inter1 = ', '
        inter2 = nth(person.rank) + ' in '
        inter3 = ', improves '
        relRank = ''
        if board.mode == 'score':
            inter3 += 'to '
        elif board.mode == 'speed':
            inter3 += 'time to '
        elif board.mode == 'deathless':
            inter3 += 'streak to '




    tag = '#necrodancer'
    twitterHandle = nsb_steam.getTwitterHandle(person.steamid, twitit)
    if twitterHandle:
        name = '.@' + twitterHandle
    
    return name + inter1 + str(person.rank) + inter2 + str(board) + inter3 + strScore + ' ' + url + tag


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


def postYesterday():
    postDaily(datetime.date.today() - datetime.timedelta(days=1))


def postDaily(date, path=currPath):
    nsb_steam.downloadIndex()
    root = getRoot(boardFile)

    for i in range(3, len(root)):
        board = nsb_leaderboard.leaderboard(root[i])
        if not board.daily():
            continue
        if board.date() == date:
            board.fetch()

            for entry in board.topEntries(3):
                message = composeMessage(entry, board)
                if tweet:
                    twitit.postTweet(message)
                if True:
                    print(message)
            break



#TODO: broken
def printBoard(lbid, path=currPath, start=1, end=10):
    nsb_steam.downloadBoard(lbid, currPath, start, end)
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

def delete20():
    a = TWITTER_AGENT.statuses.user_timeline(screen_name='necro_score_bot')
    for i in range(1, 20):
        print(i)
        TWITTER_AGENT.statuses.destroy(id=int(a[i]['id_str']))
#print(TWITTER_AGENT.users.show(screen_name='necro_score_bot'))
#postTweet('Hello again')
if __name__=="__main__":
    update()
#print(getTwitterHandle('76561198074553183'))
#print(getTwitterHandle('76561197975956199'))
#rat
#print(getTwitterHandle(76561198089674311))
#print(getTwitterHandle(76561197998362244))
#printBoard('470749', currPath)
#printBoard('386753', currPath)
#prit(diff('695473'))
