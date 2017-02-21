import nsb_entry

import os.path

import nsb_steam
import nsb_database

from nsb_config import options


class board:

    def __init__(self, name, url):
        self._name = name
        self._url = url

        self._data = None
        self._history = None
        #self._path = None
        self.path = os.path.join(options['data'],
                'boards', _filename() + '.pickle')

    def _get_common(self, num, data):
        if data == None:
            raise Exception('Data unavailable')
        num = min(num, len(data))
        return nsb_entry.generate_entries(data[:num])


    def get_top(self, num=10):
        return self._get_common(num, self._data)
    
    def get_top_history(self, num=10):
        return self._get_common(num, self._history)


    def get_improvements(self, num=None, twitter=None):
        if self._data == None:
            raise Exception('No data')
        if self._history == None:
            raise Exception('No history')

        result = []


        #rankMax = max(self.board.entriesToReportOnRankDiff(),
        #        self.board.entriesToPrivateReportOnRankDiff())

        if num == None:
            num = 500

        num = min(num, len(self.data))
        if num == 0:
            return []

        key = self._key()



        #if 'steam_id' in self.data[0]:
        #    key = 'steam_id'
        #else:
        #    key = 'name'

        curr_index = 0
        hist_index = 0

        unmatched_new = {}
        unmatched_hist = {}
        improved = []

        while index < num:
            curr_person = self._data[curr_index]
            hist_person = self._history[hist_index]
            curr_id = curr_person[key]


            if curr_id in unmatched_hist:
                if self._improved(curr_person,
                        unmatched_hist[curr_id]):
                    improved.append((curr_person,
                        unmatched_hist[curr_id]))




            for i in range(len(unmatched_hist)):
                if unmatched_hist[i][key] == curr_id:
                    if self._improved(curr_person,
                            unmatched_hist[i]):
                        improved.append(curr_person,
                                unmatched_hist[i])
                    unmatched_hist.pop(i)
                    break
            else:
                unmatched_new.append(curr_person)




            


        for i in range(num):
            found = False
            person = self.data[i]


            for hist in self.history:
                if person[key] == hist[key]:
                    found = True
                    #save = False
                    if self.board.report(person, hist, twitter=twitter):
                        person['histRank'] = hist['rank']
                        person['histPoints'] = hist['points']
                        result.append(person)
                    break

            if not found:
                if self.board.report(person, twitter=twitter, hist=None):
                    result.append(person)

        return result
       


    def hasFile(self):
        #print(self.path)
        return self.path != None and os.path.isfile(self.path)


    def read(self):
        self.history = nsb_database.unpickle(self.path)


    def write(self):
        if self.data == None:
            raise Exception('Trying to pickle with no data read')
        nsb_database.pickle_file(data=self.data, path=self.path)
  

    def fetch(self):
        url = nsb_steam.boardUrl(self.board._lbid, 1, 100)
        response = nsb_steam.fetchUrl(url)
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
        #print(self.data)
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
                #print(i, hist)
                deleted += 1
        return deleted
    
    

    def realRank(self, rank):
        subtract = 0
        if 'SRL' in str(self.board):
            return rank
        for i in self.data[:rank-1]:
            if self.impossiblePoints(i) or nsb_steam.known_cheater(i['steam_id']):
                #print(i)
                subtract += 1
        return rank - subtract



    def __str__(self):
        return str(self.board)

    def __repr__(self):
        #print(self.orig_name)
        return repr(self.info)

    def formatPoints(self, person):
        #TODO: Not public, write to the entry.
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
        return False

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

    def impossiblePoints(self, person):
        return self.board.impossiblePoints(person)

    def getUrl(self, person=None):
        return self.board.getUrl(person)
