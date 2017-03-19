import xml.etree.ElementTree as ET
import os
import os.path
import time
import datetime

import nsb_leaderboard
import nsb_necrolab_board
import nsb_steam_board
import nsb_srl_board
import nsb_steam
import nsb_index
import nsb_database
import nsb_format_points

from nsb_config import options


baseUrl = 'http://steamcommunity.com/stats/247080/leaderboards/'
leaderboardsurl = baseUrl + '?xml=1'





def update(twitter):
    print('start at: ', time.strftime('%c'))

    debug = options['debug']

    index = nsb_index.index()
    #index.read_xml()
    index.fetch()


    for entry in index.entries():
        steam_board = nsb_steam_board.steam_board(entry)
        board = nsb_leaderboard.leaderboard(steam_board)
        #print(board)
        if steam_board.include():
            #print("hi")
            if debug:
                #print(repr(board))
                print("including: ", str(board))
            if not board.hasFile() and not options['handle-new']:
                print('New leaderboard', str(board), 'use --handle-new to use')
                continue

            board.fetch()


            if board.hasFile():
                board.read()
                try:
                    deletedEntries = board.checkForDeleted(90)
                except:
                    #we probably have an older leaderboard
                    continue
                if deletedEntries > 0:
                    print("Found", deletedEntries, "deleted entries in", str(board))
                if deletedEntries > len(board.history):
                    raise Exception('ERROR: ' + str( deletedEntries) + ' ' + str(board)+ ' all entries deleted')
                if deletedEntries > 60:
                    raise Exception('ERROR:', deletedEntries, 'too many deleted entries')
                entries = board.diffingEntries(twitter=twitter)
            else:
                entries = board.topEntries(5)


            for entry in entries:
                #print(nsb_steam.steamname(int(entry['steam_id']), options['steam_key']))
                message = composeMessage(entry, board, twitter)
                if options['tweet']:
                    twitter.postTweet(message)
                print(message.encode('ascii', 'replace'))

            if options['backup']:
                board.write()

def updateJson(twitter):
    boards = {}
    for name in options['json_urls']:
        if options['debug']:
            print(name)

        necrolab_board = nsb_necrolab_board.leaderboard(name, boards)
        board = nsb_leaderboard.leaderboard(necrolab_board)
        board.fetch()
        boards[name] = board

        if board.hasFile():
            board.read()
            entries = board.diffingEntries(twitter=twitter, num=500)
        else:
            entries = board.topEntries(5)


        for entry in entries:
            message = composeMessage(entry, board, twitter)
            if options['tweet']:
                twitter.postTweet(message)
            print(message.encode('ascii', 'replace'))
            #message = composeMessage(entry, board, twitter)
            #print(message)
    if options['backup']:
        for board in boards:
            board.write()

def updateSRL(twitter):
    srl_board = nsb_srl_board.leaderboard()
    board = nsb_leaderboard.leaderboard(srl_board)
    board.fetch()

    if board.hasFile():
        board.read()
        entries = board.diffingEntries()
    else:
        entries = board.topEntries(board.board.entriesToReportOnRankDiff())


    for entry in entries:
        message = composeMessage(entry, board, twitter)
        if options['tweet']:
            twitter.postTweet(message)
        print(message.encode('ascii', 'replace'))
        #message = composeMessage(entry, board, twitter)
        #print(message)
    if options['backup']:
        board.write()

def postYesterday(twitter):
    postDaily(datetime.date.today() - datetime.timedelta(days=1), twitter)


def postDaily(date, twitter):
    index = nsb_index.index()
    index.fetch()

    for entry in index.entries():
        steam_board = nsb_steam_board.steam_board(entry)
        board = nsb_leaderboard.leaderboard(steam_board)
        if not board.board._availability == 'prod':
            continue
        if board.board._coop:
            continue
        if not board.board.daily():
            continue
        if board.board._date != date:
            continue
        print(str(board))

        board.fetch()
        message = composeDailyMessage(board.topEntries(3), board, twitter)
        if options['tweet']:
            twitter.postTweet(message)
        if True:
            #print(repr(board))
            print(message)
        #break

