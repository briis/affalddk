#!/usr/bin/env python3
# ruff: noqa: T201, E501
"""Random-address regression test for pyaffalddk.

Samples a random real address (street, house number, zipcode, city) for
every supported municipality via Klimadatastyrelsens Adressevaelger, then runs it
through the full GarbageCollection chain: address search -> address
lookup -> garbage pull.

Purpose:
1. catch provider/API regressions with fresh, realistic addresses, and
2. surface fractions that fail the SUPPORTED_ITEMS mapping (the
   "Garbage type [...] is not defined" warnings from api.py), aggregated
   per fraction and municipality in a summary at the end, so new
   spellings can be added to const.py.

The seed defaults to today's date (YYYYMMDD), so a failure can be rerun
against the same address with --seed. Municipalities in FIXED_ADDRESSES
(e.g. Odense, which requires per-address online activation) use a pinned
address instead of sampling. Address sampling is live (AV) and
provider endpoints are geo-blocked outside Denmark - run from a server
inside Denmark, like scripts/weekly_api_check.py.

Usage (from the repo root, with the pyaffald env python):
    python scripts/random_regression.py
    python scripts/random_regression.py --progress
    python scripts/random_regression.py --retries 5 --municipalities Aarhus,Kolding
    python scripts/random_regression.py --seed 20260930 --json results.json

Exit code is 1 only on FAIL (an exception on every attempt); a municipality
that resolves but has no pickup data after --retries attempts is a SKIP -
per AGENTS.md that is usually a data-level gap, not an API break.
"""

import argparse
import asyncio
import io
import json
import logging
import random
import re
import sys
import time
import warnings
from datetime import date
from pathlib import Path

import aiohttp

ROOT = Path(__file__).resolve().parent.parent
# Append, not insert: custom_components/affalddk contains calendar.py and
# sensor.py, which would shadow stdlib modules if placed first on sys.path.
sys.path.append(str(ROOT / 'custom_components' / 'affalddk'))

from pyaffalddk.api import GarbageCollection  # noqa: E402
from pyaffalddk.municipalities import MUNICIPALITIES_IDS, MUNICIPALITIES_LIST  # noqa: E402

AV = 'https://adressevaelger.dk'
ATTEMPT_TIMEOUT = 120
DEFAULT_RETRIES = 10
DEFAULT_CONCURRENCY = 5

# Municipalities where a random address is known not to work. Odense
# requires each address to be activated online (recaptcha) before the
# backend serves data, so the regression pins one activated address
# instead of sampling. (zipcode, street, house number, city)
FIXED_ADDRESSES = {
    'Odense': ('5000', 'Flakhaven', '2', 'Odense'),
}

# 'Thy' was the old list name for Thisted (kommunekode 0787). The
# openexplive address search matches on street string + zipcode, so
# addresses sampled from Thisted work for it.
SAMPLING_KODE = {
    'Thisted': '0787',
}

# warn_or_fail() in api.py logs:
#   Garbage type [<name>] is not defined in the system. Please notify the
#   developer. Municipality: <muni>, Address ID: <id>
MISSING_PATTERN = re.compile(
    r'Garbage type \[(?P<name>.+?)\] is not defined.*'
    r'Municipality: (?P<muni>.+), Address ID: (?P<address_id>.+)')


class MissingPrintFilter(io.TextIOBase):
    """Drop the library's raw 'missing: ...' stdout prints.

    api.py prints 'missing: [...]' for unmapped fractions; the same event
    is captured as a warning (with municipality and address id) by
    MissingFractionCapture, so the raw print is pure noise here. A single
    process-wide filter is used instead of redirect_stdout per attempt:
    redirect_stdout swaps the global sys.stdout and restores the wrong
    stream when attempts overlap, swallowing all later output.
    """

    def __init__(self, wrapped):
        """Initialize the filter."""
        self._wrapped = wrapped
        self._drop_next_ws = False

    def write(self, text):
        """Drop any chunk containing a 'missing:' line (incl. its \\n).

        print() writes the trailing newline as a separate chunk, so a
        whitespace-only chunk right after a dropped one is swallowed too.
        """
        if any(line.lstrip().startswith('missing:')
               for line in text.splitlines()):
            self._drop_next_ws = True
            return len(text)
        if self._drop_next_ws and not text.strip():
            self._drop_next_ws = False
            return len(text)
        self._drop_next_ws = False
        return self._wrapped.write(text)

    def flush(self):
        """Flush the wrapped stream."""
        return self._wrapped.flush()


