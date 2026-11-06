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

These conventions apply to new work, including bug fixes. Preserve existing historical names; do not rename unrelated branches.

- Start each delivery item from `master`, after checking the working tree and base revision. Use one branch and one PR per item. The agreed combined #728 + #735 package may share one branch/PR, with both issues listed in its description.
- Name branches `feature/#<issue>_<shortDescription>`: ASCII without spaces or diacritics, with a concise `lowerCamelCase` description. Examples: `feature/#731_referencniCentrum`, `feature/#712_addSeederUrl`. For a combined item, use the first issue in the branch name and list all issues in the PR. Use `feature/` for bug fixes too; `feat/` does not match the configured Jenkins test-deployment patterns.
- Write commit subjects in English as `#<issue>: <imperative description>`, for example `#731: Centralize and fix reference centre links`. Keep each commit focused; use an optional body to explain the reason or a material trade-off. Include generated migrations with model changes. Do not mix unrelated fixes or commit secrets/generated runtime files.
- Use the same issue prefix and concise English description for the PR title, for example `#731: Fix reference centre links`. Target `master`; production releases use `production` and are coordinated with the client.
- Write the PR description in English for a reviewer who has not seen the chat: explain the concrete problem and resulting behavior, link every relevant issue, summarize the final scope, and list actual validation commands/results and any remaining failures. Include screenshots for UI/template changes and deployment requirements (migrations, environment variables, other operational steps), or explicitly state when none are required. Distinguish local verification from client test acceptance and production verification.
- Keep the title and description aligned with the final diff. Use `Closes #<issue>` only when merging the PR should close that issue; otherwise use a plain issue reference. Never claim tests, client acceptance or deployment that have not happened.

Recommended PR body:

```markdown
<Problem and resulting behavior. Issue link/reference.>

## Changes
- <Relevant change and purpose.>

## Validation
- `<exact command>` — <actual result; disclose remaining failures.>
- <Manual/browser checks and screenshots for each affected language.>

## Deployment
<Required steps, or "No migrations or new environment variables required.">
<Client test acceptance / production status when relevant.>
```

## Test Deployment

- A push to `feature/*` or `master` (including a PR merge into `master`) triggers the build and deployment to the shared test environment. Treat each such push as a test deployment. The pipeline also accepts `feature-*`, but use `feature/` for new branches.
- Before reporting deployment as complete, verify that the build and `Deploy to test` stages actually ran for the intended commit and verify the deployed revision in the test environment. A green status alone is insufficient because stages can be skipped.
- The `production` branch also deploys to test; its subsequent production deployment requires manual approval in Jenkins and coordination with the client.

Verified on 2026-11-07 against [Jenkinsfile](Jenkinsfile) and the [maintainer's clarification in PR #741](https://github.com/WebarchivCZ/Seeder/pull/741#issuecomment-6685547289).

## Security & Configuration Tips
Do not commit secrets. Keep local overrides in environment variables or local settings files derived from `Seeder/settings/local_settings.template.py`. Treat `ci/group_vars/*/vault.yaml` and runtime `.cronenv` content as sensitive.
