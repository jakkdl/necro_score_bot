import nsb_format_points
import nsb_database

def readable_name(name):
    split_name = name.split('_')
    return ' '.join([split_name[0], split_name[-1]])
    #result = name.replace('deathless_score', 'deathless')
    #result = name.replace('_', ' ')
    #return result



    


class leaderboard:


    def __init__(self, name, other_boards):
        self._name = name
        self.name = readable_name(name)
        if name == 'power_rankings':
            self.boards = other_boards

        baseurl = 'http://www.necrolab.com/'
        self.url = baseurl + name
        self._url = baseurl + 'api/' + name + '/latest_rankings'

        self.date = None


    def __str__(self):
        return self.name

    def parseResponse(self, response):
        return nsb_database.necrolabToList(response)

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

    def report(self, person, hist, twitter=None):
        if hist is None:
            if person['rank'] <= self.entriesToReportOnRankDiff():
                return True
            #Check for private tweet
            if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
                twitter_handle = self.getTwitterHandle(person, twitter)
                if twitter_handle:
                    return True
            return False

        if float(hist['points']) >= person['points']:
            return False

        if int(hist['rank']) <= person['rank']:
            return False

        #TODO: Add check that one of the users personal ranks have risen
        if self._name == 'power_rankings':
            if not self.improvedCharRankOnBoards(person, boards):
                return False
        elif not self.improvedCharRank(person, hist):
            print(person['name'], 'didnt improve char rank')
            return False


        if person['rank'] <= self.entriesToReportOnRankDiff():
            return True

        if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
            if person['twitter_username']:
                return True

        return False
    
    def improvedCharRank(self, person, hist):
        for key in person.keys():
            if 'rank' not in key or key == 'rank':
                continue
            if hist[key] is None:
                if person[key] is not None:
                    print(person['name'], key, 'added')
                    return True
            elif person[key] is None:
                print('got removed score:', person)
            elif person[key] < hist[key]:
                print(person['name'], key, 'improved')
                return True
        return False



    def getTwitterHandle(self, person, twitter=None):
        return person['twitter_username']
    
    def formatPoints(self, points):
        return str(int(float(points)))

    def relativePoints(self, points, prevPoints):
        return nsb_format_points.relativeScore(float(points), float(prevPoints))

    def impossiblePoints(self, person):
        return False
    
    def getUrl(self, person):
        return self.url
