# ruff: noqa: S301
import pytest
from freezegun import freeze_time
from aiohttp import ClientSession
from custom_components.affalddk.pyaffalddk.api import GarbageCollection
from custom_components.affalddk.pyaffalddk.interface import AffaldOnlineWeb, InfovisionAPI, split_housenumber
from pathlib import Path
import pickle
import json
import datetime as dt
import os


CI = os.getenv("CI") == "true"
skip_in_ci = pytest.mark.skipif(CI, reason="Skipped in CI environment")
UPDATE = False
ADDRESS_LIST_KEYS = ['id', 'fullname']

datadir = Path(__file__).parent/'data'
kbh_ics_data = (datadir/'kbh_ics.data').read_text()
odense_ics_data = (datadir/'odense_ics.data').read_text()
aalborg_data_gh = json.loads((datadir/'Aalborg_gh.data').read_text())
aarhus_data = json.loads((datadir/'Aarhus.data').read_text())
koege_data = json.loads((datadir/'Koege.data').read_text())
affaldonline_data = json.loads((datadir/'affaldonline.data').read_text())
vestfor_data = pickle.loads((datadir/'vestfor.data').read_bytes())
openexp_data = json.loads((datadir/'openexp.data').read_text())
openexplive_data = json.loads((datadir/'openexplive.data').read_text())
renodjurs_data = json.loads((datadir/'renodjurs.data').read_text())
provas_data = json.loads((datadir/'provas.data').read_text())
herning_data = json.loads((datadir/'herning.data').read_text())
tønder_data = json.loads((datadir/'tonfor.data').read_text())

FREEZE_TIME = "2025-04-25"
compare_file = (datadir/'compare_data.p')


def update_and_compare(name, actual_data, update=False, debug=False):
    compare_data = pickle.load(compare_file.open('rb'))
    if update:
        compare_data[name] = actual_data
        pickle.dump(compare_data, compare_file.open('wb'))
    if debug and actual_data != compare_data[name]:
        print(actual_data.keys())
        print(compare_data[name].keys())
#        print(actual_data['next_pickup'])
#        print(compare_data[name]['next_pickup'])
    assert actual_data == compare_data[name]


async def assert_add_list(gc, address_list):
    add = await gc.get_address(address_list[0])
    print(add.address_id, add.address)
    assert list(gc._api.address_list[address_list[0]].keys()) == ADDRESS_LIST_KEYS


@pytest.mark.asyncio
@freeze_time("2025-05-25")
async def test_OpenExpLive(capsys, monkeypatch):
    # test Fredericia
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Fredericia', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Fredericia_14578', 'address_id': '14578',
                'kommunenavn': 'Fredericia', 'address': 'Gothersgade 20b'}
            if True:
                address_list = await gc.get_address_list('7000', 'Gothersgade', '20')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('7000', 'korskærvej', '')
                assert len(address_list) == 4
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('7000', 'Korskærvej', '2')
                assert len(address_list) == 1

            async def get_data(*args, **kwargs):
                return openexplive_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Frederiksberg', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-05-20")
async def test_OpenExp(capsys, monkeypatch):
    # test Holstebro
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Holstebro', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Holstebro_14738', 'address_id': '14738',
                'kommunenavn': 'Holstebro', 'address': 'Kirkestræde 11'}
            if True:
                address_list = await gc.get_address_list('7500', 'Kirkestræde', '11')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('7500', 'Skivevej', '')
                assert len(address_list) == 52
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('7500', 'Skivevej', '4')
                assert len(address_list) == 14

            async def get_data(*args, **kwargs):
                return openexp_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Holstebro', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-05-20")
async def test_Affaldonline(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Vejle', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Vejle_1261533|490691026|0', 'address_id': '1261533|490691026|0',
                'kommunenavn': 'Vejle', 'address': 'Klostergade 2a'}
            if True:
                address_list = await gc.get_address_list('7100', 'Klostergade', '2A')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('7100', 'Vestbanevej', '')
                assert len(address_list) == 52
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('7100', 'Vestbanevej', '1')
                assert len(address_list) == 12

            async def get_data(*args, **kwargs):
                return affaldonline_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Vejle', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-05-04")
