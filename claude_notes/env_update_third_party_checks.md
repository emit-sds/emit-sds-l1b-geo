# Env updates: checking for problems that come from third party libraries

Written 2026-11-27 from the geocal session, at the maintainer's request, to pass on what geocal is doing after the
GDAL VRT / VICAR plugin problem (GDAL 3.10 changed a default, and it was found only by accident, in EMIT). The
full plan is in the geocal repository, `claude_notes/third_party_testing_plan.md` (step F14 of geocal's Phase 10);
this is the part that applies to every project that takes its libraries from a conda or pixi env. Nothing here
has been done in this repository yet.

## The procedure, at every env update

1. Keep the previous env (its lock file and, if possible, the env directory).
2. List the packages whose version changed (diff the lock files) and read the release notes of the ones this code
   calls, looking for: changed defaults, new threading, removed or renamed options and drivers, changed numerics.
   Write a short note of what was found.
3. Run a fixed set of real operations in both envs, at the same commit of this code, and compare the outputs
   (integer images exactly, numbers numerically).
4. Explain every difference (expected, with the release note; or a finding) before the new env is adopted.

## Tests that can see this kind of problem

* Data generated with a known answer, just past the library's thresholds: several tiles or files, compressed,
  large enough that the library's fast paths (threads, caches) are used. Small single file tests don't reach them.
* The same data read by two independent routes and compared.
* Each case run several times and compared (the VRT failure was random, and when it didn't fail it wrote wrong
  pixels).
* Every value compared, not the size and a few samples.
* A check in the test fixtures that fails a test when a library has started threads nobody asked for.
* A list of the libraries that are process wide and not thread safe, and of what can call them from a thread.

## For this project

This project uses GDAL and the VICAR GDAL plugin through geocal and through command lines (`gdalbuildvrt` +
`gdal_translate`). geocal's fix covers only its own `create_subset_file`; the command lines need
`VRT_NUM_THREADS=1` in the environment until the plugin with the RTL mutex is packaged. The command lines that
geocal's review found are listed in geocal's `claude_notes/gdal_3_10_to_3_13_review.md`; they should go into the
two env comparison with real inputs. geocal's test data generator and characterization suite (Phase 10 step F14,
not written yet) are meant to be reusable here.
