# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Workflow

**IMPORTANT: Claude should NEVER commit or push git changes directly.** Make the changes, stage them with `git add`, and stop. The user reviews and commits.

## Documentation Practices

Put planning documents, analysis notes, and support scripts for Claude in `claude_notes/`, and save substantial planning or analysis work there as markdown for future sessions. The `.md` files are the authority; any `.html` there is generated for display, so ignore it and don't add it to git. `claude_notes/emit_migration_plan.md` tracks the move to the layout used by `../ecostress-level1`, `../geocal-repo` and `../framework`.

Related repositories (siblings of this one, each with its own CLAUDE.md): `../geocal-repo` (GeoCal, which this builds on), `../ecostress-level1` (closest template: same autotools + pixi + SWIG layout), `../framework`.

## What this is

EMIT / AVIRIS-NG Level 1B geolocation (emit-sds-l1b-geo), built on JPL's GeoCal library. Pipeline: raw + GPS/PPS -> orbit/time table (L1A orbit stage) -> image-ground connection (IGC) and projection -> tiepointing/matching and exterior orientation correction -> LOC/IGM/OBS (GLT still pending) output files. See `README.md` for the full run instructions and test data locations.

## Build / install

Autotools project layered on a [pixi](https://pixi.sh) environment (`env/`, as in ecostress-level1) that provides GeoCal, AFIDS and the compilers. `README.md` still describes the older conda-based flow.

```
cd env && make create-env          # ENV_DIR default ../../emit-build/build-pixi; override in env/Makefile.local
cd <ENV_DIR> && pixi shell
./configure --prefix=$CONDA_PREFIX --with-test-data=<path> --enable-maintainer-mode   # or the pixi tasks: configure, build, install-editmode
```

`env/linux/pixi.toml` has no committed `pixi.lock` yet (`PIXI_LOCKED=no`); after the first working env run `make update-lock` in `env/`. Generic flow once configured:

```
./configure --prefix=$INSTALL_DIR --with-test-data=<path to test data>
make -j 20 all && make install && make -j 20 check && make -j 20 installcheck
source $INSTALL_DIR/setup_emit.sh     # needed before running tools or tests
```

- `make install` also pip-installs `python/` into the prefix (`python/python.am`); `make installcheck` runs the Python test suite. `make check` runs C++ tests.
- `make end-to-end-aviris-ng-check` runs the end-to-end AVIRIS-NG test.
- The top-level Makefile.am just includes `include.am`, which lists the sub-`.am` files (lib, python, bindings/python, unit_test_data, script, l1b_geo).
- `configure`, `Makefile.in`, and the SWIG `*_wrap.cc` in `bindings/python/swig` are generated.

## Python (in `python/`)

`python/Makefile` is a developer convenience Makefile (separate from autotools):

- `make install` — editable pip install into `$(EMITTOP)`; `make install2` non-editable
- `make check` — `pytest -n 10 tests`
- `./test.sh tests/unit/emit_igc_test.py -k name` runs a single test (puts `python/` on PYTHONPATH). Always give it a test path.
- Long tests are skipped unless `--run-long` is given (marker `long_test`). pytest uses `--basetemp=./pytest_tmp` (large temp data; untracked).
- `make lint` / `make format` use ruff. Per `README_developer.md`, lint/format cleanliness is a convenience, not a requirement; silence false positives via per-file ignores in `pyproject.toml`. Static typing is deliberately not pursued in general, though `make mypy` exists.

## Architecture

- `lib/` — C++ (classes such as `emit_orbit`, `emit_igc_collection`, `reverse_camera`, `resampler`, `camera_paraxial`, `emit_obs_calc`), each wrapped for Python with a SWIG `.i` file. Generated wrappers land in `bindings/python/swig`, with the swig support in `bindings/python`. Changing a `.cc/.h/.i` requires rebuilding via make before Python sees it.
- `python/emit/` — the Python package (`import emit`). Mixes both instruments:
  - EMIT: `emit_orbit_extension`, `emit_time_table`, `emit_camera`, `emit_igc`, `emit_loc/obs/glt`.
  - AVIRIS-NG: `aviris_ng_raw`, `aviris_ng_orbit`, `aviris_ng_time_table`, `aviris_ng_loc/igm/obs/glt`, plus `aviris_*` for classic AVIRIS.
  - Shared: `l1b_proj` (IGC projection), `l1b_tp_collect` and `l1b_correct` (tiepointing and correction), `l1b_geo_generate`, `aviris_ng_l1a_orbit_generate` and `aviris_ng_geo_generate` (top-level drivers), `l1_osp_dir` (config dir handling).
- `l1b_geo/` — command-line scripts (`aviris_ng_l1a_orbit_process`, `aviris_ng_geo_process`, `*_pge`) installed to `$INSTALL_DIR/bin`. They call the generator classes. The L1A orbit script must run before the geo script.
- `script/` — `setup_emit.sh/.csh` templates for the runtime environment.
- `camera_model/`, `aviris_ng_support/` — camera model data (historical/fitted); `unit_test_data/` and `end_to_end_testing/` hold test inputs (including SPICE data).
- `run_shift_tests.py` — runs all files for a given date (see `README.md`).