async def test_PerfectWaste(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Køge', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Køge_27768', 'address_id': '27768',
                'kommunenavn': 'Køge', 'address': 'Torvet 1'}
            if True:
                address_list = await gc.get_address_list('4600', 'Torvet', '1')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('4600', 'Oksbølvej', '')
                assert len(address_list) == 47
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('4600', 'Oksbølvej', '1')
                assert len(address_list) == 11

            async def get_data(*args, **kwargs):
                return koege_data["result"]
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Koege', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-05-04")
async def test_Renoweb(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Aalborg', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Aalborg_139322', 'address_id': '139322',
                'kommunenavn': 'Aalborg', 'address': 'Boulevarden 13'}
            if True:
                address_list = await gc.get_address_list('9000', 'Boulevarden', '13')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('9000', 'Boulevarden', '')
                assert len(address_list) == 425
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('9000', 'Boulevarden', '1')
                assert len(address_list) == 21

            async def get_data(*args, **kwargs):
                return aalborg_data_gh
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Aalborg_gh', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time(FREEZE_TIME)
async def test_Odense(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Odense', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Odense_112970', 'address_id': '112970',
                'kommunenavn': 'Odense', 'address': 'Flakhaven 2'}
            if True:
                address_list = await gc.get_address_list('5000', 'Flakhaven', '2')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('5230', 'Læssøegade', '')
                assert len(address_list) == 162
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('5230', 'Læssøegade', '1')
                assert len(address_list) == 95

            async def get_data(*args, **kwargs):
                return odense_ics_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Odense', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time(FREEZE_TIME)
async def test_Aarhus(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Aarhus', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Aarhus_9b9a6a18-ffb7-4ece-a7f1-5368812e4719',
                'address_id': '9b9a6a18-ffb7-4ece-a7f1-5368812e4719',
                'kommunenavn': 'Aarhus', 'address': 'Rådhuspladsen 2'}
            if True:
                address_list = await gc.get_address_list('8000', 'Rådhuspladsen', '2')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('8000', 'Rådhuspladsen', '')
                assert len(address_list) == 7
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('8000', 'Rådhuspladsen', '2')
                assert len(address_list) == 6

            async def get_data(*args, **kwargs):
                return aarhus_data[0]["plannedLoads"]
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Aarhus', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-05-18")
async def test_VestFor(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Albertslund', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Albertslund_5d715e2a-126f-e511-80cd-005056be6a4c',
                'address_id': '5d715e2a-126f-e511-80cd-005056be6a4c',
                'kommunenavn': 'Albertslund', 'address': 'Nordmarks alle 1'}
            if not CI:
                address_list = await gc.get_address_list('2620', 'Nordmarks Alle', '1')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('2620', 'Nordmarks Alle', '')
                assert len(address_list) == 100
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('2620', 'Nordmarks Alle', '2')
                assert len(address_list) == 2

            async def get_data(*args, **kwargs):
                return vestfor_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Ballerup', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-06-04")
async def test_Provas(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Haderslev', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Haderslev_UHJvcGVydHlUeXBlOjEwMTQzNDE=', 'address_id': 'UHJvcGVydHlUeXBlOjEwMTQzNDE=',
                'kommunenavn': 'Haderslev', 'address': "Christian x's vej 29"
                }
            if True:
                address_list = await gc.get_address_list('6100', "Christian X Vej", '29')
                address = await gc.get_address(address_list[0])
#                print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('6100', 'Parkvej', '')
                assert len(address_list) == 53
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('6100', 'Parkvej', '2')
                assert len(address_list) == 9

            async def get_data(*args, **kwargs):
                return provas_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Haderslev', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-06-04")
async def test_RenoDjurs(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Norddjurs', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Norddjurs_40130', 'address_id': '40130',
                'kommunenavn': 'Norddjurs', 'address': 'Torvet 3'
                }
            if True:
                address_list = await gc.get_address_list('8500', 'Torvet', '3')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('8500', 'Fuglsangparken', '')
                assert len(address_list) == 25
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('8500', 'Fuglsangparken', '1')
                assert len(address_list) == 16

            async def get_data(*args, **kwargs):
                return renodjurs_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Norddjurs', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-06-17")
async def test_Herning(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Herning', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Herning_8486', 'address_id': '8486',
                'kommunenavn': 'Herning', 'address': 'Torvet 5 (herning)'
                }
            if True:
                address_list = await gc.get_address_list('7400', 'Torvet', '5')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('7400', 'Godthåbsvej', '')
                assert len(address_list) == 113
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('7400', 'Godthåbsvej', '1')
                assert len(address_list) == 24

            async def get_data(*args, **kwargs):
                if args[0] == 'newyear1':
                    return [{"fraction": "plast/metal", "day": "Tirsdag", 'weeks':  gc._api.get_weeks('Ugenumre: 24,1,10')}]
                if args[0] == 'newyear2':
                    return [{"fraction": "plast/metal", "day": "Tirsdag", 'weeks':  gc._api.get_weeks('Ugenumre: 2,10,20')}]
                return herning_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Herning', pickups, UPDATE)

            # test over new year
            gc.today = None  # to force refetch...
            pickups = await gc.get_pickup_data('newyear1')
            assert pickups['next_pickup'].date .strftime('%d/%m/%y') == '30/12/25'

            gc.today = None  # to force refetch...
            pickups = await gc.get_pickup_data('newyear2')
            assert pickups['next_pickup'].date .strftime('%d/%m/%y') == '06/01/26'

            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time(FREEZE_TIME)
