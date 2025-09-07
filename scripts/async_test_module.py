#!/usr/bin/env python3
# ruff: noqa: F401
"""This module is only used to run some realtime data tests using the async functions, while developing the module."""

import argparse
import asyncio
from aiohttp import ClientSession
import datetime as dt
import logging
import time
import sys
import pickle
from pathlib import Path

sys.path.insert(0, str((Path(__file__).parent.parent / 'custom_components/affalddk').resolve()))

from pyaffalddk.api import GarbageCollection
from pyaffalddk.municipalities import MUNICIPALITIES_LIST
from pyaffalddk.const import NAME_ARRAY
from pyaffalddk.interface import AffaldDKNoConnection

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Async test module."""
    parser = argparse.ArgumentParser(description="Async test module")

    parser.add_argument("municipality", help="The name of the municipality")
    parser.add_argument("--municipalities",
                        action="store_true", help="list municipalities")
    parser.add_argument("-a", "--address_id", type=str, help="address id")
    parser.add_argument("-s", "--street", type=str, help="street name")
    parser.add_argument("-n", "--number", type=str, help="street number")
    parser.add_argument("-z", "--zipcode", type=str, help="zipcode")
    parser.add_argument("--smoketest", type=str,
                        help="add to smoketest data with this name")
    parser.add_argument("--pickup", action="store_true", help="show pickups")
    parser.add_argument("--force", action="store_true", help="force overwrite of smoketest")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("ical").setLevel(logging.WARNING)
    start = time.time()

    async with ClientSession() as session:
        if args.municipalities:
            for row in MUNICIPALITIES_LIST:
                print(row.capitalize())
            sys.exit(0)

        gc = GarbageCollection(municipality=args.municipality, session=session)
        if args.street or args.address_id:
            if args.street:
                try:
                    address_list = await gc.get_address_list(
                        zipcode=args.zipcode, street=args.street, house_number=args.number
                    )
                    for address_name in address_list:
                        address = await gc.get_address(address_name)
                        address_id = address.address_id
                        print("")
                        print("========================================================")
                        print("Address ID: ", address.address_id)
                        print("Kommune: ", address.kommunenavn)
                        print("Addresse: ", address.address)

                except Exception as err:
                    print(err)
            else:
                address_id = args.address_id

            if args.pickup:
                try:
                    await gc.init_address(address_id)
                    data = await gc.get_pickup_data(address_id)
                    if data:
                        print("")
                        print(
                            "========================================================")
                        for item in NAME_ARRAY:
                            if data.get(item) is None:
                                continue
                            print(f"{data[item].friendly_name}:")
                            print("  Nøgle: ", item)
                            print("  Gruppe: ", data[item].group)
                            print("  Navn: ", data[item].friendly_name)
                            try:
                                print("  Dato: ",
                                      data[item].date.strftime("%d-%m-%Y"))
                            except:  # noqa: E722
                                print("  Dato: ", data[item].date)
                            print("  Beskrivelse: ", data[item].description)
                            print("  Icon: ", data[item].icon)
                            print("  Picture: ", data[item].entity_picture)
                            print("  Sidst Opdateret: ",
                                  dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
                            print(
                                "  ======================================================")

                        item = "next_pickup"
                        print("Mext Pickup:")
                        print("  Gruppe: ", data[item].group)
                        print("  Navn: ", data[item].friendly_name)
                        print("  Dato: ", data[item].date.strftime("%d-%m-%Y"))
                        print("  Beskrivelse: ", data[item].description)
                        print("  Icon: ", data[item].icon)
                        print("  Picture: ", data[item].entity_picture)
                        print("  Sidst Opdateret: ",
                              dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
                        print(
                            "  ======================================================")

                except AffaldDKNoConnection as err:
                    print(err)

            if args.smoketest:
                with open('tests/data/smoketest_garbage_data.p', 'rb') as fh:
                    smokedata = pickle.load(fh)

                data = await gc._api.get_garbage_data(address_id)
                if data:
                    if args.smoketest in smokedata and args.force is False:
                        raise RuntimeError(
                            f'the name "{args.smoketest}"is already in the smoketest set')
                    smokedata[args.smoketest] = {
                        'city': args.municipality, 'data': data}
                    print(f'Added "{args.smoketest}" to the smoketest set...')
                    with open('tests/data/smoketest_garbage_data.p', 'wb') as fh:
                        smokedata = pickle.dump(smokedata, fh)

    end = time.time()
    _LOGGER.info("Execution time: %s seconds", end - start)


asyncio.run(main())
