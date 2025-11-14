"""This module contains the code to get garbage data from AffaldDK."""

import datetime as dt
from ical.calendar_stream import IcsCalendarStream
from ical.exceptions import CalendarParseError
import logging
import re
from typing import Any
import aiohttp
from dateutil import parser

from .const import (
    ICON_LIST,
    NAME_LIST,
    NON_SUPPORTED_ITEMS,
    RE_WORDS,
    RE_RAW,
    SPECIAL_MATERIALS,
    STRIPS,
    SUPPORTED_ITEMS,
    WEEKDAYS,
)
from .municipalities import MUNICIPALITIES_IDS, MUNICIPALITIES_LIST
from .data import PickupEvents, PickupType, AffaldDKAddressInfo
from . import interface

_LOGGER = logging.getLogger(__name__)


APIS = {
    'odense': interface.OdenseAffaldAPI,
    'aarhus': interface.AarhusAffaldAPI,
    'nemaffald': interface.NemAffaldAPI,
    'perfectwaste': interface.PerfectWasteAPI,
    'renoweb': interface.RenowebghAPI,
    'vestfor': interface.VestForAPI,
    'affaldonline': interface.AffaldOnlineAPI,
    'openexp': interface.OpenExperienceAPI,
    'openexplive': interface.OpenExperienceLiveAPI,
    'provas': interface.ProvasAPI,
    'renodjurs': interface.RenoDjursAPI,
    'renosyd': interface.RenoSydAPI,
    'herning': interface.AffaldWebAPI,
    'ikastbrande': interface.IkastBrandeAPI,
    'silkeborg': interface.SilkeborgAPI,
    'kolding': interface.InfovisionAPI,
}


