# ruff: noqa: S301, B023
import pytest
from freezegun import freeze_time
from aiohttp import ClientSession
import datetime as dt

from custom_components.affalddk.pyaffalddk import api, const
from custom_components.affalddk.pyaffalddk.api import GarbageCollection
from custom_components.affalddk.pyaffalddk.const import NAME_LIST

from .data import const_tests
from pathlib import Path
import pickle
import json
from ical.calendar_stream import IcsCalendarStream


datadir = Path(__file__).parent/'data'


# always sort and overwrite the supported_items.json when running pytest
for key, vals in const.SUPPORTED_ITEMS.items():
    const.SUPPORTED_ITEMS[key] = sorted(set(vals), key=str.lower)
with open(datadir.parents[1] / 'custom_components/affalddk/pyaffalddk/supported_items.json', 'w', encoding="utf-8") as fh:
    json.dump(const.SUPPORTED_ITEMS, fh, indent=4, ensure_ascii=False)


def test_const_consistency(capsys):
    with capsys.disabled():
        names = list(NAME_LIST.values())
        assert len(set(names)) == len(names)


@pytest.mark.asyncio
@freeze_time("2025-05-09")
async def test_smoketest(capsys, monkeypatch, update=False):
    with capsys.disabled():
        async with ClientSession() as session:
            smokedata = pickle.load((datadir / 'smoketest_garbage_data.p').open('rb'))
            smokecompare_file = datadir / 'smoketest_fractions.json'
            with smokecompare_file.open('r') as fh:
                smokecompare = json.load(fh)

            for name, val in smokedata.items():
                city = val['city']
                gc = GarbageCollection(city, session=session, fail=True)

                async def get_data(*args, **kwargs):
                    return val['data']
                monkeypatch.setattr(gc._api, "get_garbage_data", get_data)
                pickups = await gc.get_pickup_data(1111)
                keys = list(pickups.keys())

                assert set(keys[:-1]).issubset(NAME_LIST)
                assert keys[-1] == 'next_pickup'

                data = {key: pickups[key].description for key in keys[:-1]}
                data['next_pickup'] = pickups['next_pickup'].friendly_name

                if name not in smokecompare or update:
                    smokecompare[name] = data
                    print(f'adding "{name}" to the smoketest compare data')
                    with smokecompare_file.open('w', encoding="utf-8") as fh:
                        json.dump(smokecompare, fh, indent=2, ensure_ascii=False)
                if smokecompare[name] != data:
                    print(name, city)
                    print(data)
                    print(smokecompare[name])
                assert smokecompare[name] == data


@pytest.mark.asyncio
@freeze_time("2025-05-22 12:30:00")
async def test_switch_next(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession() as session:
            gc = GarbageCollection('Viborg', session=session, fail=True)
            openexp_data = json.loads((datadir/'openexp.data').read_text())

            async def get_data(*args, **kwargs):
                return openexp_data
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data('1111')
            assert pickups['next_pickup'].date == dt.date(2025, 5, 22)

            gc.set_switch_time(12, 0)
            pickups = await gc.get_pickup_data('1111')
            assert pickups['next_pickup'].date == dt.date(2025, 6, 4)

@pytest.mark.asyncio
@freeze_time("2025-05-22 12:30:00")
async def test_next_of_same(capsys, monkeypatch):
    with capsys.disabled():
        async with ClientSession() as session:
            gc = GarbageCollection('Viborg', session=session, fail=True)
            openexp_data = json.loads((datadir/'openexp.data').read_text())

            async def get_data(*args, **kwargs):
                return {'collections': [item for item in openexp_data['collections'] if item['fraction']['name'] == 'Rest/Madaffald']}
            monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

            pickups = await gc.get_pickup_data('1111')
            assert pickups['next_pickup'].date == dt.date(2025, 5, 22)

            gc.set_switch_time(12, 0)
            pickups = await gc.get_pickup_data('1111')
            assert pickups['next_pickup'].date == dt.date(2025, 6, 5)


def test_type_from_material_cleaning(capsys, monkeypatch):
    with capsys.disabled():
        for category, vals in const_tests.MATERIAL_LIST.items():
            for val in vals:
                cat = api.get_garbage_types(val, 'test', '1111', fail=False)[0]
                if cat != category:
                    print(val, api.clean_fraction_string(val))
                assert cat == category

        for val in const_tests.NON_MATERIAL_LIST:
            cat = api.get_garbage_types(val, 'test', '1111', fail=False)[0]
            assert cat == 'not-supported'


def test_type_cleaning(capsys, monkeypatch):
    with capsys.disabled():
        for category, vals in const_tests.SUPPORTED_ITEMS.items():
            for val in vals:
                cat = api.get_garbage_types(val, 'test', '1111', fail=False)[0]
                if cat != category:
                    print(val, api.clean_fraction_string(val))
                assert cat == category


def test_ics(capsys):
    with capsys.disabled():
        odense_ics_data = (datadir/'odense_ics.data').read_text()
        ics = IcsCalendarStream.calendar_from_ics(odense_ics_data)
        data = odense_ics_data.replace("END:VTIMEZONE", """BEGIN:STANDARD
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
END:DAYLIGHT
END:VTIMEZONE""")
        ics2 = IcsCalendarStream.calendar_from_ics(data)
        assert ics.events == ics2.events


@freeze_time("2025-06-16")
def test_weekday_conversion(capsys):
    with capsys.disabled():
        date = api.weekday_week_to_date('Mandag', 26, 2024)
        assert date == dt.date(2024, 6, 24)

        date = api.weekday_week_to_date('MANDAG', 26, 2025)
        assert date == dt.date(2025, 6, 23)

        date = api.weekday_week_to_date('Mandag', 26)
        assert date == dt.date(2025, 6, 23)

        date = api.weekday_week_to_date('Onsdag', -1)
        assert date == dt.date(2025, 6, 18)

        date = api.weekday_week_to_date('Onsdag', -2)
        assert date == dt.date(2025, 6, 25)

