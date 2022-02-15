import pickle
import os.path

import nsb_steam

from nsb_config import options


class leaderboard:
    def __init__(self, board):
        self.board = board

        self.data = None
        self.history = None

        self.path = os.path.join(options["data"], "boards", board._name + ".pickle")

    def hasFile(self):
        return self.path is not None and os.path.isfile(self.path)

    def read(self):
        with open(self.path, "rb") as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.history = pickle.load(f)

    def write(self):
        if self.data is None:
            raise Exception("Trying to pickle with no data read")
        with open(self.path, "wb") as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def fetch(self):
        # url = nsb_steam.boardUrl(self.lbid, 1, 100)
        response = nsb_steam.fetchUrl(self.board._url)
        self.data = self.board.parseResponse(response)

    def topEntries(self, num=None, includeBoard=False, necrolab_lookup=False):
        if not num:
            num = self.board.entriesToPrivateReportOnRankDiff()
        num = min(num, len(self.data))
        res = []
        for i in range(num):
            if necrolab_lookup:
                pass
            res.append((self, self.data[i]))
        return res

    def checkForDeleted(self, num):
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

    # def diffingEntries(self, num=1,
    #        includeBoard = False,
    def diffingEntries(
        self, num=None, twitter=None, includeBoard=False, necrolab_lookup=False
    ):
        if self.data is None:
            raise Exception("No data")
        if self.history is None:
            raise Exception("No history")

        if not self.data:
            return []

        result = []

        rankMax = max(
            self.board.entriesToReportOnRankDiff(),
            self.board.entriesToPrivateReportOnRankDiff(),
        )

        if num is None:
            num = rankMax

        num = min(num, len(self.data))
        if num == 0:
            return []

        if "steam_id" in self.data[0]:
            key = "steam_id"
        else:
            key = "name"

        for person in self.data[:num]:
            found = False
            include = False

            for hist in self.history[: num + 10]:  # TODO: 10?
                # for hist in self.history:
                if person[key] == hist[key]:
                    found = True

                    if self.board.report(person, hist, twitter=twitter):
                        # if person['points'] > hist['points']:
                        person["histRank"] = hist["rank"]
                        person["histPoints"] = hist["points"]
                        include = True
                    break

            if not found or include:
                if includeBoard:
                    result.append((self, person))
                else:
                    result.append(person)

        return result

    def realRank(self, rank):
        subtract = 0
        for i in self.data[: rank - 1]:
            if self.impossiblePoints(i) or nsb_steam.known_cheater(i["steam_id"]):
                # print(i)
                subtract += 1
        return rank - subtract

    def __str__(self):
        return str(self.board)

    def __info__(self):
        return str(self.board)

    def __repr__(self):
        # print(self.orig_name)
        # return repr(self.info())
        return str(self.board)

    def formatPoints(self, person):
        strPoints = self.board.formatPoints(person["points"])
        if "histPoints" in person:
            strPoints += self.board.relativePoints(
                person["points"], person["histPoints"]
            )
        if self.board.unit():
            strPoints += " " + self.board.unit()
        return strPoints

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
    #        twitterHandle = nsb_steam.getTwitterHandle(entry['steam_id'], twitter)
    #        if twitterHandle:
    #            # print('handle:', twitterHandle)
    #            entry['twitter_username'] = twitterHandle
    #            return True
    #    return False

    def getTwitterHandle(self, person, twitter):
        return self.board.getTwitterHandle(person, twitter)

    def impossiblePoints(self, person):
        return self.board.impossiblePoints(person)

    def getUrl(self, person=None):
        return self.board.getUrl(person)
