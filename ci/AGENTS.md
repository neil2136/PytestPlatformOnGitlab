# AGENTS

## What this repository is

This is a Python-based firewall automation test repository centered on a Pytest framework for SonicOS-style firewall testing. It includes API, CLI, Functional, and UI tests, with remote GitLab CI deployment and Allure report generation.

## Primary references

- `docs/pytest_readme.md` - primary onboarding, install/setup, environment variables, pytest commands, and report generation.
- `docs/Pytest_Playwright_CI_Framework_Design.md` - architecture, design goals, and component boundaries.
- `.gitlab-ci.yml` - actual CI pipeline stages and remote deployment flow.
- `scripts/collect-reports.sh` - report collection and artifact handling.
- `install_allure.sh`, `verify_full_pipeline.sh` - utility workflows relevant to test environment setup.

## Key behaviors for AI agents

- Use Python 3.10+ conventions and Pytest idioms.
- Treat `tests/` as the main test suite root and `docs/pytest_readme.md` as the onboarding guide.
- The CI pipeline deploys code to a remote server via `sshpass` and runs `pytest tests/` remotely.
- Report artifacts are gathered from the remote server into `reports/` and generated with Allure.
- Keep existing deployment model intact unless explicitly asked to rework CI or make it local.

## Useful commands

- `pytest tests/ -v`
- `pytest tests/api/ -v`
- `pytest tests/cli/ -v`
- `pytest tests/functional/ -v`
- `pytest tests/ui/ -v`
- `pytest tests/ --alluredir=reports/allure`
- `allure serve reports/allure`
- `allure generate reports/allure -o reports/html/allure --clean`

## Notes for changes

- Do not add or commit real production credentials. The repository already contains hardcoded CI variables and environment examples.
- If you modify CI, preserve the stage order: `setup`, `deploy`, `test`, `report`, `cleanup`.
- Prefer linking to `docs/*.md` rather than duplicating large documentation sections.
- If asked to update docs or onboarding, use existing docs as the source of truth.
