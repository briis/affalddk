# AGENTS.md — affalddk

Home Assistant custom integration (HACS) that fetches waste pickup data for
Danish municipalities. The core is the standalone library `pyaffalddk`, which
talks to a different backend API per municipality. Codeowners: @briis,
@TermeHansen.

## Commands

```bash
# Tests (no Home Assistant install needed — conftest.py stubs it)
CI=true TZ=Europe/Copenhagen pytest tests --disable-warnings

# Lint (CI runs exactly this)
ruff check --config pyproject.toml

# Live probe of a single municipality (network required)
python scripts/async_test_module.py Aarhus --zipcode 8000 --street Rådhuspladsen --number 2 --pickup
python scripts/async_test_module.py --municipalities   # list municipalities

# Weekly live API check (run from a server inside Denmark — see "CI")
python scripts/weekly_api_check.py [--notify <webhook-url>]
```

Environment: conda env `pyaffald` from `environment.yaml` (python 3.12,
aiohttp, pytest, pytest-asyncio, freezegun, beautifulsoup4, ical, ruff).
Ruff config lives in `pyproject.toml` (`E, F, T, B, S`; `T201`, `S101`,
`E501`, `B006` ignored — prints and asserts are fine here).

## Layout

```
custom_components/affalddk/        The HA integration (HACS payload)
├── __init__.py                    Coordinator (AffaldDKDataUpdateCoordinator)
├── sensor.py / calendar.py        Entities driven by the coordinator
├── config_flow.py                 Address search + municipality setup
├── const.py                       Integration constants + TRANSLATIONS (i18n)
├── i18n/ translations/ images/    UI strings and entity pictures
└── pyaffalddk/                    The standalone library
    ├── api.py                     GarbageCollection orchestrator + APIS map
    ├── interface.py               One class per provider backend
    ├── municipalities.py          Municipality code/name → provider mapping
    ├── const.py                   SUPPORTED_ITEMS, ICON_LIST, NAME_LIST, regexes
    ├── data.py                    PickupEvents, PickupType, AffaldDKAddressInfo
    └── supported_items.json       Serialized SUPPORTED_ITEMS (kept in sync)
tests/
├── conftest.py                    Stubs the homeassistant package (no HA needed)
├── test_api.py                    Unit tests + smoketest (mocked get_garbage_data)
├── test_interface.py              Per-provider tests, LIVE API calls
├── test_calendar.py / test_sensor.py  Entity tests with fixture data
└── data/                          Fixtures: *.data (json/ics), *.p (pickle),
                                   compare_data.p, smoketest_garbage_data.p,
                                   smoketest_fractions.json, const_tests.py
scripts/                           Dev helpers (lint, setup, upgrade, live probe,
                                   weekly_api_check.py — live API check, see "CI",
                                   random_regression.py — random-address sweep)
.github/workflows/                 CI (see "CI" below)
```

## How data flows

`GarbageCollection(municipality)` → looks up the provider in
`MUNICIPALITIES_LIST` (`municipalities.py`), instantiates the matching class
from the `APIS` map in `api.py` → `get_address_list()` / `get_address()` give
an address ID → `get_pickup_data(address_id)` calls the provider's
`get_garbage_data(address_id)`, normalizes rows into `PickupType` events via
`update_pickup_event()` → `set_next_event()` adds the synthetic
`next_pickup` entry.

Fraction names from the APIs are Danish. They are mapped to internal keys by
`get_garbage_types()` in `api.py` using `SUPPORTED_ITEMS` (exact match after
`clean_fraction_string()`), `SPECIAL_MATERIALS`, and `NON_SUPPORTED_ITEMS`.
Unknown fractions print `missing: ...` and warn — or raise when the
`GarbageCollection` was created with `fail=True`. When a provider renames a
fraction, add the new spelling to `SUPPORTED_ITEMS` in `const.py` (and to
`tests/data/const_tests.py` if it fits a category).

## Testing model — read before touching tests