class MissingFractionCapture(logging.Handler):
    """Collect the missing-fraction warnings emitted by api.py."""

    def __init__(self):
        """Initialize the capture."""
        super().__init__()
        # fraction name -> {municipality: set of address_ids}
        self.fractions = {}

    def emit(self, record):
        """Extract fraction, municipality and address id from the warning."""
        match = MISSING_PATTERN.match(record.getMessage())
        if match:
            munis = self.fractions.setdefault(match['name'], {})
            munis.setdefault(match['muni'], set()).add(match['address_id'])


async def dawa_get(session, path, params):
    """GET an address-service endpoint, returning (json-or-None, error-string).

    DAWA (api.dataforsyningen.dk) was retired 2026-10-01. Street sampling
    now goes through Klimadatastyrelsens Adressevælger, which has no
    /vejstykker endpoint; a kommunewide free-text search is used instead.
    """
    try:
        async with session.get(f'{AV}{path}', params=params,
                               timeout=aiohttp.ClientTimeout(total=60)) as resp:
            if resp.status != 200:
                return None, f'AV {path} returned HTTP {resp.status}'
            return await resp.json(content_type=None), None
    except Exception as err:  # noqa: BLE001
        return None, f'AV {path} failed: {type(err).__name__}: {err}'


async def sample_address(session, kode, street, rng):
    """Pick a random address on a street. Returns (address-or-None, reason).

    The house number is a random single digit (1-9); it acts as a wildcard
    in the provider's address search (digit 1 also matches 12 and 188), and
    attempt_address() picks the real address from the provider's response,
    so the sampled address is always one the provider knows.
    """
    data, err = await dawa_get(session, '/adresser/soeg', {
        'vejnavn': street['vejnavn'], 'postnummer': street['postnr'],
        'husnummer': str(rng.randint(1, 9)), 'token': 'adressevaelger123'})
    if err:
        return None, err
    fund = [x for x in data.get('fund', []) if x.get('type') == 'adresse']
    if not fund:
        return None, f"street {street['vejnavn']} has no registered addresses"
    return {'street': street['vejnavn'], 'husnr': str(rng.randint(1, 9)),
            'postnr': street['postnr'], 'city': street['postdistrikt'],
            'digit_search': True}, None


async def attempt_address(prov_session, name, addr, rng):
    """Run one address through the full chain.

    Returns (fractions-or-None, reason, picked-address-or-None). Mirrors
    probe_provider() in scripts/weekly_api_check.py. When
    addr['digit_search'] is set, the house number is a single digit (1-9)
    used as a wildcard: the provider search returns every house on the
    street starting with that digit, and one entry is picked at random, so
    the address is guaranteed to be known to the provider before the
    garbage pull.
    """
    picked = None
    try:
        gc = GarbageCollection(name, session=prov_session, fail=False)
        lst = await asyncio.wait_for(
            gc.get_address_list(addr['postnr'], addr['street'], addr['husnr']),
            ATTEMPT_TIMEOUT)
        if not lst:
            return None, (f"provider list empty for {addr['street']} "
                          f"{addr['husnr']}"), None
        entry = rng.choice(lst) if addr.get('digit_search') else lst[0]
        picked = entry
        address = await asyncio.wait_for(gc.get_address(entry), ATTEMPT_TIMEOUT)
        if address is None:
            return None, 'address lookup returned nothing', picked
        await asyncio.wait_for(gc.init_address(address.address_id), ATTEMPT_TIMEOUT)
        gc.today = None  # force refetch: get_pickup_data caches per day
        data = await asyncio.wait_for(
            gc.get_pickup_data(address.address_id), ATTEMPT_TIMEOUT)
        if not data or 'next_pickup' not in data:
            return None, 'no pickup events returned', picked
        return sorted(key for key in data if key != 'next_pickup'), None, picked
    except asyncio.TimeoutError:
        return None, f'timed out after {ATTEMPT_TIMEOUT}s', picked
    except Exception as err:  # noqa: BLE001
        return None, f'{type(err).__name__}: {err}', picked


