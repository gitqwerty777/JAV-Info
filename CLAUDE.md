# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CLI tool that renames local video files by their JAV bangou (unique ID) and can download album/thumbnail images. It scrapes metadata from javlibrary and javdb.

## Run

```
poetry install          # first time / after dependency changes
poetry run python main.py
```

Dependencies are managed with Poetry (`pyproject.toml` + `poetry.lock`); there is no `requirements.txt`. `package-mode = false` — this is an application, not an installable library, so `poetry install` sets up the venv without trying to build a package.

Requires first-time setup (see README for full detail):
- Copy `config-template.json` to `config.json` (the app reads `config.json`; it is gitignored).
- Put a matching-version `ChromeDriver.exe` on `PATH` — scraping uses headless Selenium Chrome.
- Provide logged-in cookie files for javlibrary/javdb at the paths named in `config.json`.

`dryRun: true` in `config.json` is the safe default — it plans renames without touching files. Running with `dryRun: false` prompts for confirmation before executing.

## Architecture

`main.py` wires together single-responsibility modules and runs the pipeline:
- `Setting.py` — loads `config.json` into a `Setting` object.
- `FileNameParser.py` — scans `fileDirs`, parses bangou from filenames (skips files under `minFileSizeMB`, drops `ignoreWords`).
- `JAVInfoGetter.py` — `JAVInfoGetter_javlibrary` and `JAVInfoGetter_javdb` fetch metadata; tried in order, first complete result wins.
- `webpage_getter.py` — `WebPageGetter` Selenium/BeautifulSoup base for the getters.
- `DataManager.py` — caches queries (including failures) to `db-{language}.json` so re-runs don't re-scrape.
- `Executor.py` — performs the actual rename / image downloads.

## Conventions

- Public methods use PascalCase (`GetInfo`, `HandleFiles`, `GetFiles`, `AddRecord`, `Save`); variables and functions are camelCase. This is not PEP 8 — match the existing style rather than "correcting" it.
- Formatter is autopep8 (in `requirements.txt`).
- User-facing output goes through `utils.py` helpers (e.g. `utils.logError`, `utils.yellowStr`) which use colorama.

## Gotchas

- The database persists failed lookups too — if data comes back wrong, clear or edit `db-{language}.json` (or set `retryFailedDB`) rather than assuming a code bug.
- A file's **name** must contain the bangou or it cannot be renamed.
- `venv/` is committed to the repo but not in `.gitignore`; ignore it when searching, and don't treat its contents as project code.
