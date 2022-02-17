"This file handles all the main leaderboard parsing and update logic"
import pickle
import os.path
from abc import abstractmethod
from typing import Optional

import nsb_entry

from nsb_config import options
from nsb_abc import BoardEntry


class Leaderboard:
    def __init__(self, name: str):
        # TODO: call read and fetch on init
        self.name: str = name.lower()
        self.mode: str = ""
        self.data: list[BoardEntry] = []
        self.history: list[BoardEntry] = []

        # Some other board has "name" as key, but don't remember what
        self.path = os.path.join(options["data"], "boards", f"{self.name}.pickle")

    def has_file(self) -> bool:
        return self.path is not None and os.path.isfile(self.path)

    def read(self) -> None:
        with open(self.path, "rb") as file:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.history = pickle.load(file)

    def write(self) -> None:
        if self.data is None:
            raise Exception("Trying to pickle with no data read")
        with open(self.path, "wb") as file:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.data, file, pickle.HIGHEST_PROTOCOL)

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def fetch(self) -> None:
        pass
        # url = nsb_steam.board_url(self.lbid, 1, 100)
        # response = nsb_steam.fetch_url(self._url)
        # self.data = self.board.parseResponse(response)

    @abstractmethod
    def impossible_score(self, data: BoardEntry) -> bool:
        pass

    def top_entries(self, num: Optional[int] = None) -> list[nsb_entry.Entry]:
        if num is None:
            num = options["public_report_rank_diff"]
        assert isinstance(self.data, list)
        num = min(num, len(self.data))
        res = []
        for board_entry in self.data:
            if not self.impossible_score(board_entry):
                board_entry.rank = self.real_rank(board_entry.rank)
                res.append(
                    nsb_entry.Entry(
                        board_entry, board=self, template=self.get_template(board_entry)
                    )
                )
            if len(res) == num:
                break
        return res

    def check_for_deleted(self, num: int) -> int:
        deleted = 0
        # num = 150
        # print(len(self.history))
        # print(len(self.data))
        # for hist in self.history[:num]:
        assert isinstance(self.history, list)
        assert isinstance(self.data, list)
        for i in range(min(num, len(self.history))):
            hist = self.history[i]
            found = False
            for person in self.data[: num + 20]:
                if person.uid == hist.uid:
                    if person.points >= hist.points:
                        # print(self.history.index(hist), self.data.index(person))
                        found = True
                    else:
                        print(
                            f"Found deleted entry due to less points\n"
                            f"new: {person}\nold: {hist}"
                        )
                        raise Exception(
                            "ERROR: Found deleted entry due to less points", person
                        )
                    break
            if not found:
                # deleted.append(i)
                deleted += 1
        return deleted

    def get_template(self, curr: BoardEntry, hist: Optional[BoardEntry] = None) -> str:
        if hist is None:
            return options[f"{self.mode}_message_new_entry"]  # type: ignore
        if curr.rank == hist.rank:
            return options[f"{self.mode}_message_same_rank"]  # type: ignore
        return options[f"{self.mode}_message_new_rank"]  # type: ignore

    def diffing_entries(self, num: Optional[int] = None) -> list[nsb_entry.Entry]:
        assert self.data is not None
        assert self.history is not None

        if not self.data:
            return []

        result = []

        if num is None:
            num = max(
                options["private_report_rank_diff"],
                options["private_report_points_diff"],
                options["public_report_rank_diff"],
                options["public_report_points_diff"],
            )

        num = min(num, len(self.data))
        if num == 0:
            return []

        # Save all players according to unique key for fast lookup
        curr_entries = {e.uid: e for e in self.data[:num]}

        for hist in self.history[: max(len(self.data) // 2, num + 50)]:
            if not curr_entries:
                break

            curr = curr_entries.pop(hist.uid, None)

            if curr is None:
                continue

            # If the person haven't improved points, don't include
            if hist.points >= curr.points:
                continue

            hist.rank = self.real_rank(hist.rank)
            curr.rank = self.real_rank(curr.rank)

            template = self.get_template(curr, hist)

            entry = nsb_entry.Entry(
                board=self, data=curr, hist_data=hist, template=template
            )
            if not entry.report():
                continue
            result.append(entry)

        # TODO: this is the dangerous loop, and will often also include only cheaters
        # and garbage records. Maybe special-case for small boards only?
        for data in curr_entries.values():
            data.rank = self.real_rank(data.rank)
            template = self.get_template(data)
            entry = nsb_entry.Entry(board=self, data=data, template=template)
            if not entry.report():
                continue
            result.append(entry)

        return result

    # @staticmethod
    # def known_cheater(steam_id: str) -> bool:
    #    filename = "known_cheaters.txt"
    #    if not os.path.isfile(filename):
    #        filename = os.path.dirname(os.path.realpath(__file__)) + "/" + filename

    #    with open(filename, "r", encoding="utf-8") as file:
    #        for line in file:
    #            if int(line) == int(steam_id):
    #                return True
    #    return False

    def real_rank(self, rank: int) -> int:
        assert self.data is not None
        subtract = 0
        for i in self.data[: rank - 1]:
            if self.impossible_score(i):  # or self.known_cheater(i["steam_id"]):
                # print(i)
                subtract += 1
        return rank - subtract

    # def includePublic(self, entry):
    #    rank = int(entry['rank'])
    #    if rank <= self.board.entriesToReportOnRankDiff():
    #        # print('rankdiff')
    #        return True
    #    if rank <= self.board.entriesToReportOnPointsDiff():
    #        # print('pointsdiff')
    #        return True
    #    return False

    # def includePrivate(self, entry, twitter):
    #    rank = int(entry['rank'])
    #    if (
    #        rank < self.board.entriesToPrivateReportOnRankDiff()
    #        or rank < self.board.entriesToPrivateReportOnPointsDiff()
    #    ):
    #        if 'twitter_username' in entry and entry['twitter_username']:
    #            return True
    #        twitterHandle = nsb_steam.get_twitter_handle(entry['steam_id'], twitter)
    #        if twitterHandle:
    #            # print('handle:', twitterHandle)
    #            entry['twitter_username'] = twitterHandle
    #            return True
    #    return False

    @abstractmethod
    def pretty_url(self, person: Optional[nsb_entry.Entry] = None) -> str:
        pass
