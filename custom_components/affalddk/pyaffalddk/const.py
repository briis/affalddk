"""Constants for the pyaffalddk integration."""
from pathlib import Path
#import importlib.resources as pkg_resources  # Python 3.7+
import json

GH_API = b'NDc5RDQwRjQtQjNFMS00MDM4LTkxMzAtNzY0NTMxODhDNzRD'


#with pkg_resources.files('pyaffalddk').joinpath('supported_items.json').open('r', encoding='utf-8') as f:
with (Path(__file__).parent / 'supported_items.json').open('r', encoding='utf-8') as f:
    SUPPORTED_ITEMS = json.load(f)


NON_SUPPORTED_ITEMS = [
    'Asbest',
    'Beholderservice',
    'Beholderudbringning',
    'Bestil afhentning',
    'Bestillerordning',
    'Farligt affald (skal bestilles)',
    'Farligt affald - tilmeld',
    'Haveaffald (skal bestilles)',
    'Henteordning for grene',
    'Ingen tømningsdato fundet!',
    'Pap bundtet',
    'Skal tilmeldes',
    'Storskrald (skal bestilles)',
    'Trærødder og stammer',
    'Udbringning',
]


SPECIAL_MATERIALS = {
    '240 l genbrug 2-kammer': ['pappapirglasmetal'],
    'haveaffald': ['haveaffald'],
    '4-kammer (370 l)': ['papirglasmetalplast'],
    '4-kammer (240 l)': ['pappapirglasmetal'],
    '240L genbrug': ['pappi'],
    'genbrug - blåt låg': ['plastmadkarton'],
    'Genbrug henteordning': ['plastmadkarton'],
    'Miljøkasse/tekstiler': ['farligtaffald', 'tekstil'],
}


ICON_LIST = {
    "batterier": "mdi:battery",
    "dagrenovation": "mdi:trash-can",
    "elektronik": "mdi:power-plug",
    "farligtaffald": "mdi:recycle",
    "farligtaffaldmiljoboks": "mdi:recycle",
    "flis": "mdi:tree",
    "genbrug": "mdi:recycle",
    "glas": "mdi:bottle-soda",
    "glasplast": "mdi:trash-can",
    "haveaffald": "mdi:leaf",
    "jern": "mdi:bucket",
    "juletrae": "mdi:pine-tree",
    "madaffald": "mdi:trash-can",
    "metal": "mdi:anvil",
    "metalglas": "mdi:glass-fragile",
    "pap": "mdi:note",
    "pappapir": "mdi:file",
    "pappapirglasmetal": "mdi:trash-can",
    "pappapirtekstil": "mdi:recycle",
    "pappi": "mdi:trash-can",
    "papir": "mdi:file",
    "papirglas": "mdi:greenhouse",
    "papirglasdaaser": "mdi:trash-can",
    "papirglasmetalplast": "mdi:trash-can",
    "papirmetal": "mdi:delete-empty",
    "plast": "mdi:trash-can",
    "plastmadkarton": "mdi:trash-can",
    "plastmdkglasmetal": "mdi:trash-can",
    "plastmetal": "mdi:trash-can-outline",
    "plastmetalmdk": "mdi:trash-can",
    "plastmetalpapir": "mdi:trash-can",
    "restaffald": "mdi:trash-can",
    "restaffaldmadaffald": "mdi:trash-can",
    "restplast": "mdi:trash-can",
    "storskrald": "mdi:table-furniture",
    "storskraldogtekstilaffald": "mdi:table-furniture",
    "storskraldogfarligtaffald": "mdi:table-furniture",
    "tekstil": "mdi:recycle",
}

