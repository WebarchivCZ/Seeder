# Repository Guidelines

## Project Structure & Module Organization
Core Django project code lives in `Seeder/`. App modules are split by domain (`source/`, `harvests/`, `contracts/`, `blacklists/`, `comments/`, `www/`, etc.), each with models, views, forms, migrations, and app-local templates where needed. Shared templates and static assets are in `Seeder/templates/` and `Seeder/static/`. Environment-specific settings are in `Seeder/settings/` (`base.py`, `env.py`, `tests.py`). Infrastructure and deployment files are at the repo root (`docker-compose.yml`, `Dockerfile`, `Jenkinsfile`) and `ci/`.

## Build, Test, and Development Commands
- `docker-compose up`: start the full local stack (web, postgres, memcached, proxies).
- `./local`: reset `web`/`static` containers and static volume, then start in background.
- `./drun migrate`: run Django management commands in Docker (`./drun <command>`).
- `./drun --run test --settings=settings.tests`: run test suite in an isolated run container.
- `coverage run --source=Seeder Seeder/manage.py test --settings=settings.tests`: CI-style coverage run (same as `.travis.yml`).
- `make -C docs html`: build Sphinx documentation into `docs/_build/`.

## Coding Style & Naming Conventions
Use Python 3 + Django conventions with 4-space indentation and PEP 8-compatible formatting. Follow existing naming patterns: `snake_case` for functions/variables, `CamelCase` for classes, and descriptive app/module names by domain. Keep business logic in app modules rather than templates. Migration files should be auto-generated and committed with model changes.

## Testing Guidelines
Tests are primarily Django `manage.py test` tests, located in app-level files such as `Seeder/source/tests.py` and `Seeder/harvests/tests.py`. Add or update tests for behavior changes and regressions. For DB-sensitive logic, run with `--settings=settings.tests` (SQLite test settings) to match CI expectations.

## Commit & Pull Request Guidelines
Recent history favors short, imperative commit messages, often with issue references (for example: `#710: fix slug creation...`). Keep commits focused and include migrations with schema changes. PRs should include: purpose/scope, linked issue, deployment notes (if any), and screenshots for UI/template changes. Target `master` for development work; `production` is release-focused.

## Security & Configuration Tips
Do not commit secrets. Keep local overrides in environment variables or local settings files derived from `Seeder/settings/local_settings.template.py`. Treat `ci/group_vars/*/vault.yaml` and runtime `.cronenv` content as sensitive.