async def run_municipality(session, sem, name, kode, args):
    """Sample and test up to args.retries addresses for one municipality."""
    rng = random.Random(f'{args.seed}:{name}')  # noqa: S311 - sampler, not crypto

    async with sem:
        started = time.monotonic()
        fixed = FIXED_ADDRESSES.get(name)
        if fixed is not None:
            zipcode, street, number, city = fixed
            order = []  # pinned address: no street sampling
        else:
            # AV has no street listing; a kommunewide free-text search
            # returns street+postnummer rows (navngivenvejpostnummer) which
            # serve as the street pool.
            streets, err = await dawa_get(
                session, '/adresser/soeg', {'tekst': 'a', 'kommunekode': f'{kode:04d}',
                                            'maksimum': '200', 'token': 'adressevaelger123'})
            if err:
                return {'status': 'FAIL', 'error': err, 'attempts': 0}
            streets = [x for x in streets.get('fund', [])
                       if x.get('type') == 'navngivenvejpostnummer']
            if not streets:
                return {'status': 'SKIP', 'error': 'AV returned no streets',
                        'attempts': 0}

            # Deterministic shuffled order; a street with no addresses just
            # costs one attempt. An empty garbage pull is a data-level gap,
            # so the next attempt samples a *new* street, not a neighbor.
            order = list(streets)
            rng.shuffle(order)

        last_reason = 'not attempted'
        saw_exception = False
        for attempt in range(1, args.retries + 1):
            if fixed is not None:
                addr = {'street': street, 'husnr': number, 'postnr': zipcode,
                        'city': city}
            else:
                street_row = order[(attempt - 1) % len(order)]
                addr, reason = await sample_address(session, kode, street_row, rng)
            if addr is None:
                last_reason = reason
                if args.progress:
                    print(f'[{name} {attempt}/{args.retries}] {reason}', flush=True)
                continue
            if args.progress:
                print(f"[{name} {attempt}/{args.retries}] trying "
                      f"{addr['street']} {addr['husnr']}, {addr['postnr']} "
                      f"{addr['city']}", flush=True)
            # A fresh session per attempt: async_api_request() closes the
            # session it is given when a request fails (interface.py).
            async with aiohttp.ClientSession(trust_env=True) as prov_session:
                fractions, reason, picked = await attempt_address(
                    prov_session, name, addr, rng)
            if fractions is not None:
                addr['picked'] = picked
                return {'status': 'OK', 'address': addr, 'fractions': fractions,
                        'attempts': attempt,
                        'seconds': round(time.monotonic() - started, 1)}
            last_reason = reason
            # Data-level reasons are SKIP material; anything else (timeout,
            # HTTP/API errors) means a possible API break -> FAIL.
            saw_exception = saw_exception or not reason.startswith(
                ('street ', 'address list', 'address lookup', 'no pickup '
                 'events', 'provider list'))
            if args.progress:
                print(f'[{name} {attempt}/{args.retries}] {reason}', flush=True)

    status = 'FAIL' if saw_exception else 'SKIP'
    return {'status': status, 'error': last_reason,
            'attempts': args.retries,
            'seconds': round(time.monotonic() - started, 1)}


def print_summary(results, capture, seed, elapsed):
    """Print the per-municipality results and the missing-fraction summary."""
    print(f'\n=== Random regression summary (seed={seed}, '
          f'{len(results)} municipalities, {elapsed:.0f}s) ===')
    counts = {'OK': 0, 'SKIP': 0, 'FAIL': 0}
    for name in sorted(results):
        res = results[name]
        counts[res['status']] += 1
        if res['status'] == 'OK':
            addr = res['address']
            where = addr.get('picked') or f"{addr['street']} {addr['husnr']}"
            print(f'OK   {name:20} {where}: {len(res["fractions"])} '
                  f'fraction(s) ({res["attempts"]} attempt(s), '
                  f'{res["seconds"]}s)')
        else:
            print(f"{res['status']:4} {name:20} {res['error']} "
                  f"({res['attempts']} attempt(s))")
    print(f'==> {counts["OK"]} OK, {counts["SKIP"]} skipped, '
          f'{counts["FAIL"]} failed')

    print(f'\n=== Missing fractions ({len(capture.fractions)} unique) ===')
    if capture.fractions:
        for fraction, munis in sorted(capture.fractions.items(),
                                      key=lambda kv: (-len(kv[1]), kv[0])):
            print(f'{fraction}  ({len(munis)} municipality(ies))')
            for muni, ids in sorted(munis.items()):
                for address_id in sorted(ids):
                    print(f'     {muni:20} '
                          f'reproduce: '
                          f"{muni} -a '{address_id}'")
        print('Add accepted spellings to SUPPORTED_ITEMS in const.py.')
    else:
        print('No missing fractions detected.')


