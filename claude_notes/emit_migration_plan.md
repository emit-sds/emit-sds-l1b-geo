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
