format_dict = {
    "$NAME$": str,
    "$RANK$": lambda e: str(e.score["rank"]),
    "$RANKTH$": lambda e: _nth(e.score["rank"]),
    "$BOARD$": lambda e: e.board.display_name,
    "$TIME$": lambda e: _format_time(_score_to_ms(e.score["points"])),
    "$DELTATIME$": lambda e: _format_time(
        _score_to_ms(e.prev_score["points"] - e.score["points"])
    ),
    "$PROGRESS$": lambda e: _format_progress(e.score["points"]),
    "$DELTAPROGRESS$": lambda e: _relative_progress(
        e.score["points"], e.prev_score["points"]
    ),
    "$SCORE$": lambda e: str(e.score["points"]),
    "$DELTASCORE$": lambda e: str(e.prev_score["points"] - e.score["points"]),
}


def format_message(entry):
    template = entry.template
    for key, func in format_dict.items():
        if key not in template:
            continue
        template = template.replace(key, func(entry))
    return template


def _nth(i):
    if i % 100 in (11, 12, 13):
        return "th"
    if i % 10 == 1:
        return "st"
    if i % 10 == 2:
        return "nd"
    if i % 10 == 3:
        return "rd"
    return "th"


def _score_to_progress(score):
    wins = score // 100
    zone = (score // 10) % 10 + 1
    level = score % 10 + 1
    return wins, zone, level


def _format_progress(score):
    wins, zone, level = _score_to_progress(score)
    return f"{wins} win{'s' if wins != 1 else ''}, dying on {zone}-{level}"


def _relative_progress(new_score, prev_score):
    if prev_score in (-1, new_score):
        return ""
    wins, zone, level = _score_to_progress(prev_score)
    return f" (up from {wins}-{zone}-{level})"


def _score_to_ms(score):
    return 100000000 - score


def _format_time(milliseconds):
    """Takes in a time (in milliseconds) and returns a formatted string.
    examples:
        1000    -> '01.00'
        100293  -> '01:40.29'
        100298  -> '01:40.30'
        4100298 -> '1:08:20.30'
    """
    result = ""

    if milliseconds < 0:
        milliseconds *= -1
        result = "-"

    hours, milliseconds = divmod(milliseconds, 60 * 60 * 1000)
    minutes, milliseconds = divmod(milliseconds, 60 * 1000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    milliseconds = round(milliseconds / 10.0)  # Change precision from 3 to 2

    if hours:
        result += f"{hours}:{minutes:02}:"
    elif minutes:
        result += f"{minutes}:"

    result += f"{seconds:02}.{milliseconds:02}"

    return result