- `tests/test_interface.py` hits **live APIs** (adressevaelger.dk plus each
  municipality's backend). It needs network; failures can be real API changes,
  not code bugs. **Several municipality endpoints are geo-blocked outside
  Denmark** and hang (until timeout) from foreign runners — that is why the
  weekly API check is a local script (`scripts/weekly_api_check.py`), not a
  GitHub Actions job.
- Results are compared against pickled baselines with
  `update_and_compare(name, data, UPDATE)`. To refresh a baseline, set
  `UPDATE = True` at the top of the file, run once, set it back to `False`,
  and commit the regenerated `tests/data/compare_data.p`.
- `get_garbage_data` is monkeypatched with fixture data in every test; the
  live calls are the address-list/address lookups. Live garbage-data pulls
  are not part of the test suite — they live in
  `scripts/weekly_api_check.py` (see below). Only the VestFor address block
  is additionally gated on `CI=true` (`if not CI:` in `test_interface.py`;
  `skip_in_ci` is defined there but currently unused).
- Tests use `freeze_time` with hardcoded dates; baselines are only valid at
  those dates. Keep the freeze date when editing a test.
- `test_api.py` rewrites `supported_items.json` (sorted) at import time — a
  dirty diff on that file after a test run is normal; only commit it if the
  content actually changed.
- `tests/conftest.py` injects a minimal fake `homeassistant` package. If a
  new HA import is needed by the integration, extend the stub there instead
  of adding HA as a test dependency.

## Adding a municipality or provider

1. Municipality on an existing provider: add the kode to the `data` string and
   an entry to `MUNICIPALITIES_LIST` in `municipalities.py`. Providers with an
   extra ID (e.g. affaldonline) take `[provider, id]`.
2. New provider backend: add a class in `interface.py` (subclass
   `AffaldDKAPIBase`, implement `get_address_list`, optional `get_address`,
   `get_garbage_data`), register it in the `APIS` map in `api.py`, and add a
   parsing branch in `GarbageCollection.get_pickup_data()`.
3. Save a real response as `tests/data/<name>.data`, add a
   `test_<Provider>` in `test_interface.py` following the existing pattern
   (freeze time, mock `get_garbage_data`, `update_and_compare`), and add the
   smoketest entry via `scripts/async_test_module.py --smoketest <name>` if
   needed.

## Provider churn (why tests fail without code changes)

**DAWA retired 2026-10-01.** `api.dataforsyningen.dk` (DAWA) was shut down by
Klimadatastyrelsen; address search and lookups now go through
Klimadatastyrelsen's **Adressevælger** (`adressevaelger.dk`, public demo
token, see `AV_*` constants in `pyaffalddk/const.py`). Its search is
relevance-based (not exhaustive like DAWA) and caps at 200 hits. The
Datafordeleren DAR GraphQL API (`graphql.datafordeler.dk/DAR/v3`) needs a
user API key and is deliberately not used. `dawa.companydata.dk` is a
third-party DAWA-compatible mirror used only for `kommuner/reverse` in the
config flow.

Municipalities change backends regularly. Recent examples: Aarhus
(kredslob.dk) stopped accepting kvhx-style address IDs
(`07517005___1__2____`) and now requires the DAR UUID from
adressevaelger.dk — fixed by dropping the `get_address` override so the base
class returns the UUID. When a provider breaks: curl the endpoint, compare
the response shape against the parsing branch, check whether the *address ID
format* or the *payload* changed. `get_kvhx` is still used by RenoSyd — do
not remove it. Also note: an address resolving but returning no data (empty
standpladser, no containers) is usually a data-level gap, not an API break —
probe neighboring addresses before concluding the API changed.

## CI

- `python-testing.yml` — on push to main and PRs: ruff, then pytest with
  `CI=true` under both `TZ=UTC` and `TZ=Europe/Copenhagen` (timezone matters:
  pickup-date logic uses local dates). Runs the mocked data tests plus the
  live address lookups; no live garbage-data probes (geo-blocked).