NAME_LIST = {
    "batterier": "Batterier",
    "bioposer": "Bioposer",
    "dagrenovation": "Dagrenovation",
    "elektronik": "Elektronik",
    "farligtaffald": "Farligt affald",
    "farligtaffaldmiljoboks": "Farligt affald & Miljøboks",
    "flis": "Flis",
    "genbrug": "Genbrug",
    "glas": "Glas",
    "glasplast": "Glas, Plast & Madkartoner",
    "haveaffald": "Haveaffald",
    "jern": "Jern",
    "juletrae": "Juletræer",
    "madaffald": "Madaffald",
    "metal": "Metal",
    "metalglas": "Metal & Glas",
    "pap": "Pap",
    "pappapir": "Pap & Papir",
    "pappapirglasmetal": "Pap, Papir, Glas & Metal",
    "pappapirtekstil": "Pap, Papir & Tekstilaffald",
    "pappi": "Papir & Plast",
    "papir": "Papir",
    "papirglas": "Papir, Pap & Glas",
    "papirglasdaaser": "Papir, Glas & Dåser",
    "papirglasmetalplast": "Papir, Glas, Metal & Plast",
    "papirmetal": "Papir & Metal",
    "plast": "Plast",
    "plastmadkarton": "Plast & Madkarton",
    "plastmdkglasmetal": "Plast, Madkarton, Glas & Metal",
    "plastmetal": "Plast & Metal",
    "plastmetalmdk": "Plast, Metal, Mad & Drikkekartoner",
    "plastmetalpapir": "Plast, Metal & Papir",
    "restaffald": "Restaffald",
    "restaffaldmadaffald": "Rest & Madaffald",
    "restplast": "Restaffald & Plast/Madkartoner",
    "storskrald": "Storskrald",
    "storskraldogfarligtaffald": "Storskrald & Farligt affald",
    "storskraldogtekstilaffald": "Storskrald & Tekstilaffald",
    "tekstil": "Tekstilaffald",
}

NAME_LIST_REV = {val: key for key, val in NAME_LIST.items()}
NAME_ARRAY = list(NAME_LIST.keys())


STRIPS = [
        'med 14-dages tømning ved helårshuse', '– tømmes hver 2. uge', 'tømning af',
        'sommerhustømning', 'henteordning', 'beholder til', '1-rums',
        'egenløsning', 'en-familie', 'enfamiliehus', '26 tøm', 'm. sommertømning',
        '-skel 0-2 meter', 'afstand over 5 meter', 'Jern/Elektronik/Hårde hvidevarer', ' ?', '**',
]
RE_WORDS = [
    r'14(\.)?[\s-]?(?:dags|dage|dages|dg)(\.)?',  # diffenrent ways of 14. dags
    r'\b\d+/\d+\.\s*uge\b', # fixing https://github.com/briis/affalddk/issues/373 looking for "2/4. uge" and "8/12. uge"
    r'(?:2|3|4|6|8)?(\.)?[\s-]?(?:uge k|uge p|uge|ugers)',  # diffenrent ways of uge
    r'(?:to|1|2)[\s-]?(?:delt|kammer)',  # diffenrent ways of  2-delt or 2-kammer
    r'beh\.(,)?', r'\bgl\.', 'beholder', 'dobbeltbeholder', 'spand', 'tøm', 'villa', 'tømning', 'ekstra', 'havebolig', '5 m3',
    'stand', 'skel', 'skelordning', 'hver', 'nord', 'syd', 'øst', 'vest', r'sommer( \d{2})?', 'vinter',
    r'distrikt (?:[A-Za-z]|\d+)', 'rute [0-9]', 's[0-9]', 'd[0-9]', r'/\d{2}',
    ]

RE_RAW = [
    r'\b\d{4}\b\s*,',  # 4 digit postal codes with a comma after
    r'\b\d{4}\b\ og \b\d{4}\b',  # special ending of postal code listing
    r'(?<![\w/-])(?:25|90|140|190|240|360|370|400|660|770)\s*l(?:tr|iter)?\.?(?=\b|[^a-zA-Z]|$)',  # remove volume parts
    r'(?<![\w/-])(?:25|90|140|190|240|360|370|400|660|770)l(?:tr|iter)?\.?(?=\b|[^a-zA-Z]|$)',  # remove volume parts (no space before L)
    r'^(?:90|140|190|240|370|400)\s',  # only remove "[vol] " if it is the start of the string like in Assens
    ]

ODD_EVEN_ARRAY = ["lige", "ulige"]
WEEKDAYS = ["Mandag", "Tirsdag", "Onsdag",
            "Torsdag", "Fredag", "Lørdag", "Søndag"]
WEEKDAYS_SHORT = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
