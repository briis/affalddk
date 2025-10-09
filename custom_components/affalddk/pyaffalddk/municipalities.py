data = '''0101: København
0147: Frederiksberg
0151: Ballerup
0153: Brøndby
0155: Dragør
0157: Gentofte
0159: Gladsaxe
0161: Glostrup
0163: Herlev
0165: Albertslund
0167: Hvidovre
0169: Høje-Taastrup
0173: Lyngby-Taarbæk
0175: Rødovre
0183: Ishøj
0185: Tårnby
0187: Vallensbæk
0190: Furesø
0201: Allerød
0210: Fredensborg
0217: Helsingør
0219: Hillerød
0223: Hørsholm
0230: Rudersdal
0240: Egedal
0250: Frederikssund
0253: Greve
0259: Køge
0260: Halsnæs
0265: Roskilde
0269: Solrød
0270: Gribskov
0306: Odsherred
0316: Holbæk
0320: Faxe
0326: Kalundborg
0329: Ringsted
0330: Slagelse
0336: Stevns
0340: Sorø
0350: Lejre
0360: Lolland
0370: Næstved
0376: Guldborgsund
0390: Vordingborg
0400: Bornholm
0410: Middelfart
0411: Christiansø
0420: Assens
0430: Faaborg-Midtfyn
0440: Kerteminde
0450: Nyborg
0461: Odense
0479: Svendborg
0480: Nordfyns
0482: Langeland
0492: Ærø
0510: Haderslev
0530: Billund
0540: Sønderborg
0550: Tønder
0561: Esbjerg
0563: Fanø
0573: Varde
0575: Vejen
0580: Aabenraa
0607: Fredericia
0615: Horsens
0621: Kolding
0630: Vejle
0657: Herning
0661: Holstebro
0665: Lemvig
0671: Struer
0706: Syddjurs
0707: Norddjurs
0710: Favrskov
0727: Odder
0730: Randers
0740: Silkeborg
0741: Samsø
0746: Skanderborg
0751: Aarhus
0756: Ikast-Brande
0760: Ringkøbing-Skjern
0766: Hedensted
0773: Morsø
0779: Skive
0787: Thisted
0791: Viborg
0810: Brønderslev
0813: Frederikshavn
0820: Vesthimmerlands
0825: Læsø
0840: Rebild
0846: Mariagerfjord
0849: Jammerbugt
0851: Aalborg
0860: Hjørring'''


MUNICIPALITIES_IDS = {line.split(':')[1].strip().lower(): int(line.split(':')[0]) for line in data.splitlines()}


