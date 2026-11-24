# Moving emit to the ecostress-level1 / geocal-repo / framework layout

Started 2026-11-24. Target is geocal 1.x for now (not geocal 2.0 / nanobind); ecostress-level1 `master` is the model.

## Done in the first pass
- `CLAUDE.md` with the no-commit rule and the `claude_notes/` convention (as geocal-repo and framework).
- `env/linux/pixi.toml` and a pixi-based `env/Makefile` (copied from ecostress-level1, renamed ECOSTRESS -> EMIT). Not yet run: no env created, no `pixi.lock`.
- `python/test` -> `python/tests` (as ecostress-level1 and geocal-repo); `python/Makefile` and `python/python.am` updated; `python/test.sh` copied from geocal-repo.
- `.gitignore`: build products in `python/`, generated `claude_notes/*.html`.

## Not done / to decide
1. Create the env (`make -C env create-env`), then `make -C env update-lock` and commit `env/linux/pixi.lock`; flip `PIXI_LOCKED` to yes.
2. Old micromamba files in `env/` (`emit_environment_*.yml`, `micromamba`, `*~`) are now unused; delete once the pixi env works. `README.md` still describes the old conda flow.
3. `python/Makefile`: ecostress uses `python -m pip install -e .` (no `--prefix=$(EMITTOP)`); emit still uses `--prefix`. Pixi env sets `EMITTOP=$CONDA_PREFIX`, so check which works.
4. Replace `setup_emit.sh` dependence in `python.am` (`python-check`) if the pixi env makes it unnecessary.
5. `conftest.py` fixtures in `python/tests/fixtures` still use the old `--with-test-data` mechanism; compare with ecostress-level1.
6. ecostress-level1 also has `python/ecostress/__init__.py` made by `mkinit` and `ecostress_version.py`; emit has neither.
7. Optional later: geocal 2.0 port (see ecostress-level1 branch `geocal_2.0`, geocal-repo `RELEASE_NOTES_2.0.md`), `ruff`/`mypy` cleanup, coverage.

## Deferred (come back to these)
- **Code coverage**: geocal `maintain_1.28` `common.am` has `ax_code_coverage` rules (`CODE_COVERAGE_*`, `@CODE_COVERAGE_RULES@`) and `config/m4/ax_code_coverage.m4` is already here; emit's `common.am` lacks the rules. Also see geocal-repo `script/coverage.sh` (`make coverage`).
- **swig_rules subtree**: geocal 1.28 keeps generic SWIG support in a `swig_rules/` subtree (`swig_rules.am`, `swig_wrap.tmpl`, `doxy2swig.py`, `doxygen_single.cfg`, `create_python_init.py`, `include/*.i`, `lib/`). Emit keeps copies in `config/` and `bindings/python/` (`python.am` hand-written). Consider switching to the subtree; touches `bindings/python/python.am` and `config/m4_local/emit_source_directory.m4` (`swigrules`).
- 2026-11-24: pulled from geocal `maintain_1.28`: `doxy2swig.py`, `doxygen_single.cfg`, raw-string fix in `create_python_init.py`, boost_process in `ac_boost.m4`. Not yet tested with a build. Not taken: `<module>_config.h` include in `create_python_init.py` (emit has no `emit_config.h`), `ac_msp.m4`, `ac_geotiff.m4`.
- `general-autoconf` master is geocal 2.0 (no SWIG macros); don't subtree-pull it while on SWIG.

## EmitResampler (2026-11-24)
- geocal 20261021 (develop_2_0 and maintain_1.28) now has its own `GeoCal::Resampler` (added 2026-09-01, copied from ECOSTRESS; `geocal/resampler.h`). Emit's `Emit::Resampler` copy made `#include "resampler.h"` in the SWIG wrapper pick up geocal's header, and the build failed.
- Same fix as ecostress-level1 (commit 780d22d, "Rename a couple of files that got copied over to geocal"): renamed the class and files so the names don't conflict, and kept our copy so we don't depend on the newer geocal. `lib/resampler.*` -> `lib/emit_resampler.*`, class `EmitResampler`, python uses `from emit_swig import EmitResampler`.
- **TODO: remove this and use `geocal.Resampler`.** Differences to handle: geocal's `resample_field` has an extra `Fill_value_threshold` argument (default: no threshold), whereas ours hardcodes `fill_value_threshold = -999`, so callers need `Fill_value_threshold=-999`. Geocal also has `Mark_missing` in the constructor (ours hardcodes -1000), `clear`, `empty_resample`, `determine_range`. Callers: `emit_glt.py`, `aviris_ng_glt.py`, `emit_kmz_and_quicklook.py`. Then drop `emit_resampler.*` and `lib.am` entries.

