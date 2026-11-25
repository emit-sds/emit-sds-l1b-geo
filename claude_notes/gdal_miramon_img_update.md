# GDAL 3.13 MiraMonRaster driver breaks update-mode opens of ENVI `*.img` files

Written for a geocal session that will update comments (no code change wanted).

## Symptom

With GDAL 3.13.3 (pixi env, python 3.14, geocal 1.26.1 built from geocal-repo
e6577fe), update-mode opens of an ENVI file named `*.img` fail:

```python
geocal.GdalRasterImage("x_l1b_loc_v02.img", 1, 4, True)   # Update = True
# RuntimeError: Trouble opening file x_l1b_loc_v02.img
```

"Trouble opening file" is the generic message from `gdal_openex`
(`lib/GeoCalCore/Implementation/geocal_gdal.cc`, thrown when `GDALOpenEx`
returns null). With `CPL_DEBUG=ON` GDAL itself says the file "succeeds as ENVI"
when probed read-only, which hides the real problem.

## Root cause (a GDAL problem, not geocal, not vicar-gdalplugin)

GDAL 3.13 added the **MiraMonRaster** driver, whose extensions are `rel img`.
When no driver list is given, GDAL probes drivers in registration order and
MiraMonRaster comes before ENVI (index 196 vs 203 in this build). For an
update-mode open, MiraMonRaster accepts the `.img` name and then fails with:

    ERROR 6: The MiraMonRaster driver does not support update access to
    existing datasets.

GDAL does not fall through to ENVI, so the open fails. Read-only opens are fine.

Evidence:
- Plain C, no geocal: `GDALOpenEx(f, GA_Update, nullptr/empty lists...)` fails
  with the error above on the ENVI `.img`.
- The same file copied to `.bin` (with its `.hdr`) opens fine in update mode.
- `GDAL_SKIP=MiraMonRaster` makes the open succeed.
- Passing the driver explicitly (`allowed_drivers=['ENVI']`) succeeds.
- vicar-gdalplugin was not the cause: the failure is the MiraMon message, and
  the vicar driver is not involved.

## Workarounds (known, accepted)

1. Pass the driver explicitly. For `GdalRasterImage` this is the overload
   `GdalRasterImage(fname, band, "ENVI", "", "", number_tile, update)`
   (the driver is `Allowed_drivers`, as used by `gdal_openex`).
   emit's `envi_file.py` already does this, and emit now does so in
   `standard_metadata.py`, `emit_glt.py` and `aviris_ng_standard_metadata.py`.
2. Set `GDAL_SKIP=MiraMonRaster` in the environment. With this set, emit's
   `make end-to-end-check` passes with no code changes. It affects every
   GDAL user in the environment.

## Requested comment updates in geocal

No behavior change. Add a comment where it will be found:

- At `gdal_openex` in `lib/GeoCalCore/Implementation/geocal_gdal.cc`, next to
  the `throw Exception("Trouble opening file " + Fname)`: when `Update` is true
  and no `Allowed_drivers` is given, GDAL >= 3.13 can pick MiraMonRaster for
  `*.img` files, which can't be opened for update. Say to pass the driver
  (e.g. "ENVI") explicitly or set `GDAL_SKIP=MiraMonRaster`.
- At the documentation of the `GdalRasterImage(Fname, Band_id, Number_tile,
  Update, ...)` constructor in `gdal_raster_image.h`/`.cc` (the one with no
  driver argument): same note, pointing at the overload that takes
  `Allowed_drivers`.
- Optionally in the Python docs for those constructors.

## Context

Found while fixing `make end-to-end-check` in emit's `build-pixi`
(see also `memory/emit-gdal-open-driver.md`). The python 3.14 multiprocessing
default change (forkserver) was a separate issue, already fixed in emit by
using `get_context("fork").Pool(...)`.
