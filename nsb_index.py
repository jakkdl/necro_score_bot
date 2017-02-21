class index:
    data = {
            741312: ('all',       'score',     False),
            742307: ('all',       'speed',     False),
            74548:  ('all',       'score',     True ),
            745768: ('all',       'speed',     True ),
            745607: ('all',       'deathless', False),
            741115: ('aria',      'score',     False),
            741114: ('aria',      'speed',     False),
            745465: ('aria',      'score',     True ),
            745562: ('aria',      'speed',     True ),
            745472: ('aria',      'deathless', False),
            739795: ('bard',      'score',     False),
            739796: ('bard',      'speed',     False),
            740370: ('bard',      'score',     True ),
            740372: ('bard',      'speed',     True ),
            740959: ('bard',      'deathless', False),
            741400: ('bolt',      'score',     False),
            741112: ('bolt',      'speed',     False),
            745761: ('bolt',      'score',     True ),
            749064: ('bolt',      'speed',     True ),
            745467: ('bolt',      'deathless', False),
            739999: ('cadence',   'score',     False),
            740000: ('cadence',   'speed',     False),
            740363: ('cadence',   'score',     True ),
            742635: ('cadence',   'speed',     True ),
            741677: ('cadence',   'deathless', False),
            741119: ('coda',      'score',     False),
            741120: ('coda',      'speed',     False),
            742305: ('coda',      'score',     True ),
            742295: ('coda',      'speed',     True ),
            742569: ('coda',      'deathless', False),
            741117: ('dorian',    'score',     False),
            741116: ('dorian',    'speed',     False),
            745771: ('dorian',    'score',     True ),
            746203: ('dorian',    'speed',     True ),
            745492: ('dorian',    'deathless', False),
            741328: ('dove',      'score',     False),
            741329: ('dove',      'speed',     False),
            745549: ('dove',      'score',     True ),
            745516: ('dove',      'speed',     True ),
            743127: ('dove',      'deathless', False),
            739792: ('eli',       'score',     False),
            741122: ('eli',       'speed',     False),
            745638: ('eli',       'score',     True ),
            745791: ('eli',       'speed',     True ),
            745486: ('eli',       'deathless', False),
            740390: ('melody',    'score',     False),
            740397: ('melody',    'speed',     False),
            743251: ('melody',    'score',     True ),
            745776: ('melody',    'speed',     True ),
            742624: ('melody',    'deathless', False),
            742526: ('monk',      'score',     False),
            741638: ('monk',      'speed',     False),
            745413: ('monk',      'score',     True ),
            745414: ('monk',      'speed',     True ),
            745487: ('monk',      'deathless', False),
            740154: ('story',     'score',     False),
            742250: ('story',     'speed',     False),
            741210: ('story',     'score',     True ),
            742251: ('story',     'speed',     True )
    }

    @classmethod
    def character(cls, lbid):
        return cls.data[lbid][0]

    @classmethod
    def mode(cls, lbid):
        return cls.data[lbid][1]

    @classmethod
    def seeded(cls, lbid):
        return cls.data[lbid][2]

    @classmethod
    def lbids(cls):
        return cls.data.keys()

    @classmethod
    def boards(cls):
        return cls.data