## SWIG version (2026-11-24)
- geocal's installed `geocal_swig` wrappers and ecostress-level1's regenerated ones are SWIG 4.4.0; emit's checked-in wrappers were mostly 4.3.1 (one 3.0.12). The swig `.i` support files (`swig_array.i` etc.) come from the geocal install, `share/geocal/swig`, via `GEOCAL_SWIG_CFLAGS`, so they follow whichever geocal is in the env.
- `env/linux/pixi.toml` now pins `swig = "4.4.0"` (ecostress-level1 still has `<4.4.0`). All wrappers in `bindings/python/swig` should be regenerated together with the same SWIG.
- `bindings/python/python.am` `GSWIG_FLAGS` strips `-pthread` (as ecostress-level1 does): the newer geocal's `BLITZ_CFLAGS` has it, and SWIG rejects it.
- `./bootstrap` was rerun in the pixi env (automake 1.20, autoconf 2.72, libtool): `configure`, `Makefile.in`, `aclocal.m4` regenerated 2026-11-24. Rerun it after changing any `.am`/`configure.ac`/m4.

## First full test run (2026-11-24, pixi env `/home/smyth/Local/emit-build/build-pixi`, SWIG 4.4.0, geocal 20261021)
- `make -j 10 all` (SWIG wrappers regenerated, maintainer mode), `make install`, `make check` (C++): all pass.
- `make installcheck` (python, no `--run-long`): 11 passed, 34 skipped (12 need `--run-long`, 5 unconditional skips, the rest not itemized; xdist reports more skips than a serial run).
- **TODO: come back to the long tests.** `pytest -n 10 --run-long tests` (about 12 minutes): 7 failed, 33 passed, 5 skipped. Not known whether they ever passed before this migration, so don't assume a regression. The first run's output was cut off (`| tail -30`), so the failures weren't named; a rerun logs to `/home/smyth/Local/emit-build/build-pixi/long.log` (use `-rfE --tb=short`). One captured log in the first run showed `l1b_tp_collect`: "Too few tie-point found. Found 0, and require at least 20" for scene 20240102t001521, then "No tie-points, so skipping SBA correction" (may be expected for that test, not confirmed to be a failure cause).
- The long tests are slow and I/O bound (workers in D state; `/ldata` is 98% full), and they use the data in `/home/smyth/Local/emit-test-data` and `/opt/afids/data`.
- `python/.pytest_cache/v/cache/lastfailed` is stale (old `lib/...` paths); ignore it.
- To check against the old setup: run the same long tests with the pre-migration commit (`git stash` or a worktree at `HEAD`) in the old conda env, if it still exists, to see whether the 7 failed there too.

### Long test failures (rerun 2026-11-24, `long.log`, 7 failed / 33 passed / 5 skipped, 3 minutes)
The same 7 fail on both runs. Two groups:
1. **"RuntimeError: Trouble opening file test_*.img"** (5 tests: `emit_obs_test::test_generate_obs`, `emit_glt_test::test_generate_glt`, `emit_loc_test::test_generate_loc`, `aviris_ng_loc_test::test_generate_avris_loc`, `standard_metadata_test::test_standard_metadata`). Raised from `geocal.GdalRasterImage(str(fname), 1, 4, True)` (update mode, on an ENVI `.img` the code just wrote) in `standard_metadata.py:52` (`write_metadata`) and `emit_glt.py:188`. Candidates: GDAL 3.13.3's ENVI driver (the env's GDAL is much newer than whatever this last ran with) or the newer geocal's `GdalRasterImage` open flags, or file not flushed/closed before reopening. `gdal.GetDriverByName('ENVI')` exists. Start by reproducing outside pytest.
2. **"RuntimeError: Band out of range, Band: 38, Should be in range 1 to 2"** (2 tests: `l1b_geo_generate_test::test_l1b_geo_generate`, `::test_dateline_l1b_geo_generate`). Raised from `EmitL1bImage(str(rdn_fname), l1b_band, ...)` in `emit_igc.py:141`. The radiance file used has 2 bands but code asks for band 38, so likely the test data in `/home/smyth/Local/emit-test-data` is a reduced file or the wrong one, not a code problem. Check against the data the tests expect (the end-to-end data in `/store/shared/emit-test-data`?).
- Neither group touches the SWIG/EmitResampler changes made here, but we haven't compared with the pre-migration code, so that is still open (see above).
