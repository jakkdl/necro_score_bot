import pickle
import os.path
import abc

import nsb_steam
import nsb_entry

from nsb_config import options


class Leaderboard:
    def __init__(self, name, key="steam_id"):
        self.mode = None
        self.data = None
        self.history = None

        # Some other board has "name" as key, but don't remember what
        self.key = key

        self.path = os.path.join(options["data"], "boards", name + ".pickle")

    def has_file(self):
        return self.path is not None and os.path.isfile(self.path)

    def read(self):
        with open(self.path, "rb") as file:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.history = pickle.load(file)

    def write(self):
        if self.data is None:
            raise Exception("Trying to pickle with no data read")
        with open(self.path, "wb") as file:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.data, file, pickle.HIGHEST_PROTOCOL)

    @abc.abstractmethod
    def fetch(self):
        pass
        # url = nsb_steam.board_url(self.lbid, 1, 100)
        # response = nsb_steam.fetch_url(self._url)
        # self.data = self.board.parseResponse(response)

    @abc.abstractmethod
    def impossible_score(self, data):
        pass

    def top_entries(self, num=None):
        if num is None:
            num = options["public_report_rank_diff"]
        num = min(num, len(self.data))
        res = []
        for data in self.data:
            if not self.impossible_score(data):
                data["rank"] = self.real_rank(data["rank"])
                res.append(
                    nsb_entry.Entry(data, board=self, template=self.get_template(data))
                )
            if len(res) == num:
                break
        return res

    def check_for_deleted(self, num):
        deleted = 0
        # num = 150
        # print(len(self.history))
        # print(len(self.data))
        # for hist in self.history[:num]:
        for i in range(min(num, len(self.history))):
            hist = self.history[i]
            found = False
            for person in self.data[: num + 20]:
                if person["steam_id"] == int(hist["steam_id"]):
                    if int(person["points"]) >= int(hist["points"]):
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

    def get_template(self, curr, hist=None):
        if hist is None:
            return options[f"{self.mode}_message_new_entry"]
        if curr.rank == hist.rank:
            return options[f"{self.mode}_message_same_rank"]
        return options[f"{self.mode}_message_new_rank"]

    def diffing_entries(self, num=None):
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
        curr_entries = {e[self.key]: e for e in self.data[:num]}

        for hist in self.history[: max(len(self.data) // 2, num + 50)]:
            if not curr_entries:
                break

            curr_entry = curr_entries.pop(hist[self.key], None)

            if curr_entry is None:
                continue

            # If the person haven't improved points, don't include
            if float(hist["points"]) >= curr_entry["points"]:
                continue

            hist["rank"] = self.real_rank(hist["rank"])
            curr_entry["rank"] = self.real_rank(curr_entry["rank"])

            template = self.get_template(curr_entry, hist)

            entry = nsb_entry.Entry(
                board=self, data=curr_entry, hist_data=hist, template=template
            )
            if not entry.report():
                continue
            result.append(entry)

        # TODO: this is the dangerous loop, and will often also include only cheaters
        # and garbage records. Maybe special-case for small boards only?
        for curr_entry in curr_entries:
            curr_entry["rank"] = self.real_rank(curr_entry["rank"])
            template = self.get_template(curr_entry)
            entry = nsb_entry.Entry(board=self, data=curr_entry, template=template)
            if not entry.report():
                continue
            result.append(entry)

        return result

    def real_rank(self, rank):
        subtract = 0
        for i in self.data[: rank - 1]:
            if self.impossible_score(i) or nsb_steam.known_cheater(i["steam_id"]):
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

    @abc.abstractmethod
    def pretty_url(self, person=None):
        pass
