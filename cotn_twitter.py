import xml.etree.ElementTree as ET
import os
import os.path
import time
import math
import datetime
import concurrent.futures
import sys
import pprint

import nsb_leaderboard
import nsb_steam_board
import nsb_steam
import nsb_index
import nsb_database
import nsb_format_points

from nsb_config import options

def update(twitter=None, numDiscord=50, numTwitter=5):
    print('start at: ', time.strftime('%c'))

    index = nsb_index.index()
    index.fetch()

    entries = []
#for index_entry in index.entries():
#    res = update_board(index_entry)
#    if res:
#        entries.append(res)
    res = []
    num = max(numDiscord, numTwitter)
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=50) as executor:
        # Start the load operations and mark each future
        # with its index_entry
        future_to_entry = {executor.submit(update_board,
            index_entry, num): index_entry for index_entry in
            index.entries()}

        future_to_linked_handles = {}
        for future in concurrent.futures.as_completed(
                future_to_entry):
            entry = future_to_entry[future]
            try:
                data = future.result()
            except Exception as exc:
                print('{} generated an exception: {}'.format(
                    url, exc))
            else:
                if not data:
                    continue
                for entry in data:
                    print(entry)
                    future_to_linked_handles[executor.submit(
                        nsb_steam.get_linked_handles,
                        entry[1]['steam_id'])] = entry;

        for future in concurrent.futures.as_completed(
                future_to_linked_handles):
            data = future_to_linked_handles[future]
            try:
                linked_data = future.result()
            except Exception as exc:
                print('{} generated an exception: {} ; {}'.format(
                    data, exc, sys.exc_info()))
            else:
                res.append((data, linked_data))
                if options['debug']:
                    pprint.pprint((data, linked_data))
    
    discord_messages = []
    for data, linked_data in res:
        board = data[0]
        person = data[1]
        if (linked_data['twitter']['nickname'] or
                (not data[0].board._seeded
                    and data[1]['rank'] <= numTwitter)):
            t = compose_tweet(data, linked_data)
            if options['debug']:
                print(t)
            if options['tweet'] and twitter:
                twitter.postTweet(t)
        else:
            print('skipping twitter')


        if (linked_data['discord']['username'] or
                data[1]['rank'] <= math.ceil(0.10*len(board.data))):
            discord_messages.append((composeMessage(data[1], data[0]),
                linked_data))
            #TODO: yield
        else:
            print('skipping discord, {} < {}'.format(data[1]['rank'],
                math.ceil(0.10*len(board.data))))

    print('finished at: ', time.strftime('%c'))
    return discord_messages
    






def update_board(index_entry, num=100):
    steam_board = nsb_steam_board.steam_board(index_entry)
    board = nsb_leaderboard.leaderboard(steam_board)

    #if options['debug']:
        #print(str(board))

    if not board.hasFile() and not options['handle-new']:
        print('New leaderboard {}, use --handle-new to use'.format(str(board)))
        return

    board.fetch()
    if options['churn']:
        if options['backup']:
            board.write()


    if not board.hasFile():
        entries = board.topEntries(num=5, #TODO: 5?
                includeBoard = True,
                necrolab_lookup = True)
        if options['backup']:
            board.write()
        return entries

    board.read()
    try:
        deletedEntries = board.checkForDeleted(num)
    except:
        print('checkForDeleted threw exception in board {}, skipping'.format(
            str(board)))
        #we probably have an older leaderboard
        return []

    if deletedEntries > 0:
        print("Found {} deleted entries in {}".format(
            deletedEntries, str(board)))
        return 

    if deletedEntries > len(board.history): #TODO: >=?
        print('ERROR: {} {} all entries deleted'.format(deletedEntries, board))
        return

    if deletedEntries > 60:
        print('ERROR: {} too many deleted entries'.format(deletedEntries))
        return

    entries = board.diffingEntries(num=num, includeBoard = True,
            necrolab_lookup = True)
    if options['backup']:
        board.write()
    return entries





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

def compose_tweet(data, linked_data):
    msg = composeMessage(data[1], data[0], url=True)
    handle = linked_data['twitter']['name']
    if handle:
        if data[1]['rank'] <= 5:
            return '.@{} {}'.format(handle, msg)
        else:
            return '@{} {}'.format(handle, msg)
    else:
        return '{} {}'.format(linked_data['steam']['personaname'], msg)





def composeMessage(person, board, url=False):
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

    localurl = board.getUrl(person)

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



    full = inter1 + str(board.realRank(rank)) + inter2 + str(board) + inter3 + strPoints
    if url:
        full += ' {}'.format(localurl)

#   length = len(full)
#   if length + 24 < 140:
#       full += ' ' + url
#       if length + 24 + len(tag) < 140:
#           full += tag

#   elif length > 140:
#       full = full[:140]
    


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
