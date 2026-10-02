#!/usr/bin/env python3
# ruff: noqa: T201, S603, S301
"""Weekly live API check for the pyaffalddk providers.

Runs on a server inside Denmark (several municipality endpoints are
geo-blocked and hang from foreign/CI runners). It

1. optionally runs tests/test_interface.py (live address lookups for every
   tested provider; garbage data is mocked with fixtures), and
2. probes the providers that have no interface test with a real address
   search + garbage pull.

The pytest suite is skipped by default; pass --with-pytest to include it.
Exit code is 1 if anything failed, so it can drive cron mail. Optionally
POST a JSON summary to a webhook (Discord/ntfy/Home Assistant) with
--notify URL or the NOTIFY_URL environment variable.

Usage (from the repo root, with the pyaffald env python):
    python scripts/weekly_api_check.py
    python scripts/weekly_api_check.py --with-pytest
    python scripts/weekly_api_check.py --notify https://ntfy.sh/mytopic
    python scripts/weekly_api_check.py --with-pytest --progress
Cron example (Mondays 06:30):
    30 6 * * 1  <env>/bin/python <repo>/scripts/weekly_api_check.py --notify <url> >> <repo>/weekly_api_check.log 2>&1
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

from aiohttp import ClientSession

ROOT = Path(__file__).resolve().parent.parent
# Append, not insert: custom_components/affalddk contains calendar.py and
# sensor.py, which would shadow stdlib modules if placed first on sys.path.
sys.path.append(str(ROOT / 'custom_components' / 'affalddk'))

from pyaffalddk.api import GarbageCollection  # noqa: E402

# One representative address per provider that has no test in
# test_interface.py, plus Aarhus (whose test uses fixture data only; the
# live pull runs here instead). Addresses verified 2026-09-29; adjust if an
# address loses service. The probe walks up to MAX_ADDRESSES_TO_TRY
# addresses on the street, so a single address losing service does not fail
# the check.
PROBE_ADDRESSES = {
    'aarhus': ('Aarhus', '8000', 'Rådhuspladsen', '2'),
    'renosyd': ('Odder', '8300', 'Nørregade', '12b'),
    'ikastbrande': ('Ikast-Brande', '7430', 'Gammelagervej', '8'),
    'affaldonlineweb': ('Middelfart', '5500', 'Vestergade', '1'),
    'kolding': ('Kolding', '6000', 'Skovbrynet', '2'),
}

# nemaffald is kept in the APIS map but has no municipalities left.

MAX_ADDRESSES_TO_TRY = 5


async def probe_provider(session, municipality, zipcode, street, house_number):
    """Live address search + garbage pull for one municipality."""
    gc = GarbageCollection(municipality, session=session, fail=False)
    address_list = await gc.get_address_list(zipcode, street, house_number)
    if not address_list:
        raise RuntimeError(f'no addresses found for {street} {house_number}, {zipcode}')

    last_err = None
    for name in address_list[:MAX_ADDRESSES_TO_TRY]:
        try:
            address = await gc.get_address(name)
            if address is None:
                raise RuntimeError('address lookup returned nothing')
            await gc.init_address(address.address_id)
            gc.today = None  # force refetch: get_pickup_data caches per day
            data = await gc.get_pickup_data(address.address_id)
            if not data or 'next_pickup' not in data:
                raise RuntimeError('no pickup events returned')
            return address.address, len(data)
        except Exception as err:  # noqa: BLE001
            last_err = err
    raise RuntimeError(f'all {min(len(address_list), MAX_ADDRESSES_TO_TRY)} '
                       f'addresses failed, last error: {last_err}')


def run_pytest(progress=False):
    """Run the live interface test suite in a subprocess."""
    env = os.environ.copy()
    env.update({'CI': 'true', 'TZ': 'Europe/Copenhagen'})
    if progress:
        # Stream output live so the user sees each test as it runs.
        proc = subprocess.run(  # noqa: S603
            [sys.executable, '-m', 'pytest', 'tests/test_interface.py',
             '-v', '--disable-warnings'],
            cwd=ROOT, env=env, timeout=900,
        )
        output = ''
        return proc.returncode == 0, output
    proc = subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'pytest', 'tests/test_interface.py',
         '-q', '--disable-warnings'],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=900,
    )
    return proc.returncode == 0, proc.stdout + proc.stderr


async def notify(url, ok, lines):
    """POST a plain-text summary to a webhook (e.g. ntfy.sh), if configured."""
    try:
        async with ClientSession(trust_env=True) as session:
            await session.post(url, data='\n'.join(lines).encode('utf-8'),
                               headers={'Title': f'AffaldDK API check: '
                                                 f'{"OK" if ok else "FAILED"}'})
    except Exception as err:  # noqa: BLE001
        print(f'notify failed: {err}')


async def main():
    parser = argparse.ArgumentParser(description='Weekly live API check')
    parser.add_argument('--notify', default=os.getenv('NOTIFY_URL'),
                        help='webhook URL to POST a JSON summary to')
    parser.add_argument('--with-pytest', action='store_true',
                        help='run the pytest interface suite (skipped by default)')
    parser.add_argument('--skip-probes', action='store_true',
                        help='skip the per-provider probes')
    parser.add_argument('--progress', action='store_true',
                        help='show live progress: stream pytest output and print '
                             'each probe as it starts')
    args = parser.parse_args()

    results = []  # (name, ok, detail)

    if args.with_pytest:
        ok, output = run_pytest(progress=args.progress)
        tail = output.strip().splitlines()[-1] if output.strip() else ''
        if not tail and args.progress:
            tail = 'output streamed above'
        results.append(('pytest test_interface.py', ok, tail))
        if not ok and output.strip():
            print('\n--- pytest output (tail) ---')
            print('\n'.join(output.strip().splitlines()[-40:]))

    if not args.skip_probes:
        async with ClientSession(trust_env=True) as session:
            for provider, (muni, zipcode, street, number) in PROBE_ADDRESSES.items():
                if args.progress:
                    print(f'probing {provider} ({muni}, {street} {number}, '
                          f'{zipcode})...', flush=True)
                try:
                    address, count = await probe_provider(
                        session, muni, zipcode, street, number)
                    results.append((provider, True, f'{address} -> {count} pickups'))
                except Exception as err:  # noqa: BLE001
                    results.append((provider, False, str(err)))

    print('\n=== Weekly API check summary ===')
    ok = True
    for name, passed, detail in results:
        print(f'{"PASS" if passed else "FAIL"}  {name:24} {detail}')
        ok = ok and passed
    print(f'==> {"ALL OK" if ok else "FAILURES DETECTED"}')

    if args.notify:
        await notify(args.notify, ok,
                     [f'{"PASS" if passed else "FAIL"}  {name}: {detail}'
                      for name, passed, detail in results])

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    asyncio.run(main())
