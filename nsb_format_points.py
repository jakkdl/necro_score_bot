def scoreToProgress(score):
    wins = score // 100
    zone = ( score // 10 ) % 10 + 1
    level = score % 10 + 1
    return wins, zone, level

def formatProgress(score):
    wins, zone, level = scoreToProgress(score)
    if wins == 1:
        strWin = 'win'
    else:
        strWin = 'wins'
    return '%d %s, dying on %d-%d'%(wins, strWin, zone, level)

def relativeProgress(newScore, prevScore):
    if prevScore == -1 or newScore == prevScore:
        return ''
    else:
        wins, zone, level = scoreToProgress(prevScore)
        return ' (up from %d-%d-%d)'%(wins, zone, level)

def scoreAsMilliseconds(score):
    return 100000000 - score

def formatTime(milliseconds):
    """ Takes in a time (in milliseconds) and returns a formatted string.
        examples:
            1000    -> '01.00'
            100293  -> '01:40.29'
            100298  -> '01:40.30'
            4100298 -> '1:08:20.30'
    """
    hours, milliseconds = divmod(milliseconds, 60*60*1000)
    minutes, milliseconds = divmod(milliseconds, 60*1000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    milliseconds = round(milliseconds / 10.0) # Change precision from 3 to 2

    result = ''

    minutePad='%d:'
    if hours:
        result += '%d:'%(hours)
        minutePad='%02d:'
    if minutes or hours:
        result += minutePad%(minutes)

    result += '%02d.%02d'%(seconds, milliseconds)

    return result

def relativeTime(newTime, prevTime):
    """ newTime and prevTime should be given in milliseconds
    """
    if prevTime == -1 or newTime == prevTime:
        return ''
    else:
        return ' (-%s)'%(formatTime(prevTime - newTime))

def relativeRank(newRank, prevRank):
    if prevRank == -1 or newRank == prevRank:
        return ''
    else:
        return ' (%+d)'%(prevRank - newRank)

def relativeScore(newScore, prevScore):
    if prevScore == -1 or newScore == prevScore:
        return ''
    else:
        return ' (+%d)'%(newScore - prevScore)

