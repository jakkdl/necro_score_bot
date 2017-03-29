




class nsb_entry:
    def __init__(self, steamid, score, rank, histScore=None, histRank=None):
        self._steamid = steamid
        self._score = score
        self._rank = rank
        self._histScore = histScore
        self._histRank = histRank



def generate_entries(entrylist):
    result = []
    for p in entrylist:
        result.append(nsb_entry(
            steamid = p['steam_id'],
            score   = p['points'],
            rank    = p['rank']
            ))