class GarbageCollection:
    """Class to get garbage collection data."""

    def __init__(
        self,
        municipality: str,
        session: aiohttp.ClientSession = None,
        switch_hour: int = 15,
        fail: bool = False,
    ) -> None:
        """Initialize the class."""
        self._municipality = municipality
        self._street = None
        self._house_number = None
        self._api_type = None
        self._address_id = None
        self.fail = fail
        self.set_switch_time(switch_hour, 0)
        self.utc_offset = dt.datetime.now().astimezone().utcoffset()
        self.today = None
        self.last_fetch = ''
        municipality_id = MUNICIPALITIES_IDS.get(self._municipality.lower(), '')

        for key, value in MUNICIPALITIES_LIST.items():
            if key.lower() == self._municipality.lower():
                self._api_type = value[0]
                if len(value) > 1:
                    municipality_id = value[1]
                self._api = APIS[self._api_type](municipality_id, session=session)

        if self._api_type is None:
            raise RuntimeError(f'Unknow municipality: "{municipality}"')

    def set_switch_time(self, hours, minutes):
        self.switch_time = dt.time(hours, minutes)

    async def async_init(self) -> None:
        """Initialize the connection."""
        if self._municipality is not None:
            if self._api_type == "nemaffald":
                await self._api.token

    async def init_address(self, address_id) -> None:
        """calls when initializing a new address the first time"""
        if self._municipality is not None:
            if self._api_type == "perfectwaste":
                await self._api.save_to_db(address_id)

    async def get_address_list(self, zipcode, street, house_number):
        """Get list of address, id """
        if self._api_type is not None:
            address_list = await self._api.get_address_list(zipcode, street, house_number)
            return sorted(address_list, key=extract_house_number)
        raise interface.AffaldDKNotSupportedError("Cannot find Municipality")

    async def get_address(self, address_name) -> AffaldDKAddressInfo:
        """Get the address from id"""

        if self._api_type is not None:
            self._address_id, address = await self._api.get_address(address_name)

            if self._address_id is None:
                raise interface.AffaldDKNotValidAddressError("Address not found")

            address_data = AffaldDKAddressInfo(
                str(self._address_id),
                self._municipality.capitalize(),
                address.capitalize()
            )
            return address_data
        else:
            raise interface.AffaldDKNotSupportedError("Cannot find Municipality")

    def update_pickup_event(self, item_name, address_id, _pickup_date):
        if _pickup_date is not None and _pickup_date < self.today:
            return 'old-event'

        for key in get_garbage_types(item_name, self._municipality, address_id, self.fail):
            if key in ['not-supported', 'missing-type']:
                return key

            if (key not in self.pickup_events) or (_pickup_date < self.pickup_events[key].date):
                _pickup_event = {
                    key: PickupType(
                        date=_pickup_date,
                        group=key,
                        friendly_name=NAME_LIST.get(key),
                        icon=ICON_LIST.get(key),
                        entity_picture=f"{key}.svg",
                        description=item_name,
                    )
                }
                self.pickup_events.update(_pickup_event)

            if _pickup_date in self.next_events:
                if NAME_LIST.get(key) not in self.next_events[_pickup_date]['name']:
                    self.next_events[_pickup_date]['name'] .append(NAME_LIST.get(key))
                    self.next_events[_pickup_date]['description'].append(item_name)
            else:
                self.next_events.update({_pickup_date: {'name': [NAME_LIST.get(key)], 'description': [item_name]}})
        return 'done'

    def set_next_event(self):
        if self.next_events:
            if dt.datetime.now().time() > self.switch_time:
                _next_pickup = sorted([key for key in self.next_events.keys() if key > self.today])[0]
            else:
                _next_pickup = sorted([key for key in self.next_events.keys() if key >= self.today])[0]

            _next_name = self.next_events[_next_pickup]['name']
            _next_description = self.next_events[_next_pickup]['description']
            # Zip, sort by _next_name, then unzip
            sorted_pairs = sorted(zip(_next_name, _next_description), key=lambda pair: pair[0])
            _next_name, _next_description = zip(*sorted_pairs)

            _next_pickup_event = {
                "next_pickup": PickupType(
                    date=_next_pickup,
                    group="genbrug",
                    friendly_name=list_to_string(_next_name),
                    icon=ICON_LIST.get("genbrug"),
                    entity_picture="genbrug.svg",
                    description=list_to_string(_next_description),
                )
            }
            self.pickup_events.update(_next_pickup_event)

    async def get_pickup_data(self, address_id: str, debug=False) -> PickupEvents:
        """Get the garbage collection data."""

        # pull data from these each time we sync
        if self._api_type == 'odense':
            garbage_data = await self._api.get_garbage_data(address_id)

        if (self._api_type is not None) & (self.today != dt.date.today()):
            self.pickup_events: PickupEvents = {}
            self.next_events: PickupEvents = {}
            self.today = dt.date.today()
            self.last_fetch = str(dt.datetime.now())

            if self._api_type == 'odense':
                try:
                    ics = IcsCalendarStream.calendar_from_ics(garbage_data)
                    for event in ics.timeline:
                        _garbage_types = split_ical_garbage_types(event.summary)
                        for garbage_type in _garbage_types:
                            _pickup_date = event.start_datetime.date()
                            self.update_pickup_event(garbage_type, address_id, _pickup_date)
                except CalendarParseError as err:
                    _LOGGER.error("Error parsing iCal data: %s", err)

            elif self._api_type == "aarhus":
                garbage_data = await self._api.get_garbage_data(address_id)
                for row in garbage_data:
                    _pickup_date = iso_string_to_date(row["date"])
                    for garbage_type in row["fractions"]:
                        self.update_pickup_event(garbage_type, address_id, _pickup_date)

            elif self._api_type == "nemaffald":
                garbage_data = await self._api.get_garbage_data(address_id)
                try:
                    ics = IcsCalendarStream.calendar_from_ics(garbage_data)
                    for event in ics.timeline:
                        _garbage_types = split_ical_garbage_types(event.summary)
                        for garbage_type in _garbage_types:
                            _pickup_date = (event.start_datetime + self.utc_offset).date()
                            self.update_pickup_event(garbage_type, address_id, _pickup_date)
                except CalendarParseError as err:
                    _LOGGER.error("Error parsing iCal data: %s", err)

            elif self._api_type == "perfectwaste":
                garbage_data = await self._api.get_garbage_data(address_id)
                for row in garbage_data:
                    _pickup_date = iso_string_to_date(row["date"])
                    for item in row["fractions"]:
                        garbage_type = item['fractionName']
                        self.update_pickup_event(garbage_type, address_id, _pickup_date)

            elif self._api_type == "renoweb":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    if item['nextpickupdatetimestamp']:
                        _pickup_date = dt.datetime.fromtimestamp(int(item["nextpickupdatetimestamp"])).date()
                        self.update_pickup_event(item['name'], address_id, _pickup_date)

            elif self._api_type == "vestfor":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    _pickup_date = iso_string_to_date(item['start'])
                    self.update_pickup_event(item['title'], address_id, _pickup_date)

            elif self._api_type == "affaldonline":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    _pickup_date = iso_string_to_date(item['date'])
                    for garbage_type in item['collections']:
                        for container_description in set([cont['description'] for cont in garbage_type['containers']]):
                            self.update_pickup_event(container_description, address_id, _pickup_date)

            elif self._api_type == "openexp":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data['collections']:
                    dt_list = [iso_string_to_date(d) for d in item['dates']]
                    if dt_list:
                        for _pickup_date in sorted([d for d in dt_list if d >= self.today])[:2]:
                            fraction_name = item['fraction']['name']
                            self.update_pickup_event(fraction_name, address_id, _pickup_date)

            elif self._api_type == "openexplive":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    fraction_name = item['fraction']['name']
                    dt_list = [iso_string_to_date(d['date']) for d in item['upcoming_dates']]
                    if dt_list:
                        for _pickup_date in sorted([d for d in dt_list if d >= self.today])[:2]:
                            self.update_pickup_event(fraction_name, address_id, _pickup_date)

            elif self._api_type == "provas":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    _pickup_date = iso_string_to_date(item['date'])
                    fraction_name = item['container']['waste_fraction']['name']
                    self.update_pickup_event(fraction_name, address_id, _pickup_date)

            elif self._api_type == "renodjurs":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    _pickup_date = iso_string_to_date(item['Næste tømningsdag'], dayfirst=True)
                    fraction_name = item['Ordning']
                    self.update_pickup_event(fraction_name, address_id, _pickup_date)

            elif self._api_type == "renosyd":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    _pickup_date = iso_string_to_date(item['dato'])
                    fraction_name = ' '.join(sorted(item['fraktioner']))
                    self.update_pickup_event(fraction_name, address_id, _pickup_date)

            elif self._api_type == "herning":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    fraction_name = re.sub(r'^\d+\s*', '', item['Beholder-id'])
                    weekday, weeks = self._api.get_weekday_and_weeks(item)
                    for [w, y] in weeks:
                        _pickup_date = weekday_week_to_date(weekday, w, year=y)
                        if not _pickup_date:
                            raise RuntimeWarning(f'Failed to convert date for Herning, "{item}"')
                        self.update_pickup_event(fraction_name, address_id, _pickup_date)
            elif self._api_type == "ikastbrande":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    if item['Tømningsdag']:
                        _pickup_date = item['Tømningsdag']
                        fraction_name = item['Materiel']
                        self.update_pickup_event(fraction_name, address_id, _pickup_date)
            elif self._api_type == "silkeborg":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    if item['Tømningsdag']:
                        _pickup_date = item['Tømningsdag']
                        fraction_name = item['Materiel']
                        self.update_pickup_event(fraction_name, address_id, _pickup_date)
            elif self._api_type == "kolding":
                garbage_data = await self._api.get_garbage_data(address_id)
                for item in garbage_data:
                    dt_list = [iso_string_to_date(str(d['collectDate'])) for d in item['collectCalendar']]
                    if dt_list:
                        fraction_name = item['containerType']['fraction']['description']
                        for _pickup_date in sorted([d for d in dt_list if d >= self.today])[:2]:
                            self.update_pickup_event(fraction_name, address_id, _pickup_date)

        self.set_next_event()
        return self.pickup_events


