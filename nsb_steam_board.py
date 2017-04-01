import datetime

import nsb_database
import nsb_format_points
import nsb_steam
##character
#All-Char, story mode, Aria, Bard, Bolt, Cadence, Coda, Dorian, Dove, Eli,  Melody, Monk, None

##Mode
#Speed, Score,  Deathless, Daily, None

##dlc
#True, False

##seeded
#True, False

##coop
#True, False

##customMusic
#True, False

##extras
extras = ['no return', 'hard mode']

def extractCharacter(name):
    names = ['all char', 'story mode', 'aria', 'bard', 'bolt',
            'coda', 'dorian', 'dove', 'eli', 'melody', 'monk',
            'nocturna', 'diamond']
    for i in names:
        if i in name:
            return i
    if checkCadence(name):
        return 'cadence'
    print('unknown character in board {}'.format(name))
    return None


def checkCadence(name):
    delete = ['hardcore', 'seeded', 'deathless',
            'speedrun', 'co-op', 'custom', '_prod', '_dev', 'dlc']
    delete += extras
    for i in delete:
        name = name.replace(i, '')
    name = name.replace(' ', '')
    return name == ''


def checkSeeded(name):
    return 'seeded' in name


def checkDLC(name):
    return 'dlc' in name


def checkCoop(name):
    return 'co-op' in name


def checkCustomMusic(name):
    return 'custom' in name

def checkExtraModes(name):
    extraModes = []
    for mode in extras:
        if mode in name:
            extraModes.append(mode)
    return extraModes

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
    print('unknown mode in board {}'.format(name))
    return None


def extractAvailability(name):
    if '_dev' in name:
        return 'dev'
    if '_prod'in name:
        return 'prod'
    return 'normal'

class steam_board:

    def __init__(self, index_entry):
        name = index_entry['name'].lower()

        self._availability = extractAvailability(name)
        self._character = extractCharacter(name)
        self._mode = extractMode(name)
        self._date = self.extractDate(name)
        self._seeded = checkSeeded(name)
        self._coop = checkCoop(name)
        self._customMusic = checkCustomMusic(name)
        self._dlc = checkDLC(name)
        self._extra = checkExtraModes(name)

        self.name = self.nice_name()
        self._name = name
        self._url = index_entry['url']

        if self.toofzSupport():
            self.url = self.toofzUrl()
        else:
            self.url = None


    def nice_name(self):
        ##TODO: Make up a pretty solution for all boards and write/implement
        if self.daily():
            return str(self._date)
        if self._character == None or self._mode == None:
            return 'None'
        result = self._character
        
        if self._extra:
            result += ' ' + ' '.join(self._extra)
        if self._customMusic:
            result += ' custom music'
        if self._coop:
            result += ' co-op'
        if self._seeded:
            result += ' seeded'
        result += ' ' + self._mode
        if self._dlc:
            result += ' Amplified'
        return result.title()

    def __str__(self):
        return self.name

    def __repr__(self):
        name = ''
        name += 'DLC: ' + str(self._dlc) + '\n'
        name += 'character: ' + str(self._character) + '\n'
        name += 'mode: ' + str(self._mode) + '\n'
        name += 'seeded: ' + str(self._seeded) + '\n'
        name += 'coop: ' + str(self._coop) + '\n'
        name += 'customMusic: ' + str(self._customMusic)
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



    def toofzChar(self, char):
        if char == 'all char':
            return 'all'
        if char == 'story mode':
            return 'story'
        return char
    



    def toofzSupport(self):
        if self._coop or self._customMusic:
            return False
        if self._mode == None:
            return False
        if len(self._extra) > 1:
            print('toofz doesnt support >1 extra modes')
            return False
        return True


    def toofzUrl(self):
        base = 'http://crypt.toofz.com/leaderboards/'
        if self._dlc:
            base += 'amplified/'

        if self.daily():
            return base + 'Daily/' + self._date.strftime('%Y/%m/%d/')

        char = self.toofzChar(self._character)
        mode = self._mode
        if self._seeded:
            mode = 'seeded-' + mode
        if self._extra:
            mode += '/' + self._extra[0].replace(' ', '-')
        return base + '%s/%s'%(char, mode)

    def parseResponse(self, response):
        return nsb_database.xmlToList(response, 'leaderboard')


    def getTwitterHandle(self, person, twitter):
        return nsb_steam.getTwitterHandle(int(person['steam_id']), twitter)



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
        if not self.url:
            return ''
        return self.url + '?id=' + str(person['steam_id'])
