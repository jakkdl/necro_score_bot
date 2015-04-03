import nsb_leaderboard_info
import nsb_steam
import xml.etree.ElementTree as ET
import os.path


def entryIndex(xml):
    for index, value in enumerate(xml):
        if value.tag == 'entries':
            return index
    raise Exception('no index tag in xml')

class entry:
    def __init__(self, xmlEntry):
        self.steamid = int(xmlEntry[0].text)
        self.score = int(xmlEntry[1].text)
        self.rank = int(xmlEntry[2].text)
        self.hasHist = False
        self.prevScore = None
        self.prevRank = None

    def addHist(self, score2, rank2):
        self.hasHist = True
        self.prevScore = score2
        self.prevRank = rank2

class leaderboard:

    def __init__(self, index_entry, active_dir=None, hist_dir=None):
        self.orig_name = index_entry[2].text
        self.lbid = int(index_entry[1].text)
        self.info = nsb_leaderboard_info.leaderboard_info(self.orig_name)
        
        self.path = self.dirToPath(active_dir)
        self.hist_path = self.dirToPath(hist_dir)

        self.xml = None
        self.hist_xml = None
       

    def dirToPath(self, directory):
        if directory == None:
            return None
        if directory[-1] != '/':
            directory += '/'
        return directory + str(self.lbid) + '.xml'


    def hasFile(self):
        return self.path != None and os.path.isfile(self.path)
   

    def hasHistFile(self):
        return self.hist_path != None and os.path.isfile(self.hist_path)


    def download(self):
        if self.path == None:
            raise Exception('Cant download with path==None')
        url = nsb_steam.boardUrl(self.lbid, 1,
                self.info.maxCompareEntries())
        nsb_steam.fetchUrl(url, self.path)


    def read(self):
        if not self.hasFile():
            raise Exception('No file to read')
        self.xml = ET.parse(self.path).getroot()
   

    def read_hist(self):
        if not self.hasHistFile():
            raise Exception('No history file to read')
        self.hist_xml = ET.parse(self.hist_path).getroot()

    def create_hist(self):
        if self.hasHistFile():
            raise Exception('History file already exists')
        self.download()
        self.backup()


    def backup(self):
        os.rename(self.path, self.hist_path)


    def fetch(self):
        url = nsb_steam.boardUrl(self.lbid, 1, 100)
        response = nsb_steam.fetchUrl(url)
        text = nsb_steam.decodeResponse(response)
        self.xml = ET.fromstring(text)


    def commonEntryCode(self, num, history):
        if not history:
            xml = self.xml
        else:
            xml = self.hist_xml

        if not xml:
            raise Exception('xml not read')

        index = entryIndex(xml)
        length = len(xml[index])

        if num == -1:
            count = length
        else:
            count = min(num, length)

        return xml, index,count


    def topEntries(self, num=-1, history=False):
        result = []
        xml, index, count = self.commonEntryCode(num, history)

        for i in range(count):
            result.append(entry(xml[index][i]))
        
        return result


    def findEntry(self, steamid, max_rank=-1, history=False):
        xml, index, count = self.commonEntryCode(max_rank, history)

        for i in range(count):
            p = entry(xml[index][i])
            if p.steamid == steamid:
                return p
        return None




    def diffingEntries(self, num=None):
        result = []

        if num == None:
            num = self.info.maxLeaderboardEntries()

        for i in self.topEntries(num, False):
            res = self.findEntry(self, i.steamid,
                    self.info.maxCompareEntries())
            if res == None:
                result.append(i)
            elif res.score != i.score:
                i.addHist(score=res.score, rank=res.rank)
                result.append(i)

        return result


    def daily(self):
        return self.info.daily()

    def date(self):
        return self.info.date

    def toofzSupport(self):
        return self.info.toofzSupport()

    def toofzUrl(self):
        return self.info.toofzUrl()

    def mode(self):
        return self.info.mode

    def __str__(self):
        return str(self.info)

    def include(self):
        return self.info.include()
