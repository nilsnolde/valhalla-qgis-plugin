# CLAUDE.md

Notes for future Claude sessions working in this repo. Keep terse and current — update when assumptions change.

## What this is

QGIS plugin for the [Valhalla routing engine](https://github.com/valhalla/valhalla). Provides routing, isochrones, matrix, map-match, elevation, expansion, and TSP — both as interactive map tools and Processing algorithms — for car/bike/pedestrian/truck/motorbike profiles. Talks to remote Valhalla HTTP servers (FOSSGIS public, custom URLs) or runs Valhalla locally via the [`pyvalhalla`](https://pypi.org/project/pyvalhalla/) Python package (Linux/macOS only — Windows is HTTP-only).

## Branches & QGIS/PyQt strategy

- **`master`**: development branch for QGIS 4.x / PyQt6. **This is where new work lives.**
- **`qgis-v3`**: maintenance branch for QGIS 3.x / PyQt5.
- (`qgis-v4` may exist transiently as a working branch before merging into master — treat `master` as canonical going forward.)
- `metadata.txt` on the v4 line declares `qgisMinimumVersion=4.0`, `qgisMaximumVersion=4.99`, `version=5.0.0`.
- The `qgis.PyQt.*` compatibility layer (provided by QGIS) abstracts most PyQt version differences, but **not all**: enum scoping (`Qt.LeftButton` vs `Qt.MouseButton.LeftButton`), `QFileSystemModel` location (QtWidgets in PyQt5 → QtGui in PyQt6), `QFileDialog` option flags, etc.

## Repository layout

```
valhalla/                       # plugin source root (this is what gets shipped)
├── __init__.py                 # classFactory(iface) entry point
├── plugin.py                   # ValhallaPlugin: initGui/unload, registers provider + dock
├── metadata.txt                # QGIS plugin manifest
├── global_definitions.py       # RouterType / RouterMethod / RouterProfile / RouterEndpoint enums
├── core/
│   ├── router_factory.py       # builds router instances
│   ├── http/router_client.py   # async HTTP via QgsNetworkAccessManager; sets X-Client-Id
│   ├── results_factory.py      # parses Valhalla responses into QGIS layers
│   └── settings.py             # ValhallaSettings (QSettings-backed)
├── gui/
│   ├── dock_routing.py         # RoutingDockWidget — main interactive UI
│   ├── widgets/                # router widget, waypoints, costing settings, graphs widget
│   ├── compiled/*_ui.py        # GENERATED from resources/ui/*.ui — do not hand-edit
│   └── dlg_*.py                # dialogs (settings, providers, server log, …)
├── processing/
│   ├── provider.py             # ValhallaProvider (Processing algorithms registry)
│   └── routing/, spatial_optimization/, …
├── resources/
│   ├── ui/*.ui                 # Qt Designer XML — source of truth for compiled UIs
│   └── icons/
├── utils/                      # geom, http, layer, logger, qt, resource helpers
└── third_party/routingpy/      # vendored routing client lib (do not modify directly)

tests/
├── __init__.py                 # LocalhostDockerTestCase / LocalhostPluginTestCase base classes
├── qgis_interface.py           # mock QgisInterface for headless testing
├── test_localhost_docker/      # tests against external Valhalla on localhost:8002
├── test_localhost_plugin/      # tests using bundled pyvalhalla
└── scripts/qgis_test_setup.sh  # CI bootstrapping inside QGIS docker images

scripts/
├── compile_ui.sh               # pyuic6 over resources/ui/*.ui → gui/compiled/*_ui.py
└── pyqt5_to_pyqt6.py           # QGIS official 3to4.py migration script (one-shot use)

.github/workflows/
├── ci-tests.yml                # QGIS 4.x release tests (matrix: qgis_tags: [4.0.1])
├── ci-tests-v3.yml             # QGIS 3.44.10 tests — slated for removal when v3 dropped
└── ci-tests-latest.yml         # QGIS master nightly
```

## How the plugin loads

1. QGIS calls `valhalla/__init__.py:classFactory(iface)` → returns `ValhallaPlugin(iface)`.
2. `ValhallaPlugin.__init__` instantiates `ValhallaProvider`, which constructs every Processing algorithm class (this is where import-time errors surface — see traceback chain in `processing/provider.py:62`).
3. `ValhallaPlugin.initGui()` registers the Processing provider, builds the toolbar, and creates the `RoutingDockWidget`.

## UI compilation

`.ui` files (Qt Designer XML) live under `valhalla/resources/ui/`. They're compiled into Python with `pyuic6` via `scripts/compile_ui.sh`, output to `valhalla/gui/compiled/*_ui.py`.

- **Never hand-edit** `valhalla/gui/compiled/*_ui.py` — they're regenerated.
- After editing any `.ui`, re-run `bash scripts/compile_ui.sh`.
- Older `.ui` files may use unscoped Qt6 enum syntax (e.g. `QFileDialog::DontResolveSymlinks`); pyuic6 won't fix this for you. Update the `.ui` to use scoped form (`QFileDialog::Option::DontResolveSymlinks`) and recompile.

## Test setup

Two flavors, intentionally exclusive (one or the other, never both):

```shell
# Docker-backed: needs `docker run -p 8002:8002 ghcr.io/valhalla/valhalla-scripted:latest`
# pyvalhalla MUST be uninstalled (rm -r ~/.local/share/QGIS/QGIS4/profiles/default/valhalla/pyvalhalla)
QT_QPA_PLATFORM=offscreen python -m coverage run --append -m unittest discover -s tests/test_localhost_docker -t .

# Plugin-managed: stops docker, downloads & installs pyvalhalla itself
QT_QPA_PLATFORM=offscreen python -m coverage run --append -m unittest discover -s tests/test_localhost_plugin -t .
```

CI runs both inside QGIS docker images; see `.github/workflows/ci-tests.yml`.

## Known PyQt6 gotchas (already hit during the v4 port)

These will keep biting — check first when something breaks after touching v4 code:

1. **Enum scoping.** PyQt6 requires fully scoped enum access. `Qt.LeftButton` → `Qt.MouseButton.LeftButton`; `QDialogButtonBox.Ok` → `QDialogButtonBox.StandardButton.Ok`; `QDir.Dirs` → `QDir.Filter.Dirs`. The compiled UI files were regenerated with `pyuic6` to handle this for generated code — but hand-written code (especially `tests/`) still needs manual fixes.
2. **Class relocations.** `QFileSystemModel` moved from `QtWidgets` to `QtGui`. `QAction` moved from `QtWidgets` to `QtGui`. `QRegExp` removed → use `QRegularExpression`.
3. **`QSortFilterProxyModel` + `QFileSystemModel` is brittle in Qt6.** `proxy.mapFromSource(idx)` walks the source index's parent chain; `QFileSystemModel` only fetches children of `setRootPath`, never the ancestor chain. Result: `mapFromSource` returns invalid even when `model.index(path)` is valid. Fix used in this repo: drop the proxy, use `QFileSystemWatcher` + `QStringListModel` populated from `iterdir()` (see `widget_router.py` and `widget_graphs.py`).
4. **Stale `.pyc`.** When refactoring imports, clear `__pycache__/` — Python's mtime-based invalidation can lag and produce confusing tracebacks referring to old import statements.

## Coding conventions

- Black, line length 105. isort with black profile. `pyproject.toml` excludes `compiled/`, `third_party/`, and a few entry-point files.
- Tests under `tests/test_localhost_docker/test_processing/test_spatial_optimization/UNUSED_*.py` are deliberately skipped (filename prefix).
- Don't modify `valhalla/third_party/routingpy/` — it's vendored. The plugin overrides what it needs via subclassing in `valhalla/core/`.

---

# Dev workflow

## When working on `master` (QGIS v4) together

**Mandatory reminder to the user (the user explicitly asked for this):** they cannot test PyQt5/QGIS3 locally and rely on CI for the `qgis-v3` branch. So:

> **Whenever we change something on `master`, I should remind the user to also apply the equivalent change to `qgis-v3`.** This applies to bug fixes, new features, and behavior changes — not to PyQt6-specific syntax migrations (those are by definition v4-only). When unsure whether a change is PyQt6-specific or general, mention it explicitly so the user can decide.

How to phrase the reminder: at the end of a change session, in one sentence. Example: *"FYI — this change is logic, not PyQt6-specific. Worth porting to `qgis-v3` so CI doesn't drift."*

## Keeping this file current

After any significant change to the repo — new architectural decisions, new gotchas hit, branch-strategy shifts, conventions adopted, files moved — update CLAUDE.md in the same change. Stale notes are worse than no notes; if the reader can't trust this file, they'll re-derive everything anyway. Specifically:

- New PyQt6 gotcha → add to the "Known PyQt6 gotchas" section.
- New top-level directory or significant file move → update the layout tree.
- Change to test commands, CI, or branch model → update the corresponding section.
- Convention or workflow we agreed on in conversation → write it down here, not just in memory.

Don't pad with trivia (file-by-file changelogs, one-off bugs we already fixed). The bar is: *would a future agent waste time without this?*

## Quick commands

```shell
# Recompile UI after .ui edit
bash scripts/compile_ui.sh

# Clear stale bytecode (do this any time you refactor imports)
find tests valhalla -type d -name __pycache__ -exec rm -rf {} +

# Format / lint
black valhalla tests
isort valhalla tests
pre-commit run --all-files
```

## Backporting a change to `qgis-v3`

The two branches share most code. Typical flow when something needs to land on both:

```shell
git checkout qgis-v3
git cherry-pick <commit-on-master>
# resolve any PyQt6 vs PyQt5 enum/import conflicts manually
git push origin qgis-v3
```

CI on the v3 branch (via `ci-tests-v3.yml`) will validate. Don't promise the user it works on QGIS 3 without seeing the CI green tick.
