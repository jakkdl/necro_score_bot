import time
import math
import concurrent.futures
import typing

import nsb_leaderboard
import nsb_steam_board
import nsb_index
import nsb_entry
import nsb_format_points

from nsb_config import options


def print_board(num=5):
    if not options["board"]:
        raise AssertionError("You must specify a board to print")

    index = nsb_index.Index()
    index.fetch()

    boards_to_print = [
        e
        for e in index.entries()
        if (
            options["board"].lower() in e["display_name"].lower()
            or options["board"].lower() in e["name"].lower()
        )
    ]

    for index_entry in boards_to_print:
        print(index_entry)
        board = nsb_steam_board.SteamBoard(index_entry)
        board.fetch()
        entries = board.top_entries(num)
        for entry in entries:
            print(nsb_format_points.format_message(entry))


def update_threaded(index, num) -> typing.List[nsb_entry.Entry]:
    res = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Start the load operations and mark each future
        # with its index_entry
        future_to_entry = {
            executor.submit(update_board, index_entry, num): index_entry
            for index_entry in index.entries()
        }

        for future in concurrent.futures.as_completed(future_to_entry):
            index_entry = future_to_entry[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f"{entry} generated an exception: {exc}")
            else:
                for entry in data:
                    if options["debug"]:
                        print(entry)
                    res.append(entry)
    return res


def update_nonthreaded(index, num) -> typing.List[nsb_entry.Entry]:
    res = []
    for index_entry in index.entries():
        data = update_board(index_entry, num)
        for entry in data:
            if options["debug"]:
                print(entry)
            res.append(entry)
    return res


def update(num_discord=50, num_twitter=5):
    print("start at: ", time.strftime("%c"))

    index = nsb_index.Index()
    index.fetch()

    num = max(num_discord, num_twitter)
    if options["threaded"]:
        res = update_threaded(index, num)
    else:
        res = update_nonthreaded(index, num)

    discord_messages = []
    for entry in res:
        print(entry)
        # tweet if linked_twitter, or rank < public_tweet_limit
        # t = compose_tweet(data, linked_data)
        # twitter.postTweet(t)
        # discord message if linked_discord or rank < public_discord_limit
        # yield
        # discord_messages.append((compose_message(data[1], data[0]), linked_data))

    print("finished at: ", time.strftime("%c"))
    return discord_messages


# =======
#    for index_entry in index.entries():
#        steam_board = nsb_steam_board.SteamBoard(index_entry)
#        board = nsb_leaderboard.Leaderboard(steam_board)
#
#        if not steam_board.include():
#            print('skipping: ', index_entry)
#        else:
#            if options['debug']:
#                print("including: ", str(board))
#
#            if not board.has_file() and not options['handle-new']:
#                print('New leaderboard', str(board), 'use --handle-new to use')
#                continue
#
#            board.fetch()
#            if options['churn']:
#                if options['backup']:
#                    board.write()
#
#            if not board.has_file():
#                entries = board.top_entries(5)
#            else:
#                board.read()
#                try:
#                    deleted_entries = board.check_for_deleted(90)
#                except:
#                    print('check_for_deleted threw exception, skipping')
#                    # we probably have an older leaderboard
#                    continue
#                if deleted_entries > 0:
#                    print(f'Found {deleted_entries} deleted entries in {str(board)}')
#                    if deleted_entries >= len(board.history):
#                        raise Exception(
#                            f'ERROR: {deleted_entries} {board} all entries deleted'
#                        )
#                    if deleted_entries >= 30:
#                        raise Exception(
#                            f'ERROR: {deleted_entries} too many deleted entries'
#                        )
#                entries = board.diffing_entries(twitter=twitter)
# >>>>>>> master


def discord_include(entry, board):
    entries = len(board.data)
    rank = entry["rank"]
    if rank <= 3:
        return True
    if board.board._mode == "score":
        if rank <= math.ceil(entries * 0.05):
            return True

        print("score not within 5%")
        return False

    if rank <= math.ceil(entries * 0.10):
        return True

    print("entry not within 10%")
    return False


def check_deleted(board, num):
    try:
        deleted_entries = board.check_for_deleted(num)
    except Exception as exc:
        print(f"check_for_deleted threw exception {exc} in board {board}, skipping")
        # we probably have an older leaderboard
        return True

    if deleted_entries >= len(board.history) or deleted_entries > 60:
        print(f"ERROR: {deleted_entries} too many deleted entries")
        return True
    if deleted_entries > 0:
        print(f"Found {deleted_entries} deleted entries in {board}")
    return False


def update_board(index_entry, num=100):
    steam_board = nsb_steam_board.SteamBoard(index_entry)
    board = nsb_leaderboard.Leaderboard(steam_board)

    if options["debug"]:
        print(str(board))

    if not board.has_file() and not options["handle-new"]:
        print(f"New leaderboard {board}, use --handle-new to use")
        return None

    board.fetch()

    if options["churn"]:
        entries = None
    elif not board.has_file():
        entries = board.top_entries(num=5)
    else:
        board.read()

        if check_deleted(board, num):
            entries = None
        else:
            entries = board.diffing_entries(num=num)

    if options["backup"]:
        board.write()

    return entries


def compose_tweet(data, linked_data):
    msg = compose_message(data[1], data[0], url=True)
    handle = linked_data["twitter"]["nickname"]
    if handle:
        if data[1]["rank"] <= 5:
            return f".@{handle}{msg}"

        return f"@{handle}{msg}"

    return f"{linked_data['steam']['personaname']} {msg}"

    # tag = ' #necrodancer'

    ## TODO: yo this shit is unreadable
    # if 'twitter_username' in entry:
    #    twitterHandle = entry['twitter_username']
    # else:
    #    twitterHandle = board.getTwitterHandle(entry, twitter)

    # if twitterHandle:
    #    name = '@' + twitterHandle
    #    if board.includePublic(entry):
    #        name = '.' + name
    # elif 'name' in entry:
    #    name = entry['name']
    # elif options['steam_key']:
    #    name = nsb_steam.steamname(int(entry['steam_id']), options['steam_key'])
    # else:
    #    name = str(entry['steam_id'])

    # if 'steam_id' in entry:
    #    community_manager = '@NecroDancerGame'
    #    if nsb_steam.known_cheater(entry['steam_id']):
    #        name = f'{community_manager}, cheater: {name}'
    #        tag = ''
    #    elif board.impossiblePoints(entry):
    #        name = f'{community_manager}, bugged: {name}'
    #        tag = ''

    #   length = len(full)
    #   if length + 24 < 140:
    #       full += ' ' + url
    #       if length + 24 + len(tag) < 140:
    #           full += tag

    #   elif length > 140:
    #       full = full[:140]


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


# def composeDailyMessage(persons, board, twitter):
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
#    url = board.pretty_url()
#    tag = '#necrodancer'
#
#    return ' '.join(
#       map(str, ["Top scores for", date_string, "Daily:", namescores_string, url, tag])
#    )