def createDir(path):
    if not os.path.isdir(path):
        print(path, "doesn't exist, creating")
        if not options['dry-run']:
            os.mkdir(path)


def getRoot(xmlFile):
    tree = ET.parse(xmlFile)
    return tree.getroot()


def nth(i):
    if i % 10 == 1 and i % 100 != 11:
        return 'st'
    elif i % 10 == 2 and i % 100 != 12:
        return 'nd'
    elif i % 10 == 3 and i % 100 != 13:
        return 'rd'
    else:
        return 'th'

def composeMessage(person, board, twitter, nodot=False):
    #if 'steam_id' in person:
        #person['steamid'] = person['steam_id']
        #person['score'] = float(person['points'])



    score = person['points']
    rank = int(person['rank'])

    if 'histPoints' in person:
        hasHist = True
        histPoints = person['histPoints']
        histRank = int(person['histRank'])
    else:
        hasHist = False
        histPoints = -1
        histRank = -1

    url = board.getUrl(person)

    strPoints = board.formatPoints(person)


    if rank < histRank or histRank == -1:
        inter1 = ' claims rank '
        if hasHist:
            inter2 = nsb_format_points.relativeRank(rank, histRank) + ' in '
        else:
            inter2 = ' in '
        inter3 = ' with '
    else:
        inter1 = ', '
        inter2 = nth(rank) + ' in '
        inter3 = ', improves'
        relRank = ''
        if board.board.pre_unit():
            inter3 += ' ' + board.board.pre_unit()
        inter3 += ' to '




    tag = ' #necrodancer'


    #TODO: yo this shit is unreadable
    if 'twitter_username' in person:
        twitterHandle = person['twitter_username']
    else:
        twitterHandle = board.getTwitterHandle(person, twitter)

    if twitterHandle:
        name = '@' + twitterHandle
        if board.includePublic(person):
            name = '.' + name
    elif 'name' in person:
        name = person['name']
    else:
        name = nsb_steam.steamname(int(person['steam_id']), options['steam_key'])
    if 'steam_id' in person:
        if nsb_steam.known_cheater(person['steam_id']):
            name = '@Arachness_, cheater: ' + name
            tag = ''
        elif board.impossiblePoints(person):
            name = '@Arachness_, bugged: ' + name
            tag = ''

    full = name + inter1 + str(board.realRank(rank)) + inter2 + str(board) + inter3 + strPoints

    length = len(full)
    if length + 24 < 140:
        full += ' ' + url
        if length + 24 + len(tag) < 140:
            full += tag

    elif length > 140:
        full = full[:140]
    


    return full




def composeDailyMessage(persons, board, twitter):

    namescore_list = []

    for person in persons:
        twitterHandle = nsb_steam.getTwitterHandle(person['steam_id'], twitter)

        if twitterHandle:
            name = '@' + twitterHandle
        else:
            name = nsb_steam.steamname(int(person['steam_id']), options['steam_key'])
        namescore_list.append(str(name) + ' (' + str(person['points']) + ')')



    namescores_string = ', '.join(map(str, namescore_list))
    date_string = board.board._date.strftime("%b%d")
    url = board.getUrl()
    tag = '#necrodancer'

    return ' '.join(map(str, ["Top scores for", date_string, "Daily:",
            namescores_string, url, tag]))













#TODO: broken
def printBoard():
    index = nsb_index.index()
    index.fetch()

    for entry in index.entries():
        board = nsb_leaderboard.leaderboard(entry, 'xml')
        if board.include() and board.info.character == 'bard':
            board.fetch()
            print(board.topEntries())
    return


    nsb_steam.downloadBoard(lbid, currPath, start, end)
    root = getRoot(path + lbid + '.xml')
    index = getEntryIndex(root)
    for entry in root[index]:
        steamid, score, rank = extractEntry(entry)
        name = steamname(steamid)
        printPlayer(name, rank, score)


#leaderboardurl='http://steamcommunity.com/stats/247080/leaderboards/?xml=1'


#printTop10('695404')

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
