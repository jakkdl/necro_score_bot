import time
import math
import concurrent.futures
import pprint
import sys

import nsb_leaderboard
import nsb_steam_board
import nsb_steam
import nsb_index
import nsb_format_points

from nsb_config import options

def print_board(num=5):
    if not options['board']:
        raise AssertionError('You must specify a board to print')

    index = nsb_index.index()
    index.fetch()

    boards_to_print = [e for e in index.entries() if (
        options['board'].lower() in e['display_name'].lower() or
        options['board'].lower() in e['name'].lower())]

    for index_entry in boards_to_print:
        print(index_entry)
        steam_board = nsb_steam_board.steam_board(index_entry)
        board = nsb_leaderboard.leaderboard(steam_board)
        board.fetch()
        entries = board.topEntries(
                num=num,
                includeBoard=True,
                necrolab_lookup=True)
        for entry in entries:
            print(entry)


def update(twitter=None, numDiscord=50, numTwitter=5):
    print('start at: ', time.strftime('%c'))

    index = nsb_index.index()
    index.fetch()

    res = []
    num = max(numDiscord, numTwitter)
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=50) as executor:
        # Start the load operations and mark each future
        # with its index_entry
        future_to_entry = {
            executor.submit(update_board,
                            index_entry, num): index_entry for index_entry in
            index.entries()}

        future_to_linked_handles = {}
        for future in concurrent.futures.as_completed(future_to_entry):
            entry = future_to_entry[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f'{entry} generated an exception: {exc}')
            else:
                if not data:
                    continue
                for entry in data:
                    print(entry)
                    future_to_linked_handles[executor.submit(
                        nsb_steam.get_linked_handles,
                        entry[1]['steam_id'],
                        options['necrolab'])] = entry

        for future in concurrent.futures.as_completed(future_to_linked_handles):
            data = future_to_linked_handles[future]
            #try:
            linked_data = future.result()
            #except Exception as exc:
            #    print(f"{data} generated an exception: {exc} ; {sys.exc_info()}")
            #else:
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


        if (linked_data['discord']['id'] or
                discord_include(person, board)):
            discord_messages.append((composeMessage(data[1], data[0]),
                                     linked_data))
            #TODO: yield
        else:
            print(f"skipping discord, {data[1]['rank']} < "
                    f"{math.ceil(0.10*len(board.data))} and no id "
                    f"{linked_data['discord']['id']}")

    print('finished at: ', time.strftime('%c'))
    return discord_messages
#=======
#    for index_entry in index.entries():
#        steam_board = nsb_steam_board.steam_board(index_entry)
#        board = nsb_leaderboard.leaderboard(steam_board)
#
#        if not steam_board.include():
#            print('skipping: ', index_entry)
#        else:
#            if options['debug']:
#                print("including: ", str(board))
#
#            if not board.hasFile() and not options['handle-new']:
#                print('New leaderboard', str(board), 'use --handle-new to use')
#                continue
#
#            board.fetch()
#            if options['churn']:
#                if options['backup']:
#                    board.write()
#
#            if not board.hasFile():
#                entries = board.topEntries(5)
#            else:
#                board.read()
#                try:
#                    deletedEntries = board.checkForDeleted(90)
#                except:
#                    print('checkForDeleted threw exception, skipping')
#                    # we probably have an older leaderboard
#                    continue
#                if deletedEntries > 0:
#                    print(f'Found {deletedEntries} deleted entries in {str(board)}')
#                    if deletedEntries >= len(board.history):
#                        raise Exception(
#                            f'ERROR: {deletedEntries} {board} all entries deleted'
#                        )
#                    if deletedEntries >= 30:
#                        raise Exception(
#                            f'ERROR: {deletedEntries} too many deleted entries'
#                        )
#                entries = board.diffingEntries(twitter=twitter)
#>>>>>>> master



def discord_include(person, board):
    entries = len(board.data)
    rank = person['rank']
    if rank <= 3:
        return True
    if board.board._mode == 'score':
        if rank <= math.ceil(entries*0.05):
            return True

        print('score not within 5%')
        return False

    if rank <= math.ceil(entries*0.10):
        return True

    print('entry not within 10%')
    return False


def check_deleted(board, num):
    try:
        deletedEntries = board.checkForDeleted(num)
    except Exception as e:
        print(f'checkForDeleted threw exception {e} in board {board}, skipping')
        #we probably have an older leaderboard
        return True

    if (deletedEntries >= len(board.history) or
        deletedEntries > 60):
        print(f'ERROR: {deletedEntries} too many deleted entries')
        return True
    if deletedEntries > 0:
        print(f"Found {deletedEntries} deleted entries in {board}")
    return False


