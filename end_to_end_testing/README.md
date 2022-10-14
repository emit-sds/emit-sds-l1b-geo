ASTER based test data
---------------------

This code used to simulate input data that we will use for end to end testing
of the geolocation PGE. This data is suitable for testing the geolocation,
but is really too far away from EMIT to be used for down stream processing.

The file iss_spice/iss_2020.bsp gives a SPICE kernel for 2020 for the ISS.
This comes from www.space-track.org, and is the actual ISS orbit. We could
use ECOSTRESS data, but it is a bit tricky to find data that passes over
the CA ASTER Mosaic we have for generating test data. So we use the full
ISS orbit.

The program iss_orbit_determine.py is a one-off used to determine the
times that we have passes over our CA ASTER mosaic. This isn't
something we are likely to need again. It generates the intermediate
file iss_time.json, which again isn't something we are likely to use
regularly.

The data is restricted to day time data that passes near the CA mosaic
data. We can then use http://www.isstracker.com/historical to view the
actual orbits, and select the one that passes through our data the best

Good orbit time looks like 2020-06-10T01:51:31.753198Z

AVIRIS-NG Based Data
--------------------

This data is no longer used. We include the original information for reference.

This data is based off a real AVIRIS-NG, a specific data set 
20170328t202059.

The AVIRIS-NG data is generated using the program pyortho. To generate
EMIT like data, we run this program with a breakpoint, and then dump
data out as a pickle file.

Note that pyortho uses python 2.7. To read the pickle file with python 3
you need to use the "bytes" encoding option (see https://groups.google.com/g/sage-devel/c/nLG8zMSKSD0),
so something like:

    fname = "pyortho_20170328t202059.pkl"
	pickle.load(open(fname, "rb"), encoding="bytes")
	
We dump both the data that we need to generate the EMIT test data, and
the arguments to the function generate_obs_loc function. Strictly speaking
we don't actually need the function arguments, but it seemed like a good
idea to save this so we could run generate_obs_loc again w/o needing to
run the full pyortho program (which takes about 45 minutes to run).

The program needs to be run in a particular environment, with a breakpoint
set on the function "generate_obs_loc". So:

    conda activate /home/brodrick/miniconda/envs/pyortho
	
Start ipython, and run with:

    %run -d -b /home/brodrick/src/pyortho/ortho_util.py:2550 /home/brodrick/src/pyortho/orthorectify.py -p AVIRIS-NG -c /home/brodrick/src/ang/ort/data/avng_er2_2017_camera_cal3_2017_03_23_15_19_17 -d /beegfs/store/shared/dem/conus_ned_1arcsec -o /home/smyth/data/aviris-ng-work/ortho_debug/ /beegfs/store/brodrick/emit/pushbroom_demo/raw/ang20170328t202059_raw
	
Note this will run for a fair chunk of time.  We then save the data out
as a pickle file:

    import pickle
	pickle.dump([igmf,dem,frame_meta,gps_table],open("pyortho_20170328t202059_funcarg.pkl", "wb"))
	pickle.dump([frame_meta,gpstime, "2017-03-28T00:00:00Z", zone_alpha],open("pyortho_20170328t202059.pkl", "wb"))	
