# AI Agent Guide for this Repository

This repository is a pytest-based automation framework for firewall testing. The key goal of this file is to help AI coding agents understand the project structure, common workflows, and where to find authoritative documentation.

## What this repository contains

- `src/`: framework core implementation
  - `src/core/utils/`: utility classes for config, API/CLI clients, logging
  - `src/firewall/`: SonicOS-specific firewall client code
- `tests/`: Pytest test suites
  - `tests/api/`, `tests/cli/`, `tests/functional/`, `tests/ui/`
  - each test directory includes a `bin/` folder for shared helper code and a `testplan/` folder for test plan assets
- `skills/`: automation skill modules
- `reports/`: generated Allure and HTML reports
- `conftest.py`: project fixtures and Pytest hooks
- `pytest.ini`: Pytest settings and marker definitions
- `requirements.txt`: pinned Python dependencies
- `.env`: environment variables for firewall connection and test environment
- `QUICK_SETUP.sh`: quick deployment script

## Important conventions

- Test file naming: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Pytest markers are defined in `pytest.ini` and also auto-added by path in `conftest.py`
- The repository adds `src/` to `sys.path` in `conftest.py`
- Configuration is loaded from `.env` via `python-dotenv` and exposed through `src.core.utils.config.Config`
- Do not hardcode firewall credentials or environment-specific connection details in code; use `.env`

## Typical developer workflows

- Setup:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - `playwright install chromium`
  - `playwright install-deps chromium`
- Run all tests:
  - `pytest tests/ -v`
- Run a specific layer:
  - `pytest tests/api/ -v`
  - `pytest tests/cli/ -v`
  - `pytest tests/functional/ -v`
  - `pytest tests/ui/ -v`
- Generate reports:
  - `pytest tests/ --alluredir=reports/allure`
  - `allure serve reports/allure`
  - `allure generate reports/allure -o reports/html/allure --clean`

## What agents should know first

- This is a test automation repository rather than a production application.
- Most work is around test case design, fixture reuse, test environment configuration, and test reporting.
- The UI tests use Playwright; API/CLI/functional tests are implemented with Pytest and custom firewall clients.
- `doc/DEPLOYMENT_GUIDE.md` and `doc/Pytest_Playwright_CI_Framework_Design.md` contain higher-level architecture and CI design guidance.

## Useful reference files

- `README.md` — project overview, setup, and test commands
- `conftest.py` — global fixtures and Pytest hook behavior
- `pytest.ini` — marker and environment defaults
- `requirements.txt` — dependency versions
- `doc/DEPLOYMENT_GUIDE.md` — deployment and environment setup
- `doc/Pytest_Playwright_CI_Framework_Design.md` — framework design and CI expectations

## When to ask for more context

- If changes affect real firewall connectivity or test environment setup
- If new test types are added beyond API/CLI/functional/UI
- If environment variables or test topology handling need to change

> Do not modify production firewall credentials in code. Keep secrets in `.env` and only edit `.env` locally for environment-specific runs.