async def test_Kbh(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('København', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'København_509b3952-857c-e911-bfa7-005056ad66a0',
                'address_id': '509b3952-857c-e911-bfa7-005056ad66a0',
                'kommunenavn': 'København', 'address': 'Rådhuspladsen 1'}
            if True:
                address_list = await gc.get_address_list('1550', 'Rådhuspladsen', '1')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('2300', 'Irlandsvej', '')
                assert len(address_list) == 62
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('2300', 'Irlandsvej', '1')
                assert len(address_list) == 14


@pytest.mark.asyncio
@freeze_time("2026-01-06")
async def test_WasteWatch(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession(trust_env=True) as session:
            gc = GarbageCollection('Tønder', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Tønder_a976f9e9-8136-46fb-a54c-ce8331522834', 'address_id': 'a976f9e9-8136-46fb-a54c-ce8331522834',
                'kommunenavn': 'Tønder', 'address': 'Håndværkervej 4'
                }
            if True:
                address_list = await gc.get_address_list('6261', 'Håndværkervej', '4')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('6270', 'Ulriksalle', '')
                assert len(address_list) == 166
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('6270', 'Ulriksalle', '2')
                assert len(address_list) == 18

            async def get_data(*args, **kwargs):
                return tønder_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Tønder', pickups, UPDATE)
            print('done: ', gc._municipality)


def test_split_housenumber(capsys):
    with capsys.disabled():
        assert split_housenumber('12E') == (12, 'E')
        assert split_housenumber('12') == (12, '')
        assert split_housenumber('12, 2.tv') == (12, '2.tv')


@pytest.mark.asyncio
async def test_affaldonline_pdf_cache(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession() as session:
            gc = GarbageCollection('Sorø', session=session)
            calls = []

            async def get_pdf_calendar(address_id, year):
                calls.append(year)
                return {dt.date(year, 1, 5): {'Restaffald'}}
            monkeypatch.setattr(gc._api, "get_pdf_calendar", get_pdf_calendar)

            with freeze_time("2026-10-01"):
                assert len(await gc._api.get_garbage_data('x')) == 2
                await gc._api.get_garbage_data('x')
                assert calls == [2026, 2027]
            with freeze_time("2026-10-07"):
                await gc._api.get_garbage_data('x')
                assert calls == [2026, 2027]
            with freeze_time("2026-10-08"):
                await gc._api.get_garbage_data('x')
                assert calls == [2026, 2027, 2026, 2027]
            with freeze_time("2027-01-02"):
                await gc._api.get_garbage_data('x')
                assert calls[-2:] == [2027, 2028]


@pytest.mark.asyncio
async def test_kolding_garbage_data(capsys, monkeypatch):
    """InfovisionAPI.get_garbage_data flattens the grouped container response."""
    with capsys.disabled():
        async with ClientSession() as session:
            api = InfovisionAPI('kolding', session=session)

            def container(fraction, dates):
                return {
                    'containerType': {'fraction': {'description': fraction}},
                    'collectCalendar': [{'collectDate': d} for d in dates],
                }

            def mock_request(payload):
                async def get(*args, **kwargs):
                    return payload
                return get

            # Grouped response: every section flattened, multiple chains per
            # section, and a chain with missing/null containerDetails.
            grouped = {
                'chainDetailsOwn': [
                    {'containerDetails': [container('Rest/Madaffald', [20260907])]},
                    {'containerDetails': [
                        container('Glas/Metal', [20260908]),
                        container('Papir/Pap', [20260908]),
                    ]},
                ],
                'chainDetailsZero': [{'containerDetails': None}],
                'chainDetailsUse': [
                    {'containerDetails': [container('Plast og mad- og drikkekartoner', [])]},
                ],
            }
            monkeypatch.setattr(api, 'async_get_request', mock_request(grouped))
            result = await api.get_garbage_data('some-guid')
            assert [c['containerType']['fraction']['description'] for c in result] == [
                'Rest/Madaffald', 'Glas/Metal', 'Papir/Pap',
                'Plast og mad- og drikkekartoner',
            ]

            # A grouped response with no chains yields an empty list.
            monkeypatch.setattr(
                api, 'async_get_request',
                mock_request({'chainDetailsOwn': [], 'chainDetailsZero': None}))
            assert await api.get_garbage_data('some-guid') == []


@pytest.mark.asyncio
async def test_affaldonlineweb_address_and_garbage(capsys, monkeypatch):
    """Silkeborg's affaldonline install returns full addresses in one step and
    nests a table inside the fraction cell of showInfo.php."""
    with capsys.disabled():
        async with ClientSession() as session:
            api = AffaldOnlineWeb('silkeborg', session=session)

            # Newer install: acCal.php returns full address entries directly.
            # The street search is capped and drops "Vestergade 3 1", so it is
            # only found once the query is narrowed by house number.
            broad_style = [
                {'value': 'Vestergade 4 (8600 Silkeborg)',
                 'values': 'Vestergade|4||||8600|Silkeborg|71431359|797735|0'},
                {'value': 'Vestergade 1 (5500 Middelfart)',
                 'values': 'Vestergade|1||||5500|Middelfart|1|2|0'},
            ]
            narrow_style = [
                {'value': 'Vestergade 3 1 (8600 Silkeborg)',
                 'values': 'Vestergade|3||1||8600|Silkeborg|71446184|2012361|0'},
            ]

            async def new_request(url, para=None, **kwargs):
                if 'husnrCal' in url:
                    raise AssertionError('husnrCal.php should not be called')
                return json.dumps(narrow_style if para['term'] == 'Vestergade 3' else broad_style)
            monkeypatch.setattr(api, 'async_get_request', new_request)

            address_list = await api.get_address_list('8600', 'Vestergade', '3')
            assert address_list == ['Vestergade 3 1 (8600 Silkeborg)']
            assert api.address_list['Vestergade 3 1 (8600 Silkeborg)']['id'] == \
                'Vestergade|3||1||8600|Silkeborg|71446184|2012361|0'

            # Without a house number only the (capped) street hits are returned.
            address_list = await api.get_address_list('8600', 'Vestergade', '')
            assert address_list == ['Vestergade 4 (8600 Silkeborg)']

            # Older install: streets only, house numbers via husnrCal.php.
            old_style = [{'value': 'Vestergade (5500 Middelfart)', 'vejnavn': 'Vestergade',
                          'postnr': '5500', 'Bynavn': 'Middelfart'}]
            husnr_html = (
                '<select id="SelHusNr">'
                '<option value="Vestergade|1|B|||5500||14597918|6507092|0">1 B</option>'
                '<option value="Vestergade|2|A|||5500||14597919|6505298|0">2 A</option>'
                '</select>'
            )

            async def old_request(url, para=None, **kwargs):
                if 'husnrCal' in url:
                    return husnr_html
                return json.dumps(old_style)
            monkeypatch.setattr(api, 'async_get_request', old_request)

            address_list = await api.get_address_list('5500', 'Vestergade', '1')
            assert address_list == ['Vestergade 1 B']
            assert api.address_list['Vestergade 1 B']['id'] == \
                'Vestergade|1|B|||5500||14597918|6507092|0'

            # showInfo.php nests a table in the fraction cell; only the outer
            # table's direct rows carry the date/fraction pairs.
            show_info_html = (
                '<table>'
                '<tr><td colspan="2">OKTOBER</td></tr>'
                '<tr><td>02-11</td><td><table><tr>'
                '<td><img src="img/icons/MADAFFALD.jpg"></td><td>Mad-/Rest</td>'
                '</tr></table></td></tr>'
                '<tr><td>23-11</td><td><table><tr>'
                '<td><img src="img/icons/MADAFFALD.jpg"></td>'
                '<td>Mad-/Rest, Plast/MDK/Glas/Metal/Papir/Pap</td>'
                '</tr></table></td></tr>'
                '</table>'
            )

            async def post_request(url, para=None, **kwargs):
                return show_info_html
            monkeypatch.setattr(api, 'async_postform_request', post_request)

            with freeze_time("2026-10-28"):
                result = await api.get_garbage_data('Vestergade|3||1||8600|Silkeborg|71446184|2012361|0')
            assert result == [
                {'Materiel': 'Mad-/Rest', 'Tømningsdag': dt.date(2026, 11, 2)},
                {'Materiel': 'Mad-/Rest', 'Tømningsdag': dt.date(2026, 11, 23)},
                {'Materiel': 'Plast/MDK/Glas/Metal/Papir/Pap', 'Tømningsdag': dt.date(2026, 11, 23)},
            ]
