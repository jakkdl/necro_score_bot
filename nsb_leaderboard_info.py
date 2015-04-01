import datetime
##character
#All-Char, story mode, Aria, Bard, Bolt, Cadence, Coda, Dorian, Dove, Eli,  Melody, Monk, None

##Mode
#Speed, Score,  Deathless, Daily, None

##seeded
#True, False

##coop
#True, False

#customMusic
#True, False

def extractCharacter(name):
    names = ['all char', 'story mode', 'aria', 'bard', 'bolt',
            'coda', 'dorian', 'dove', 'eli', 'melody', 'monk']
    for i in names:
        if i in name:
            return i
    if checkCadence(name):
        return 'cadence'
    return None


def checkCadence(name):
    delete = ['hardcore', 'seeded', 'deathless',
            'speedrun', 'co-op', 'custom', ' ']
    for i in delete:
        name = name.replace(i, '')
    return name == ''


def checkSeeded(name):
    return 'seeded' in name


def checkCoop(name):
    return 'co-op' in name


def checkCustomMusic(name):
    return 'custom' in name


def extractMode(name):
    if '/' in name:
        return 'daily'
    if 'speedrun' in name and 'deathless' in name:
        return None
    if 'deathless' in name:
        return 'deathless'
    if 'speedrun' in name:
        return 'speed'
    if 'hardcore' in name:
        return 'score'
    return None


class leaderboard_info:

    def __init__(self, name):
        name = name.lower()
        self.character = extractCharacter(name)
        self.mode = extractMode(name)
        self.date = self.extractDate(name)
        self.seeded = checkSeeded(name)
        self.coop = checkCoop(name)
        self.customMusic = checkCustomMusic(name)

    
    def __str__(self):
        ##TODO: Make up a pretty solution for all boards and write/implement
        if self.daily():
            return str(self.date)
        if self.character == None or self.mode == None:
            return 'None'
        result = self.character
        if self.customMusic:
            result += ' custom music'
        if self.coop:
            result += ' co-op'
        if self.seeded:
            result += ' seeded'
        result += ' ' + self.mode
        return result.title()

    def __repr__(self):
        name = ''
        name += 'character: ' + str(self.character) + '\n'
        name += 'mode: ' + str(self.mode) + '\n'
        name += 'seeded: ' + str(self.seeded) + '\n'
        name += 'coop: ' + str(self.coop) + '\n'
        name += 'customMusic: ' + str(self.customMusic)
        return name


    def daily(self):
        return self.mode == 'daily'

    
    def extractDate(self, name):
        if not self.daily():
            return None
        sp = name.split()[0]
        sp = sp.split('/')
        return datetime.date(int(sp[2]), int(sp[1]), int(sp[0]))


    def maxLeaderboardEntries(self):
        #if self.customMusic:
            #return 1
        if self.coop:
            return 3
        if self.seeded:
            return 3
        if self.character == 'story mode':
            return 5
        if self.mode == 'deathless':
            return 5
        if self.mode == 'score':
            return 10
        if self.mode == 'speed':
            return 10
        if self.mode == 'daily':
            return 3
        return None
    
    def maxCompareEntries(self):
        return 100
    
    def include(self):
        if self.customMusic:
            return False
        if self.coop and self.seeded:
            return False
        if self.seeded and self.mode == 'deathless':
            return False
        if self.character == 'coda':
            return False
        if self.mode == 'daily':
            return False
        if self.character == None:
            return False
        if self.coop:
            return False
        if self.mode != None:
            return True
        return False

    
    def toofzChar(self, char):
        if char == 'all-char':
            return 'all'
        if char == 'story mode':
            return 'story'
        return char

    
    def toofzMode(self, mode):
        #mode = mode.replace('score', 'hardcore')
        return mode

    
    def toofzSupport(self):
        if self.coop or self.seeded or self.customMusic:
            return False
        if self.mode == 'daily' or self.mode == None:
            return False
        if self.character == 'coda':
            return False
        return True

    
    def toofzUrl(self):
        if self.daily():
            return str(self.date)
        char = self.toofzChar(self.character)
        mode = self.toofzMode(self.mode)
        return 'http://crypt.toofz.com/Leaderboards/%s/%s'%(char, mode)
