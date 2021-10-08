This code used to simulate input data that we will use for end to end testing
of the geolocation PGE.

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