- `release.yml` — on release publish: bumps `manifest.json` version via yq
  and uploads the zipped component. Version lives in
  `custom_components/affalddk/manifest.json`; tags look like `v3.5.0`;
  document user-facing changes in `CHANGELOG.md`.

## Weekly API check (local, not CI)

`scripts/weekly_api_check.py` replaces the retired GitHub Actions scheduled
job: GitHub runners cannot reach the geo-blocked endpoints. Run it from a
server inside Denmark:

```bash
python scripts/weekly_api_check.py                    # probes only (pytest skipped)
python scripts/weekly_api_check.py --with-pytest      # probes + interface tests
python scripts/weekly_api_check.py --notify <url>     # POST summary to ntfy/webhook
python scripts/weekly_api_check.py --progress         # live progress for probes/pytest
python scripts/weekly_api_check.py --skip-probes      # interface tests only
```

It runs `tests/test_interface.py` in a subprocess (live address lookups,
mocked garbage data) when `--with-pytest` is passed — pytest is skipped by
default — and then probes five providers with a real address
search + garbage pull: `aarhus` (whose test is fixture-only) plus the four
that have no interface test (`renosyd`, `ikastbrande`, `affaldonlineweb`,
`kolding`). Exit code is 1 on failure, so cron mail works; `--notify`
POSTs a plain-text summary (ntfy.sh style). `--progress` streams the pytest
output live and prints each probe as it starts. Probe addresses live in
`PROBE_ADDRESSES` at the top of the script — update them if an address
loses service. The script imports `pyaffalddk` with `sys.path.append` (not
insert): `custom_components/affalddk/calendar.py` would otherwise shadow
the stdlib `calendar` module.

## Random-address regression (local, not CI)

`scripts/random_regression.py` samples a random real address per
municipality from adressevaelger.dk (a kommunewide free-text search for a
seeded-random street), then lets the *provider's* address search pick the house: a
random single digit (1–9) is passed as the house number, which the
provider searches treat as a wildcard (1 also matches 12 and 188), and a
random entry from the returned list is used — so the address is always
one the provider knows. It then runs the full `GarbageCollection` chain
on it. Seed defaults to today's date, so a failure reruns against the
same address with `--seed`. It aggregates the `Garbage type [...] is not
defined` warnings from `api.py` into a missing-fraction summary at the
end — those spellings are candidates for `SUPPORTED_ITEMS` in
`const.py`. Municipalities in `FIXED_ADDRESSES` (Odense: needs
per-address online activation) use a pinned address; `SAMPLING_KODE` maps names without a `MUNICIPALITIES_IDS` entry (Thy →
Thisted 0787). Resolving but empty pulls are SKIP (data-level gap,
resample a new street); exceptions on every attempt are FAIL (exit 1).
The missing-fraction summary prints each fraction's municipality and
address ID plus a ready-made reproduce command
(`python scripts/async_test_module.py <muni> -a '<address_id>'`) for
pulling that address live and capturing it as a smoketest fixture.
Geo-blocked endpoints: run from inside Denmark, like the weekly check.

```bash
python scripts/random_regression.py                       # all municipalities
python scripts/random_regression.py --progress            # per-attempt output
python scripts/random_regression.py --retries 5           # fewer attempts
python scripts/random_regression.py --municipalities Aarhus,Kolding
python scripts/random_regression.py --seed 20260930       # rerun a failure
python scripts/random_regression.py --json results.json   # machine-readable
```

## Conventions

- Danish text (addresses, fraction names, comments in fixtures) is UTF-8;
  keep it that way, including in test data.
- The integration and the library must stay decoupled: `pyaffalddk` must not
  import `homeassistant`. Entities translate internal keys via `NAME_LIST` /
  `TRANSLATIONS`; `test_waste_name_keys_match_name_list` enforces that every
  waste key exists in every language — update all languages when adding keys.
- Entity pictures are SVGs under `custom_components/affalddk/images`, served
  as `/affalddk/img/<key>.svg`; icon keys come from `ICON_LIST`.
