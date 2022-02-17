from dataclasses import dataclass


@dataclass
class BoardEntry:
    points: int
    rank: int
    uid: int


class NsbError(Exception):
    pass
