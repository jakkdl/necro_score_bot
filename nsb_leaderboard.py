import datetime
##character
#All-Char, Aria, Bard, Bolt, Cadence, Coda, Dorian, Dove, Eli,  Melody, Monk, None

##Mode
#Speed, Score,  Deathless, Daily, None

##seeded
#True, False

##coop
#True, False

#customMusic
#True, False

class leaderboard:
    def checkCadence(self, name):
        name = name.replace('hardcore', '')
        name = name.replace('seeded', '')
        name = name.replace('deathless', '')
        name = name.replace('speedrun', '')
        name = name.replace('co-op', '')
        name = name.replace('custom', '')
        name = name.replace(' ', '')
        return name == ''
    
    def checkSeeded(self, name):
        return 'seeded' in name

    def checkCoop(self, name):
        return 'co-op' in name

    def checkCustomMusic(self, name):
        return 'custom' in name

    def extractCharacter(self, name):
        names = ['all char', 'aria', 'bard', 'bolt', 'coda',
                'dorian', 'dove', 'eli', 'melody', 'monk']
        for i in names:
            if i in name:
                return i
        if self.checkCadence(name):
            return 'cadence'
        return None

    def extractMode(self, name):
        if '/' in name:
            return 'daily'
        if 'speedrun' in name and 'deathless' in name:
            return None
        if 'all zones' in name:
            return None
        if 'deathless' in name:
            return 'deathless'
        if 'speedrun' in name:
            return 'speed'
        if 'hardcore' in name:
            return 'score'
        return None
    
    def daily(self):
        return self.mode == 'daily'

    def extractDate(self, name):
        if not self.daily():
            return None
        sp = name.split()[0]
        sp = sp.split('/')
        return datetime.date(int(sp[2]), int(sp[1]), int(sp[0]))


    def __init__(self, name):
        name = name.lower()
        self.character = self.extractCharacter(name)
        self.mode = self.extractMode(name)
        self.date = self.extractDate(name)
        self.seeded = self.checkSeeded(name)
        self.coop = self.checkCoop(name)
        self.customMusic = self.checkCustomMusic(name)

    def __str__(self):
        ##TODO: Make up a pretty solution for all boards and write/implement
        if self.character == None or self.mode == None:
            return 'None'
        return (self.character + ' ' + self.mode).title()

    def debugString(self):
        name = ''
        name += 'character: ' + self.character + '\n'
        name += 'mode: ' + self.mode + '\n'
        name += 'seeded: ' + str(self.seeded) + '\n'
        name += 'coop: ' + str(self.coop) + '\n'
        name += 'customMusic: ' + str(self.customMusic)
        return name


    def max(self):
        if self.customMusic:
            return 1
        if self.coop:
            return 3
        if self.seeded:
            return 1
        if self.mode == 'deathless':
            return 5
        if self.mode == 'score':
            return 10
        if self.mode == 'speed':
            return 10
        if self.mode == 'daily':
            return 3
        return None

    def include(self):
        if self.customMusic:
            return False
        if self.coop:
            return False
        if self.seeded:
            return False
        if self.mode == 'daily':
            return False
        if self.character == 'coda':
            return False
        if self.character == None:
            return False
        if self.mode != None:
            return True
        return False

    def toofzChar(self, char):
        char = char.replace('all-char', 'all')
        return char

    def toofzMode(self, mode):
        mode = mode.replace('score', 'hardcore')
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
        char = self.toofzChar(self.character)
        mode = self.toofzMode(self.mode)
        return 'http://crypt.toofz.com/Leaderboards/%s/%s'%(char, mode)
