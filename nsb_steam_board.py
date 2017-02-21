import datetime

import nsb_database
import nsb_format_points
import nsb_steam
import nsb_index


class steam_board:

    def __init__(self, lbid):
        self._lbid = lbid
        self._character = nsb_index.index.character(lbid)
        self._mode = nsb_index.index.mode(lbid)
        self._seeded = nsb_index.index.seeded(lbid)

        #self._date = self.extractDate(name)

        self._name = self._character
        if self._seeded:
            self._name += '_seeded'
        self._name += '_' + self._mode


        #self._name = self.nice_name()
        #print(self._character, self._mode)

        self.url = self.toofzUrl()
        self._url = self.toofzUrl()


    def nice_name(self):
        ##TODO: Make up a pretty solution for all boards and write/implement
        if self.daily():
            return str(self._date)
        if self._character == None or self._mode == None:
            return 'None'
        result = self._character
        if self._seeded:
            result += ' seeded'
        result += ' ' + self._mode
        return result.title()
    
    def __str__(self):
        return self._name

    def __repr__(self):
        name = ''
        name += 'character: ' + str(self._character) + '\n'
        name += 'mode: ' + str(self._mode) + '\n'
        name += 'seeded: ' + str(self._seeded) + '\n'
        return name


    def daily(self):
        return self._mode == 'daily'

    
    def extractDate(self, name):
        if not self.daily():
            return None
        name = name.replace('_dev', '')
        name = name.replace('_prod', '')
        sp = name.split()[0]
        sp = sp.split('/')
        return datetime.date(int(sp[2]), int(sp[1]), int(sp[0]))


    def maxCompareEntries(self):
        return 100
    
 

    
    def toofzSupport(self):
        if self._coop or self._customMusic:
            return False
        if self._mode == None:
            return False
        return True

    
    def toofzUrl(self):
        base = 'http://crypt.toofz.com/Leaderboards/'
        if self.daily():
            return base + 'Daily/' + self._date.strftime('%Y/%m/%d/')
        #http://crypt.toofz.com/Leaderboards/Daily/2015/05/27
        char = self._character
        mode = self._mode
        return base + '%s/%s'%(char, mode)

    def parseResponse(self, response):
        return nsb_database.xmlToList(response, 'leaderboard')
    
    
    @staticmethod
    def getTwitterHandle(person, twitter):
        return nsb_steam.getTwitterHandle(int(person['steam_id']), twitter)



    def entriesToReportOnPointsDiff(self):
        return 5

    def entriesToReportOnRankDiff(self):
        return 10

    def entriesToPrivateReportOnPointsDiff(self):
        return 100

    def entriesToPrivateReportOnRankDiff(self):
        return 100
    
    def report(self, person, hist, twitter):

        if hist is None:
            if person['rank'] <= self.entriesToReportOnRankDiff():
                return True
            #Check for private tweet
            if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
                twitter_handle = self.getTwitterHandle(person, twitter)
                if twitter_handle:
                    return True
            return False

        #If the person haven't improved points, return false
        if float(hist['points']) >= person['points']:
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
    
    def formatPoints(self, points):
        points = int(points)
        if self._mode == 'speed':
            time = nsb_format_points.scoreAsMilliseconds(points)
            return nsb_format_points.formatTime(time)
        if self._mode == 'score':
            return str(int(points))
        if self._mode == 'deathless':
            return nsb_format_points.formatProgress(points)
    
    def relativePoints(self, points, prevPoints):
        points = int(points)
        prevPoints = int(prevPoints)
        if self._mode == 'speed':
            points = nsb_format_points.scoreAsMilliseconds(points)
            prevPoints = nsb_format_points.scoreAsMilliseconds(prevPoints)
            return nsb_format_points.relativeTime(points, prevPoints)
        if self._mode == 'score':
            return  nsb_format_points.relativeScore(points, prevPoints)
        if self._mode == 'deathless':
            return nsb_format_points.relativeProgress(points, prevPoints)

    def impossiblePoints(self, person):
        if self._mode == 'score' and person['points'] > 200000:
            return True
        return False

    def unit(self):
        if self._mode == 'score':
            return 'gold'
        return None

    def pre_unit(self):
        if self._mode == 'deathless':
            return 'streak'
        if self._mode == 'speed':
            return 'time'
        return None
    
    def getUrl(self, person):
        if self._mode == 'daily':
            return self.url
        return self.url + '?id=' + str(person['steam_id'])
