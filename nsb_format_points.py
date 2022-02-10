def nth(i):
    if i % 10 == 1 and i % 100 != 11:
        return 'st'
    if i % 10 == 2 and i % 100 != 12:
        return 'nd'
    if i % 10 == 3 and i % 100 != 13:
        return 'rd'
    return 'th'


def scoreToProgress(score):
    wins = score // 100
    zone = (score // 10) % 10 + 1
    level = score % 10 + 1
    return wins, zone, level


def formatProgress(score):
    wins, zone, level = scoreToProgress(score)
    return f"{wins} win{'s' if wins != 1 else ''}, dying on {zone}-{level}"


def scoreAsMilliseconds(score):
    return 100000000 - score


def formatTime(milliseconds):
    """Takes in a time (in milliseconds) and returns a formatted string.
    examples:
        1000    -> '01.00'
        100293  -> '01:40.29'
        100298  -> '01:40.30'
        4100298 -> '1:08:20.30'
    """
    hours, milliseconds = divmod(milliseconds, 60 * 60 * 1000)
    minutes, milliseconds = divmod(milliseconds, 60 * 1000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    milliseconds = round(milliseconds / 10.0)  # Change precision from 3 to 2

    result = ''

    if hours:
        result += f'{hours}:{minutes:02}:'
    elif minutes:
        result += f'{minutes}:'

    result += f'{seconds:02}.{milliseconds:02}'

    return result


def relativeProgress(newScore, prevScore):
    if prevScore in (-1, newScore):
        return ''
    wins, zone, level = scoreToProgress(prevScore)
    return f' (up from {wins}-{zone}-{level})'


def relativeTime(new, prev):
    """newTime and prevTime should be given in milliseconds"""
    if prev in (-1, new):
        return ''
    return f' (-{formatTime(prev - new)}) '


def relativeRank(new, prev):
    if prev in (-1, new):
        return ''
    return f' ({prev-new:+}) '


def relativeScore(new, prev):
    if prev in (-1, new):
        return ''
    return f' (+{prev-new}) '