def iso_string_to_date(datetext: str, dayfirst=None) -> dt.date:
    """Convert a date string to a datetime object."""
    if datetext == "Ingen tømningsdato fundet!":
        return None
    return parser.parse(datetext, dayfirst=dayfirst).date()


def weekday_week_to_date(weekday_name, week_number, year=None):
    """Convert weekday name and ISO week number to a date.
    If weeks_number is -1 we will find next in uneven weeks,
    and if -2 in even weeks.
    """
    today = dt.date.today()
    if year is None:
        year = today.year

    weekday_name = weekday_name.lower()
    weekdays_lower = [day.lower() for day in WEEKDAYS]
    if weekday_name in weekdays_lower:
        weekday_num = weekdays_lower.index(weekday_name)

        # ISO week: Week 1 always has Jan 4th in it, so we can get the Monday of the desired week:
        # Use ISO calendar: (year, week, weekday)
        # ISO weekday: Monday = 1, Sunday = 7
        iso_weekday = weekday_num + 1

        if week_number < 0:
            remain = 0 if week_number == -2 else 1
            for i in range(0, 14):  # Look up to 2 weeks ahead
                candidate = today + dt.timedelta(days=i)
                if candidate.weekday() == weekday_num:
                    week_number = candidate.isocalendar()[1]
                    if week_number % 2 == remain:
                        return candidate
        else:
            return dt.date.fromisocalendar(year, week_number, iso_weekday)