def update_board(index_entry, num=100):
    steam_board = nsb_steam_board.steam_board(index_entry)
    board = nsb_leaderboard.leaderboard(steam_board)

    if options['debug']:
        print(str(board))

    if not board.hasFile() and not options['handle-new']:
        print(f'New leaderboard {board}, use --handle-new to use')
        return None

    board.fetch()

    if options['churn']:
        entries = None

    elif not board.hasFile():
        entries = board.topEntries(num=5, #TODO: 5?
                                   includeBoard=True,
                                   necrolab_lookup=True)
    else:
        board.read()

        if check_deleted(board, num):
            entries = None
        else:
            entries = board.diffingEntries(num=num, includeBoard=True,
                    necrolab_lookup=True)

    if options['backup']:
        board.write()

    return entries


def compose_tweet(data, linked_data):
    msg = composeMessage(data[1], data[0], url=True)
    handle = linked_data['twitter']['nickname']
    if handle:
        if data[1]['rank'] <= 5:
            return f'.@{handle}{msg}'

        return f'@{handle}{msg}'

    return f"{linked_data['steam']['personaname']} {msg}"





def composeMessage(person, board, url=False):
#def composeMessage(person, board, twitter):
    # score = person['points']
    rank = int(person['rank'])

    if 'histPoints' in person:
        # histPoints = person['histPoints']
        hasHist = True
        histRank = int(person['histRank'])
    else:
        hasHist = False
        histRank = -1
        # histPoints = -1

    localurl = board.getUrl(person)

    strPoints = board.formatPoints(person)

    if rank < histRank or histRank == -1:
        inter1 = ' claims rank '
        if hasHist:
            inter2 = nsb_format_points.relativeRank(rank, histRank) + ' in '
            inter3 = ' '
        else:
            inter2 = ' in '
            inter3 = ' with '
    else:
        inter1 = ', '
        inter2 = nsb_format_points.nth(rank) + ' in '
        inter3 = ', improves'
        # relRank = ''
        if board.board.pre_unit():
            inter3 += ' ' + board.board.pre_unit()
            inter3 += ' to '

    #tag = ' #necrodancer'

    ## TODO: yo this shit is unreadable
    #if 'twitter_username' in person:
    #    twitterHandle = person['twitter_username']
    #else:
    #    twitterHandle = board.getTwitterHandle(person, twitter)

    #if twitterHandle:
    #    name = '@' + twitterHandle
    #    if board.includePublic(person):
    #        name = '.' + name
    #elif 'name' in person:
    #    name = person['name']
    #elif options['steam_key']:
    #    name = nsb_steam.steamname(int(person['steam_id']), options['steam_key'])
    #else:
    #    name = str(person['steam_id'])

    #if 'steam_id' in person:
    #    community_manager = '@NecroDancerGame'
    #    if nsb_steam.known_cheater(person['steam_id']):
    #        name = f'{community_manager}, cheater: {name}'
    #        tag = ''
    #    elif board.impossiblePoints(person):
    #        name = f'{community_manager}, bugged: {name}'
    #        tag = ''


    full = inter1 + str(board.realRank(rank)) + inter2 + str(board) + inter3 + strPoints
    if url:
        full += f' {localurl}'

#   length = len(full)
#   if length + 24 < 140:
    #       full += ' ' + url
    #       if length + 24 + len(tag) < 140:
        #           full += tag

#   elif length > 140:
    #       full = full[:140]



    return full

#    full = (
#        name
#        + inter1
#        + str(board.realRank(rank))
#        + inter2
#        + str(board)
#        + inter3
#        + strPoints
#    )
#
#    length = len(full)
#    if length + 24 < 140:
#        full += ' ' + url
#        if length + 24 + len(tag) < 140:
#            full += tag
#
#    elif length > 140:
#        full = full[:140]
#
#    return full


#def composeDailyMessage(persons, board, twitter):
#
#    namescore_list = []
#
#    for person in persons:
#        twitterHandle = nsb_steam.getTwitterHandle(person['steam_id'], twitter)
#
#        if twitterHandle:
#            name = '@' + twitterHandle
#        else:
#            name = nsb_steam.steamname(int(person['steam_id']), options['steam_key'])
#        namescore_list.append(str(name) + ' (' + str(person['points']) + ')')
#
#    namescores_string = ', '.join(map(str, namescore_list))
#    date_string = board.board._date.strftime("%b%d")
#    url = board.getUrl()
#    tag = '#necrodancer'
#
#    return ' '.join(
#       map(str, ["Top scores for", date_string, "Daily:", namescores_string, url, tag])
#    )
