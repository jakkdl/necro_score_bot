import time
import concurrent.futures
from typing import Optional, Iterable

import nsb_leaderboard
import nsb_steam_board
import nsb_index
import nsb_entry
import nsb_format_points

from nsb_twitter import twitter
from nsb_config import options


def print_board(num: int = 5) -> None:
    if not options["board"]:
        raise AssertionError("You must specify a board to print")

    index = nsb_index.Index()

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


def update_threaded(index: nsb_index.Index, num: int) -> list[nsb_entry.Entry]:
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
            # except Exception as exc:
            #    print(f"{index_entry} generated an exception: {exc}")
            # else:
            finally:
                if not data:
                    continue
                for entry in data:
                    if options["debug"]:
                        print(entry)
                    res.append(entry)
    return res


def update_nonthreaded(index: nsb_index.Index, num: int) -> list[nsb_entry.Entry]:
    res = []
    for index_entry in index.entries():
        data = update_board(index_entry, num)
        if not data:
            continue
        for entry in data:
            if options["debug"]:
                print(entry)
            res.append(entry)
    return res


def update(num_discord: int = 50, num_twitter: int = 5) -> Iterable[str]:
    print("start at: ", time.strftime("%c"))

    index = nsb_index.Index()

    num = max(num_discord, num_twitter)
    if options["threaded"]:
        res = update_threaded(index, num)
    else:
        res = update_nonthreaded(index, num)

    for entry in res:
        print(entry)
        twitter_handle = entry.linked_accounts.get("twitter_handle", None)
        name = ""
        if twitter_handle:
            if entry.score.rank < 3:
                name = f".@{twitter_handle}"
            else:
                name = f"@{twitter_handle}"
        elif entry.score.rank < 3:
            name = str(entry)

        if name:
            twitter.post_tweet(nsb_format_points.format_message(entry, name))

        discord_id = entry.linked_accounts.get("discord_id", None)

        name = ""
        if discord_id:
            name = f"<@{discord_id}>"
        elif entry.score.rank < 3:
            name = str(entry)
        if name:
            yield nsb_format_points.format_message(entry, name)

    print("finished at: ", time.strftime("%c"))


# def discord_include(entry, board):
#    entries = len(board.data)
#    rank = entry["rank"]
#    if rank <= 3:
#        return True
#    if board.board._mode == "score":
#        if rank <= math.ceil(entries * 0.05):
#            return True
#
#        print("score not within 5%")
#        return False
#
#    if rank <= math.ceil(entries * 0.10):
#        return True
#
#    print("entry not within 10%")
#    return False


def check_deleted(board: nsb_leaderboard.Leaderboard, num: int) -> bool:
    try:
        deleted_entries = board.check_for_deleted(num)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"check_for_deleted threw exception {exc} in board {board}, skipping")
        # we probably have an older leaderboard
        return True

    if deleted_entries >= len(board.history) or deleted_entries > 60:
        print(f"ERROR: {deleted_entries} too many deleted entries")
        return True
    if deleted_entries > 0:
        print(f"Found {deleted_entries} deleted entries in {board}")
    return False


def update_board(
    index_entry: dict[str, str], num: int = 100
) -> Optional[list[nsb_entry.Entry]]:
    board = nsb_steam_board.SteamBoard(index_entry)

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


# def composeDailyMessage(persons, board, twitter):
#
#    namescore_list = []
#
#    for person in persons:
#        twitterHandle = nsb_steam.get_twitter_handle(person['steam_id'], twitter)
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
