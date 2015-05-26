import nsb_format_points
import nsb_database
import nsb_steam

class leaderboard:
    def __init__(self):
        self.name = 'SRL race rankings'
        self._name = 'srl_race_rankings'
        self.url = 'http://www.speedrunslive.com/races/game/#!/necrodancer/1'
        self._url = 'http://api.speedrunslive.com/leaderboard/necrodancer'

    def __str__(self):
        return self.name

    def parseResponse(self, response):
        return nsb_database.speedrunsliveToList(response)

    def include(self):
        return True

    def unit(self):
        return 'points'

    def pre_unit(self):
        return None

    def parseScore(self, score):
        return str(round(float(score)))

    def entriesToReportOnPointsDiff(self):
        return 0

    def entriesToReportOnRankDiff(self):
        return 20

    def entriesToPrivateReportOnPointsDiff(self):
        return 0

    def entriesToPrivateReportOnRankDiff(self):
        return 100

    def report(self, person, diff=0):
        if person['histPoints'] >= person['points']:
            return False

        if person['histRank'] <= person['rank'] + diff:
            return False

        if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
            return True

        return False

    def getTwitterHandle(self, person, twitter=None):
        url = 'http://api.speedrunslive.com/players/' + person['name']

        response = nsb_steam.fetchUrl(url)
        data = nsb_database.jsonToList(response)
        if data['twitter'] == "":
            return None


        return data['twitter']

        
    def formatPoints(self, points):
        return str(int(float(points)))

    def relativePoints(self, points, prevPoints):
        return nsb_format_points.relativeScore(float(points), float(prevPoints))
 