def get_garbage_types(item, municipality, address_id, fail=False):
    """Get the garbage types."""
    # _LOGGER.debug("Affalds type: %s", item)
    if item in NON_SUPPORTED_ITEMS:
        return ['not-supported']

    for special in SPECIAL_MATERIALS:
        if special.lower() in item.lower():
            return SPECIAL_MATERIALS[special]

    fixed_items = clean_fraction_string(item)
    for fixed_item in fixed_items:
        if fixed_item in [non.lower() for non in NON_SUPPORTED_ITEMS]:
            return ['not-supported']
        for key, values in SUPPORTED_ITEMS.items():
            for entry in values:
                if fixed_item.lower() == entry.lower():
                    return [key]
    print(f'\nmissing: {fixed_items}')
    warn_or_fail(item, municipality, address_id, fail=fail)
    return ['missing-type']


def clean_fraction_string(item):
    fixed_item = item.lower()

    for strip in WEEKDAYS + STRIPS:
        fixed_item = fixed_item.replace(strip.lower(), '')

    strings_in_parenthesis = re.findall(r'\(([^()]*)\)', fixed_item)
    pattern = r"\s*\([^()]*\)"
    fixed_item = re.sub(pattern, "", fixed_item)  # strip anything in parenthesis

    for word in RE_RAW:
        fixed_item = re.sub(word, '', fixed_item)
    for word in RE_WORDS:
        fixed_item = re.sub(fr'(?:\s|\b){word}(?=\s|$)', '', fixed_item)

    if ':' in fixed_item:
        fixed_item = fixed_item.split(':')[1]

    fixed_item = fixed_item.strip().rstrip(',').lstrip(', ').rstrip(' -').lstrip('- ').lstrip('*')
    res = [fixed_item.strip()]
    if ' - ' in fixed_item:
        res += [o.strip() for o in fixed_item.split(' - ')]
    if ', ' in fixed_item:
        res += [o.strip() for o in fixed_item.split(', ')]
    return res + strings_in_parenthesis


def warn_or_fail(name, municipality, address_id, fail=False):
    msg = f'Garbage type [{name}] is not defined in the system. '
    msg += f'Please notify the developer. Municipality: {municipality}, Address ID: {address_id}'

    if fail:
        raise RuntimeError(msg)
    _LOGGER.warning(msg)


def list_to_string(list: list[str]) -> str:
    """Convert a list to a string."""
    return " | ".join(list)


def split_ical_garbage_types(text: str) -> list[str]:
    """Split a text string at every comma and ignore everything from 'på' or if it starts with 'Tømning af'."""
    if text.startswith("Tømning af"):
        text = text[len("Tømning af "):]
    if "på" in text:
        text = text.split("på")[0]
    return [item.strip() for item in text.split(",")]


def key_exists_in_pickup_events(pickup_events: PickupEvents, key: str) -> bool:
    """Check if a key exists in PickupEvents."""
    return key in pickup_events


def value_exists_in_pickup_events(pickup_events: PickupEvents, value: Any) -> bool:
    """Check if a value exists in PickupEvents."""
    return any(event for event in pickup_events.values() if event == value)


def extract_house_number(addr):
    """Sort address string by found house number numerical"""
    parts = addr.split(',', 1)
    second_part = parts[1].strip().lower() if len(parts) > 1 else ""
    match = re.search(r'\d+', parts[0])
    house_num = int(match.group()) if match else float('inf')  # non-numbered addresses go last
    return (house_num, second_part)