async def main():
    """Run the random regression."""
    parser = argparse.ArgumentParser(description='Random-address regression test')
    parser.add_argument('--municipalities', default=None,
                        help='comma-separated subset (default: all supported)')
    parser.add_argument('--retries', type=int, default=DEFAULT_RETRIES,
                        help=f'attempts per municipality '
                             f'(default: {DEFAULT_RETRIES})')
    parser.add_argument('--seed', default=f'{date.today():%Y%m%d}',
                        help='rng seed; defaults to today, so failures are '
                             'reproducible with the same address')
    parser.add_argument('--concurrency', type=int, default=DEFAULT_CONCURRENCY,
                        help=f'municipalities tested in parallel '
                             f'(default: {DEFAULT_CONCURRENCY})')
    parser.add_argument('--progress', action='store_true',
                        help='print each attempt as it happens')
    parser.add_argument('--json', default=None, metavar='FILE',
                        help='also write machine-readable results')
    args = parser.parse_args()

    wanted = ([m.strip().lower() for m in args.municipalities.split(',')]
              if args.municipalities else None)
    targets = {name: str(SAMPLING_KODE.get(name)
                         or MUNICIPALITIES_IDS[name.lower()]).zfill(4)
               for name in MUNICIPALITIES_LIST
               if wanted is None or name.lower() in wanted}
    missing = (set(wanted or []) - {n.lower() for n in targets})
    if missing:
        parser.error(f'unknown municipality: {", ".join(sorted(missing))}')

    capture = MissingFractionCapture()
    api_logger = logging.getLogger('pyaffalddk.api')
    api_logger.addHandler(capture)
    api_logger.setLevel(logging.WARNING)
    # Keep the output clean: interface retry chatter is noise here; the
    # missing-fraction warnings are captured. The library closes its session
    # on failed requests (interface.py), which makes aiohttp log
    # "Unclosed client session" through the loop exception handler - drop
    # only those, keep everything else.
    logging.getLogger('pyaffalddk.interface').setLevel(logging.ERROR)
    logging.getLogger('aiohttp').setLevel(logging.ERROR)
    warnings.filterwarnings('ignore', message='^Unclosed')
    # One process-wide filter for the library's raw 'missing:' prints;
    # the structured copy lives in the MissingFractionCapture summary.
    sys.stdout = MissingPrintFilter(sys.stdout)

    loop = asyncio.get_running_loop()
    default_handler = loop.get_exception_handler()

    def exception_handler(inner_loop, context):
        # "Future exception was never retrieved" from the same race: a
        # request still in flight when the library closed the session.
        # Anything else goes to the default handler.
        if 'Unclosed' in str(context.get('message', '')):
            return
        if (context.get('message') == 'Future exception was never retrieved'
                and isinstance(context.get('exception'),
                               aiohttp.ClientConnectionError)):
            return
        if default_handler:
            default_handler(inner_loop, context)
        else:
            inner_loop.default_exception_handler(context)

    loop.set_exception_handler(exception_handler)

    print(f'Random regression: {len(targets)} municipalities, '
          f'seed={args.seed}, retries={args.retries}, '
          f'concurrency={args.concurrency}', flush=True)
    started = time.monotonic()
    sem = asyncio.Semaphore(args.concurrency)
    async with aiohttp.ClientSession(trust_env=True) as session:
        outcomes = await asyncio.gather(*(
            run_municipality(session, sem, name, kode, args)
            for name, kode in sorted(targets.items())))
    results = dict(zip(sorted(targets), outcomes, strict=True))

    print_summary(results, capture, args.seed, time.monotonic() - started)
    if args.json:
        payload = {'seed': args.seed,
                   'results': {name: dict(res, address=res.get('address'))
                               for name, res in results.items()},
                   'missing_fractions': {
                       name: {muni: sorted(ids) for muni, ids in munis.items()}
                       for name, munis in capture.fractions.items()}}
        Path(args.json).write_text(json.dumps(payload, ensure_ascii=False,
                                              indent=1))
        print(f'Results written to {args.json}')

    sys.exit(1 if any(r['status'] == 'FAIL' for r in results.values()) else 0)


if __name__ == '__main__':
    asyncio.run(main())
