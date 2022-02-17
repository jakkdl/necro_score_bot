import time
import concurrent.futures
from typing import Optional, Iterable

import requests

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

    try:
        index = nsb_index.Index()
    except requests.exceptions.ConnectionError as error:
        print(f"failed to fetch index, got {error}")
        return

    boards_to_print = [
        b
        for b in index.boards
        if (
            options["board"].lower() in b.display_name.lower()
            or options["board"].lower() in b.name
        )
    ]

    for board in boards_to_print:
        print(board)
        board.fetch()
        entries = board.top_entries(num)
        for entry in entries:
            print(nsb_format_points.format_message(entry))


def _update_threaded(index: nsb_index.Index, num: int) -> list[nsb_entry.Entry]:
    """Helper function for update(), which runs the main update loop concurrently."""
    res = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Start the load operations and mark each future
        # with its index_entry
        futures = [executor.submit(update_board, board, num) for board in index.boards]

        for future in concurrent.futures.as_completed(futures):
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


def _update_nonthreaded(index: nsb_index.Index, num: int) -> list[nsb_entry.Entry]:
    """Helper function for update(), mostly used for development."""
    res = []
    for board in index.boards:
        data = update_board(board, num)
        if not data:
            continue
        for entry in data:
            if options["debug"]:
                print(entry)
            res.append(entry)
    return res


def update(num_discord: int = 50, num_twitter: int = 5) -> Iterable[str]:
    """Main update function, called by main and nsb_discord."""
    print("start at: ", time.strftime("%c"))

    index = nsb_index.Index()

    num = max(num_discord, num_twitter)
    if options["threaded"]:
        res = _update_threaded(index, num)
    else:
        res = _update_nonthreaded(index, num)

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
    board: nsb_steam_board.SteamBoard, num: int = 100
) -> Optional[list[nsb_entry.Entry]]:

    if options["debug"]:
        print(str(board))

    if not board.has_file() and not options["handle_new"]:
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
#    elif board.impossiblePoints(entry):
#        name = f'{community_manager}, bugged: {name}'


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
