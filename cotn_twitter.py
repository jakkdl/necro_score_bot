import xml.etree.ElementTree as ET
import os
import os.path
import time
import datetime

import nsb_leaderboard
import nsb_steam_board
import nsb_steam
import nsb_index
import nsb_database
import nsb_format_points

from nsb_config import options

def update(twitter):
    print('start at: ', time.strftime('%c'))

    index = nsb_index.index()
    index.fetch()


    for index_entry in index.entries():
        steam_board = nsb_steam_board.steam_board(index_entry)
        board = nsb_leaderboard.leaderboard(steam_board)

        if not steam_board.include():
            print('skipping: ', index_entry)
        else:
            if options['debug']:
                print("including: ", str(board))

            if not board.hasFile() and not options['handle-new']:
                print('New leaderboard', str(board), 'use --handle-new to use')
                continue

            board.fetch()
            if options['churn']:
                if options['backup']:
                    board.write()


            if not board.hasFile():
                entries = board.topEntries(5)
            else:
                board.read()
                try:
                    deletedEntries = board.checkForDeleted(90)
                except:
                    print('checkForDeleted threw exception, skipping')
                    #we probably have an older leaderboard
                    continue
                if deletedEntries > 0:
                    print("Found", deletedEntries, "deleted entries in", str(board))
                if deletedEntries > len(board.history):
                    raise Exception('ERROR: {} {} all entries deleted'.format(deletedEntries, board))
                if deletedEntries > 60:
                    raise Exception('ERROR: {} too many deleted entries'.format(deletedEntries))
                entries = board.diffingEntries(twitter=twitter)

            for entry in entries:
                message = composeMessage(entry, board, twitter)
                if options['tweet']:
                    twitter.postTweet(message)
                if options['debug']:
                    print(message.encode('ascii', 'replace'))

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
        if options['debug']:
            print(message)

def composeMessage(person, board, twitter):
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
        inter2 = nsb_format_points.nth(rank) + ' in '
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
        community_manager = '@NecroDancerGame'
        if nsb_steam.known_cheater(person['steam_id']):
            name = '{}, cheater: {}'.format(community_manager, name)
            tag = ''
        elif board.impossiblePoints(person):
            name = '{}, bugged: {}'.format(community_manager, name)
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
