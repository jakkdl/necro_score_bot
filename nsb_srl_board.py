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
        return 10

    def entriesToPrivateReportOnPointsDiff(self):
        return 0

    def entriesToPrivateReportOnRankDiff(self):
        return 100

    def report(self, person, twitter=None):
        if 'histRank' not in person:
            if person['rank'] <= self.entriesToReportOnRankDiff():
                return True
            if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
                twitter_handle = self.getTwitterHandle(person, twitter)
                if twitter_handle:
                    return True
            return False

        #if the person haven't improved points, return false
        if person['histPoints'] >= person['points']:
            return False

        #if the person haven't improved rank, return false
        if person['histRank'] <= person['rank']:
            return False

        #Check for public tweet
        if person['rank'] <= self.entriesToReportOnRankDiff():
            return True
        #Check for private tweet
        if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
            twitter_handle = self.getTwitterHandle(person, twitter)
            if twitter_handle:
                person['twitter_username'] = twitter_handle
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

    def impossiblePoints(self, person):
        return False
    
    def getUrl(self, person):
        return self.url
