#from nsb_config import options
import nsb_steam
import nsb_database

class index:
    def __init__(self, saveToFile = True):
        #if saveToFile:
            #self.path = options['data'] + 'leaderboards.xml'
        #else:
            #self.path = None
        self.data = None
    
    def fetch(self):
        url = nsb_steam.leaderboardUrl()
        response = nsb_steam.fetchUrl(url)
        self.data = nsb_database.xmlToList(response=response, responseType='index')

    def read(self):
        self.data = nsb_database.unpickle(self.path)

    def write(self):
        nsb_database.pickle(data=self.data, path=self.path)

    def entries(self):
        if self.data == None:
            raise Exception('Read or fetch data first')
        return self.data