MUNICIPALITIES_LIST = {
    "Aabenraa": ["renoweb"],
    "Aalborg": ["renoweb"],
    "Aarhus": ["aarhus"],
    "Albertslund": ["vestfor"],
    "Allerød": ["renoweb"],
    "Assens": ["affaldonline", "YWZkOTEyYTItNDRiMy00MDJmLTllMTMtNWFlYjcwMWNlMTQz"],
    "Ballerup": ["vestfor"],
    "Billund": ["renoweb"],
    "Bornholm": ["renoweb"],
    "Brøndby": ["renoweb"],
    "Brønderslev": ["renoweb"],
    "Dragør": ["renoweb"],
    "Egedal": ["renoweb"],
    "Esbjerg": ["renoweb"],
    "Favrskov": ["affaldonline", "ZGZmY2M1YjYtYjllZS00NzhkLTgyZTItMDMwMTIzNDg1Zjdl"],
    "Faxe": ["perfectwaste"],
    "Fredensborg": ["renoweb"],
    "Fredericia": ["openexplive", "3YWh0MjlpbDh1djNiM25hZA=="],
    "Frederikssund": ["perfectwaste"],
    "Frederiksberg": ["openexplive", '6RjFCNUdtUGNxRU1xMGxFWA=='],
    "Furesø": ["vestfor"],
    "Gentofte": ["renoweb"],
    "Gladsaxe": ["perfectwaste"],
    "Glostrup": ["renoweb"],
    "Greve": ["perfectwaste"],
    "Gribskov": ["perfectwaste"],
    "Guldborgsund": ["perfectwaste"],
    "Haderslev": ['provas'],
    "Halsnæs": ["perfectwaste"],
    "Helsingør": ["perfectwaste"],
    "Herlev": ["renoweb"],
    "Herning": ["herning"],
    "Hillerød": ["perfectwaste"],
    "Hjørring": ["renoweb"],
    "Holbæk": ["affaldonline", "MDE3ZWZkMDYtYWM0Mi00YjM2LThhNzAtYWIzMDkxNjJlOTg4"],
    "Holstebro": ["openexp", "renomatic.nomi4s.dk/app/appservice/"],
    "Horsens": ["perfectwaste"],
    "Hvidovre": ["perfectwaste"],
    "Høje-Taastrup": ["perfectwaste"],
    "Hørsholm": ["renoweb"],
    "Ikast-Brande": ["ikastbrande"],
    "Ishøj": ["vestfor"],
    "Jammerbugt": ["renoweb"],
    "Kalundborg": ["perfectwaste"],
    "Kerteminde": ["renoweb"],
    "København": ["nemaffald", 'kk'],
    "Køge": ["perfectwaste"],
    "Langeland": ["affaldonline", "YmU4YTk0MjAtYTlhZS00MmU2LTgzZjItZWRhNWVjM2ZhMjlm"],
    "Lejre": ["renoweb"],
    "Lemvig": ["openexp", "renomatic.nomi4s.dk/app/appservice/"],
    "Lolland": ["perfectwaste"],
    "Lyngby-Taarbæk": ["renoweb"],
    "Mariagerfjord": ["renoweb"],
    "Morsø": ["affaldonline", "MDE5OWI3ZDItYmJhZS00NmE1LWE3MjYtMjkzYzkyMzZmNGU1"],
    "Norddjurs": ['renodjurs'],
    "Næstved": ["perfectwaste"],
    "Nordfyns": ['openexp', 'reno.nordfynskommune.dk/app/AppService/AppService/'],
    "Odense": ["odense"],
    "Odder": ["renosyd", 727],
    "Odsherred": ["perfectwaste"],
    "Randers": ["renoweb"],  # also openexplive 4UGdDU2dhdDFqTHZsV0NQSQ==
    "Rebild": ["affaldonline", "Y2IzZGRjOGMtOTAwYS00M2NlLWFjODgtZWM3NTg3ZGI0ZGIz"],
    "Ringkøbing-Skjern": ["perfectwaste"],
    "Roskilde": ["perfectwaste"],
    "Rudersdal": ["renoweb"],
    "Rødovre": ["renoweb"],
    "Samsø": ["renoweb"],
    "Silkeborg": ["silkeborg"],
    "Skanderborg": ["renosyd", 746],
    "Skive": ["openexp", "renomatic.nomi4s.dk/app/appservice/"],
    "Slagelse": ["perfectwaste"],
    "Solrød": ["perfectwaste"],
    "Stevns": ["perfectwaste"],
    "Struer": ["openexp", "renomatic.nomi4s.dk/app/appservice/"],
    "Svendborg": ["renoweb"],
    "Syddjurs": ['renodjurs'],
    "Sønderborg": ["renoweb"],
    "Thy": ["openexplive", "5NmkzUGpvZlRaMzdqZzBEQw=="],
    "Tårnby": ["perfectwaste"],
    "Vallensbæk": ["vestfor"],
    "Varde": ["renoweb"],
    "Vejen": ["perfectwaste"],
    "Vejle": ["affaldonline", "MjA5Y2I2NjktZTJlOC00YzliLTgwNDgtODI4N2RiNTFhNjFl"],
    "Viborg": ["openexp", "dagrenovation.viborg.dk/app/AppService/"],
    "Vordingborg": ["renoweb"],
    "Ærø": ["affaldonline", "ZGI3NjVhMmYtM2Y1MC00YWJkLWE3MzgtMzgyNTgxM2ZlZGNi"],
}


SUPPORTED_MUNICIPALITIES = sorted(MUNICIPALITIES_LIST.keys())
