# scripts

Dev helpers for `pyaffalddk`. All of them import the library directly from
`custom_components/affalddk/pyaffalddk`, so **run them from the repo root**
(several also read `tests/data/...` with relative paths).

| Script | What it does |
| -- | -- |
| `async_test_module.py` | Live probe of one municipality: address search, address lookup, pickup pull. Also adds/removes smoketest fixtures. |
| `weekly_api_check.py` | Live API check for providers without an interface test (plus Aarhus). Cron-friendly, exit code 1 on failure. |
| `random_regression.py` | Samples a random real address per municipality and runs the full chain; aggregates unmapped fractions. |

`weekly_api_check.py` and `random_regression.py` hit municipality endpoints
that are **geo-blocked outside Denmark** and will hang until timeout from a
foreign runner. Run them from a server inside Denmark.

## 1. Set up the environment

Dependencies are declared in `pyproject.toml` (python 3.12; runtime deps
`aiohttp`, `beautifulsoup4`, `ical`; dev deps `pytest`, `pytest-asyncio`,
`freezegun`, `ruff`, `requests`). Pick either tool below.

### Option A — uv (recommended, used by CI)

```bash
# from the repo root
uv sync          # creates .venv and installs runtime + dev deps from uv.lock
uv run python scripts/async_test_module.py --municipalities
```

`uv sync` installs project deps plus the `dev` group. Prefix commands with
`uv run` (no activation needed), or `source .venv/bin/activate` and use
`python` directly. Use `uv sync --no-dev` for runtime deps only.

### Option B — miniforge / mamba (standalone conda env)

`scripts/conda_env.yaml` is a self-contained conda environment (it lists the
same packages, so it needs no `pyproject.toml`):

```bash
# from the repo root
mamba env create -f scripts/conda_env.yaml   # creates the "pyaffald" env
mamba activate pyaffald
```

`conda env create -f scripts/conda_env.yaml` works too; `mamba` just solves
faster. To recreate after a change: `mamba env remove -n pyaffald` then create
again, or `mamba env update -f scripts/conda_env.yaml --prune`.

## 2. Run the scripts

```bash
# list every supported municipality
python scripts/async_test_module.py --municipalities

# probe one address live: address search + pickups
python scripts/async_test_module.py Aarhus --zipcode 8000 --street Rådhuspladsen --number 2 --pickup

# probe by an address id you already have
python scripts/async_test_module.py Kolding -a '<address_id>' --pickup

# capture the live response of an address as a smoketest fixture
python scripts/async_test_module.py Aarhus --zipcode 8000 --street Rådhuspladsen --number 2 \
    --smoketest my_fixture          # add --force to overwrite, --delete to remove
```

```bash
# weekly API check (run from inside Denmark)
python scripts/weekly_api_check.py                    # probes only (pytest skipped)
python scripts/weekly_api_check.py --with-pytest      # probes + tests/test_interface.py
python scripts/weekly_api_check.py --notify <url>     # POST summary to ntfy/webhook
python scripts/weekly_api_check.py --progress         # stream live output
python scripts/weekly_api_check.py --skip-probes      # interface tests only
```

```bash
# random-address regression (run from inside Denmark)
python scripts/random_regression.py                       # all municipalities
python scripts/random_regression.py --progress            # per-attempt output
python scripts/random_regression.py --retries 5           # fewer attempts
python scripts/random_regression.py --municipalities Aarhus,Kolding
python scripts/random_regression.py --seed 20260930       # rerun a failure
python scripts/random_regression.py --json results.json   # machine-readable results
```

Every script accepts `--help`. See `AGENTS.md` for the test suite, the
weekly-check cron example, and how to add a municipality or provider.
