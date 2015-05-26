import xml.etree.ElementTree as ET
import os.path

import nsb_steam
import nsb_database

from nsb_config import options


class leaderboard:

    def __init__(self, board):
        self.board = board

        self.data = None
        self.history = None
       
        self.path = os.path.join(options['data'],
                'boards', board._name + '.pickle')


    def hasFile(self):
        return self.path != None and os.path.isfile(self.path)


    def read(self):
        self.history = nsb_database.unpickle(self.path)


    def write(self):
        if self.data == None:
            raise Exception('Trying to pickle with no data read')
        nsb_database.pickle_file(data=self.data, path=self.path)
  

    def fetch(self):
        #url = nsb_steam.boardUrl(self.lbid, 1, 100)
        response = nsb_steam.fetchUrl(self.board._url)
        self.data = self.board.parseResponse(response)
   

    def topEntries(self, num=None):
        if num == None:
            num = self.board.entriesToPrivateReportOnRankDiff()
        num = min(num, len(self.data))
        return self.data[:num]

    def checkForDeleted(self, num):
        deleted = 0
        #num = 150
        #print(len(self.history))
        #print(len(self.data))
        #for hist in self.history[:num]:
        for i in range(min(num, len(self.history))):
            hist = self.history[i]
            found = False
            for person in self.data[:num+20]:
                if person['steam_id'] == int(hist['steam_id']):
                    if int(person['points']) >= int(hist['points']):
                    #print(self.history.index(hist), self.data.index(person))
                        found = True
                    else:
                        print('Found deleted entry due to less points', person)
                    break
            if found == False:
                #deleted.append(i)
                deleted += 1
        return deleted

    def diffingEntries(self, num=None, twitter=None):
        if self.data == None:
            raise Exception('No data')
        if self.history == None:
            raise Exception('No history')

        result = []


        rankMax = max(self.board.entriesToReportOnRankDiff(),
                self.board.entriesToPrivateReportOnRankDiff())

        if num == None:
            num = rankMax

        num = min(num, len(self.data))
        if num == 0:
          return []

        if 'steam_id' in self.data[0]:
            key = 'steam_id'
        else:
            key = 'name'

        for i in range(num):
            found = False
            person = self.data[i]


            for hist in self.history:
                if person[key] == hist[key]:
                    found = True
                    save = False
                    person['histRank'] = hist['rank']
                    person['histPoints'] = hist['points']
                    if self.board.report(person, twitter=twitter):
                        result.append(person)
                    break

            if not found:
                if self.board.report(person, twitter=twitter):
                    result.append(person)

        return result



    def __str__(self):
        return str(self.board)

    def __repr__(self):
        #print(self.orig_name)
        return repr(self.info)

    def formatPoints(self, person):
        strPoints = self.board.formatPoints(person['points'])
        if 'histPoints' in person:
            strPoints += self.board.relativePoints(person['points'], person['histPoints'])
        if self.board.unit() != None:
            strPoints += ' ' + self.board.unit()
        return strPoints

    def includePublic(self, entry):
        rank = int(entry['rank'])
        if rank <= self.board.entriesToReportOnRankDiff():
            #print('rankdiff')
            return True
        if rank <= self.board.entriesToReportOnPointsDiff():
            #print('pointsdiff')
            return True

    def includePrivate(self, entry, twitter):
        rank = int(entry['rank'])
        if ( rank < self.board.entriesToPrivateReportOnRankDiff()
        or rank < self.board.entriesToPrivateReportOnPointsDiff() ):
            if 'twitter_username' in entry and entry['twitter_username'] != None and entry['twitter_username'] != '':
                return True
            twitterHandle = nsb_steam.getTwitterHandle(entry['steam_id'], twitter)
            if twitterHandle != None:
                #print('handle:', twitterHandle)
                entry['twitter_username'] = twitterHandle
                return True
        return False

    def getTwitterHandle(self, person, twitter):
        return self.board.getTwitterHandle(person, twitter)


