from typing import Callable, cast, Optional
import nsb_leaderboard
import nsb_entry

format_dict: dict[str, Callable[[nsb_entry.Entry], str]] = {
    # "$NAME$": str,
    "$RANK$": lambda e: str(e.score.rank),
    "$RANKTH$": lambda e: _nth(e.score.rank),
    "$BOARD$": lambda e: str(e.board),
    "$TIME$": lambda e: _format_time(_score_to_ms(e.score.points)),
    # maybe not the cleanest way to handle the optional BoardEntry, should maybe
    # be a function with assert
    "$DELTATIME$": lambda e: _format_time(
        _score_to_ms(
            cast(nsb_leaderboard.BoardEntry, e.prev_score).points - e.score.points
        )
    ),
    "$PROGRESS$": lambda e: _format_progress(e.score.points),
    "$DELTAPROGRESS$": lambda e: _relative_progress(
        e.score.points, cast(nsb_leaderboard.BoardEntry, e.prev_score).points
    ),
    "$SCORE$": lambda e: str(e.score.points),
    "$DELTASCORE$": lambda e: str(
        cast(nsb_leaderboard.BoardEntry, e.prev_score).points - e.score.points
    ),
    "$TOOFZURL": lambda e: e.pretty_url(),
}


def format_message(entry: nsb_entry.Entry, name: Optional[str] = None) -> str:
    template = entry.template

    if not name:
        name = str(entry)
    template = template.replace("$NAME$", name)

    for key, func in format_dict.items():
        if key not in template:
            continue
        template = template.replace(key, func(entry))
    return template


def _nth(i: int) -> str:
    if i % 100 in (11, 12, 13):
        return "th"
    if i % 10 == 1:
        return "st"
    if i % 10 == 2:
        return "nd"
    if i % 10 == 3:
        return "rd"
    return "th"


def _score_to_progress(score: int) -> tuple[int, int, int]:
    wins = score // 100
    zone = (score // 10) % 10 + 1
    level = score % 10 + 1
    return wins, zone, level


# TODO move to template
def _format_progress(score: int) -> str:
    wins, zone, level = _score_to_progress(score)
    return f"{wins} win{'s' if wins != 1 else ''}, dying on {zone}-{level}"


def _relative_progress(new_score: int, prev_score: int) -> str:
    if prev_score in (-1, new_score):
        return ""
    wins, zone, level = _score_to_progress(prev_score)
    return f" (up from {wins}-{zone}-{level})"


def _score_to_ms(score: int) -> int:
    return 100000000 - score


def _format_time(milliseconds: int) -> str:
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
