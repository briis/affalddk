# ruff: noqa: S301
import pytest
from freezegun import freeze_time
from aiohttp import ClientSession
from custom_components.affalddk.pyaffalddk.api import GarbageCollection

from pathlib import Path
import pickle
import json
import os


CI = os.getenv("CI") == "true"
skip_in_ci = pytest.mark.skipif(CI, reason="Skipped in CI environment")
UPDATE = True
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
    # test Frederiksberg
    with capsys.disabled():
        async with ClientSession() as session:
            gc = GarbageCollection('Frederiksberg', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Frederiksberg_70984', 'address_id': '70984',
                'kommunenavn': 'Frederiksberg', 'address': 'Smallegade 1'}
            if not CI:
                address_list = await gc.get_address_list('2000', 'Smallegade', '1')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('2000', 'Smallegade', '')
                assert len(address_list) == 79
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('2000', 'Smallegade', '2')
                assert len(address_list) == 9

            async def get_data(*args, **kwargs):
                return openexplive_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Frederiksberg', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-05-20")
async def test_OpenExp(capsys, monkeypatch):
    # test Viborg
    with capsys.disabled():
        async with ClientSession() as session:
            gc = GarbageCollection('Viborg', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Viborg_67580', 'address_id': '67580',
                'kommunenavn': 'Viborg', 'address': 'Prinsens alle 5'}
            if not CI:
                address_list = await gc.get_address_list('8800', 'Prinsens Alle', '5')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('8800', 'Vesterled', '')
                assert len(address_list) == 52
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('8800', 'Vesterled', '4')
                assert len(address_list) == 9

            async def get_data(*args, **kwargs):
                return openexp_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Viborg', pickups, UPDATE)
            print('done: ', gc._municipality)


@pytest.mark.asyncio
@freeze_time("2025-05-20")
async def test_Affaldonline(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession() as session:
            gc = GarbageCollection('Vejle', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Vejle_1261533|490691026|0', 'address_id': '1261533|490691026|0',
                'kommunenavn': 'Vejle', 'address': 'Klostergade 2a'}
            if not CI:
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
        async with ClientSession() as session:
            gc = GarbageCollection('Køge', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Køge_27768', 'address_id': '27768',
                'kommunenavn': 'Køge', 'address': 'Torvet 1'}
            if not CI:
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
        async with ClientSession() as session:
            gc = GarbageCollection('Aalborg', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Aalborg_139322', 'address_id': '139322',
                'kommunenavn': 'Aalborg', 'address': 'Boulevarden 13'}
            if not CI:
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
        async with ClientSession() as session:
            gc = GarbageCollection('Odense', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Odense_112970', 'address_id': '112970',
                'kommunenavn': 'Odense', 'address': 'Flakhaven 2'}
            if not CI:
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
        async with ClientSession() as session:
            gc = GarbageCollection('Aarhus', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Aarhus_07517005___1__2____', 'address_id': '07517005___1__2____',
                'kommunenavn': 'Aarhus', 'address': 'Rådhuspladsen 1, 2.'}
            if not CI:
                address_list = await gc.get_address_list('8000', 'Rådhuspladsen', '2')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('8000', 'Rådhuspladsen', '')
                assert len(address_list) == 44
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('8000', 'Rådhuspladsen', '2')
                assert len(address_list) == 11

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
        async with ClientSession() as session:
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
        async with ClientSession() as session:
            gc = GarbageCollection('Haderslev', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Haderslev_UHJvcGVydHlUeXBlOjEwMTQzNDE=', 'address_id': 'UHJvcGVydHlUeXBlOjEwMTQzNDE=',
                'kommunenavn': 'Haderslev', 'address': "Christian x's vej 29"
                }
            if not CI:
                address_list = await gc.get_address_list('6100', "Christian X Vej", '29')
                address = await gc.get_address(address_list[0])
    #            print(address.__dict__)
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
        async with ClientSession() as session:
            gc = GarbageCollection('Norddjurs', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Norddjurs_40130', 'address_id': '40130',
                'kommunenavn': 'Norddjurs', 'address': 'Torvet 3'
                }
            if not CI:
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
        async with ClientSession() as session:
            gc = GarbageCollection('Herning', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'Herning_8486', 'address_id': '8486',
                'kommunenavn': 'Herning', 'address': 'Torvet 5 (herning)'
                }
            if not CI:
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
                    return [{"Beholder-id": "plast/metal", "Tømningsdag": "Tirsdag Ugenumre: 24,1,10"}]
                if args[0] == 'newyear2':
                    return [{"Beholder-id": "plast/metal", "Tømningsdag": "Tirsdag Ugenumre: 2,10,20"}]
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
        async with ClientSession() as session:
            gc = GarbageCollection('København', session=session, fail=True)
            print('start: ', gc._municipality)

            add = {
                'uid': 'København_a4e9a503-c27f-ef11-9169-005056823710',
                'address_id': 'a4e9a503-c27f-ef11-9169-005056823710',
                'kommunenavn': 'København', 'address': 'Rådhuspladsen 1'}
            if not CI:
                address_list = await gc.get_address_list('1550', 'Rådhuspladsen', '1')
                address = await gc.get_address(address_list[0])
                # print(address.__dict__)
                assert address.__dict__ == add
                address_list = await gc._api.get_address_list('2300', 'Irlandsvej', '')
                assert len(address_list) == 50
                await assert_add_list(gc, address_list)
                address_list = await gc._api.get_address_list('2300', 'Irlandsvej', '1')
                assert len(address_list) == 14

            async def get_data(*args, **kwargs):
                return kbh_ics_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data(add['address_id'])
            update_and_compare('Kbh', pickups, UPDATE)
            assert pickups['next_pickup'].description == 'Rest/Madaffald'
            assert pickups['next_pickup'].date.strftime('%d/%m/%y') == '05/05/25'
            assert list(pickups.keys()) == ['restaffaldmadaffald', 'farligtaffald', 'next_pickup']
            print('done: ', gc._municipality)
