<h1 align="center"> emit-sds-l1b-geo </h1>

_NOTE - See the **develop** branch - set as default - for the latest updates._

Welcome to the EMIT Level Level 1B Geo science data system repository.  To understand how this repository is linked to the rest of the emit-sds repositories, please see [the repository guide](https://github.com/emit-sds/emit-main/wiki/Repository-Guide).



This project provide geolocation support for AVIRIS-NG, and is based on similar support for EMIT. The code performs the following basic steps:

	1. Loads raw data plus GPS/PPS files and computes orbit information

	2. Creates an image-ground connection (IGC) and projects to the surface

	3. Performs tiepointing and matching, followed by exterior orientation correction

	4. Creates LOC/IGM/OBS output files (GLT still pending)

These are the steps to configuring and running the code:
 
	git clone -b develop https://github.jpl.nasa.gov/mhessflores/emit-sds-l1b-geo.git 
	NOTE: The develop branch must be used!

	conda activate /shared/conda-shared-env/geocal-20220215

	./configure --prefix=$INSTALL_DIR --with-test-data=/home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp 
	NOTE: for EMIT runs this test data should be used: /beegfs/store/shared/emit-test-data 

	make -j 20 all && make install && make -j 20 check && make -j 20 installcheck

	make end-to-end-aviris-ng-check

	source $INSTALL_DIR/setup_emit.sh

USAGE:

There are two main scripts, called sequentially, which can be found in $INSTALL_DIR/bin:

	1) aviris_ng_l1a_orbit_process: top-level script for setting logging and reading in config parameters, which are then passed along to emit.AvirisNgL1aOrbitGenerate(). This script takes in raw, GPS, and PPS files, along with config directory, and creates the initial orbit, time table, and line averaging files. Intermediate files "_att.nc" (produced by AvirisNgOrbit), "_line_time.nc" (produced by calling AvirisNgRaw followed by AvirisNgTimeTable), and "_raw_binfac" (same programs) in the scratch (output) directory.

	2) aviris_ng_geo_process: sets up logging and reads in config parameters, which are then passed along to emit.AvirisNgGeoGenerate(). The IGC computation itself, perhaps the most critical step in the entire pipeline, is performed here within L1bProj. Tiepointing and matching is performed using L1bCorrect, along with exterior orientation correction. Output files are generated respectively through AvirisNgLoc, AvirisNgIgm, and AvirisNgObs. 

The code can be run like this, where aviris_ng_l1a_orbit_process must be called first, followed by aviris_ng_geo_process, which takes care of the l1b stage:

	aviris_ng_l1a_orbit_process output_directory config_directory /beegfs/store/ang/y22/raw/$RAWFILE > output_l1a_log.txt

	aviris_ng_geo_process output_directory config_directory output_directory/$RAWFILE_att.nc output_directory/$RAWFILE_line_time.nc /beegfs/store/ang/y22/rdn/$RAWFILE_rdn_v2z4_clip > output_geo_log.txt

Where:

 - $RAWFILE is for example ang20220224t195402
 - The config directory can be found at this location:
	/home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp

NOTE: The following script can be used to produce all files for a given date:
	/home/mhessflores/emit-sds-l1b-geo/run_shift_tests.py

Source files for the classes used by these main functions can be found at:
	$INSTALL_DIR/lib/python3.9/site-packages/emit:

Here is a short description for each:

 - aviris_igm.py: Small helper class that handles reading AVIRIS IGM and returns the ground location. Computes Geodetic(lon, lat, elv).
NOTE: This is specific to AVIRIS, not AVIRIS-NG!

 - aviris_ng_geo_generate.py: This is the overall l1b geo process for AVIRIS NG. This is very similar to L1bGeoGenerate for EMIT. 

 - aviris_ng_glt.py: This generates the aviris_glt_geo GLT file.               

 - aviris_ng_igm.py: Generate or read the IGM file for AVIRIS-NG.              

 - aviris_ng_l1a_orbit_generate.py: This is the overall l1a orbit process for AVIRIS NG. This creates the initial orbit, time table, and line averaging files.

aviris_ng_loc.py: Generate or read the LOC file for AVIRIS-NG. Note this is almost identical to EmitLoc, and can eventually be joined together as a set of options or derived class. As a convention, if the IGC is supplied a file is created, and otherwise an existing one is read in.           

 - aviris_ng_obs.py: Reads/writes the AVIRIS NG obs data. As a convention, if the IGC is supplied a file is created, and otherwise an existing one is read in.           

 - aviris_ng_orbit.py: Orbit creation using the GPS/PPS data, and can write to a netCDF file. It calls aviris_ng_raw, which is the actual code to read GPS/PPS initially.     

 - aviris_ng_raw.py: Reads the metadata from the raw AVIRIS-NG files reads raw GPS and PPS). The file is a ENVI format file, with the metadata in the first band (e.g., this isn't actually DN data). Clock values are extracted out, along with the obcv. The clock values are integers which corresponds to a actual time the data was acquired. The clock value maps to the PPS file, which gives the gps time for particular clock values. So the clock values can't really be interpreted as anything meaningful without the PPS file, basically this are just "ticks".      

 - aviris_ng_standard_metadata.py: Handles standard metadata for AVIRIS NG.

 - aviris_ng_time_table.py: Reads the given raw PPS file for AVIRIS-NG, or the given netCDF file. For the PPS file, we use the given line_average and create a time table for every science packet.

 - aviris_orbit.py: Reads the AVIRIS orbit data. Note that there are two versions of this, a "eph" which is in terms of UTM and a "lonlat_eph" in terms of latitude and longitude. This class takes the second format. We could read the UTM data if needed, but 1) we can't easily know the UTM zone number and 2) the lonlat version gets generated whenever the UTM version does. The orbit data doesn't contain any timing information. So we also require that the AvirisTimeTable that goes with this data also.
NOTE: This is specific to AVIRIS, not AVIRIS-NG!

 - aviris_time_table.py: Creates a time table from an AVIRIS obs file. The day is obtained from parsing the file name, and the time of each line from the UTC hour found in band 10 of the file. 
NOTE: This is specific to AVIRIS, not AVIRIS-NG!

 - envi_file.py: Wrapper to make a ENVI file, and treat it like a memory mapped numpy array.

 - misc.py: Includes functions band_to_landsat_band, and others.

 - gaussian_stretch.py: This does histogram equalization on the given data, doing a Gaussian stretch. This currently this uses the vicar program 'stretch'. It is assumed that all negative values are fill, and map them to 0. Data is returned as integer data.

 - geo_qa.py: This handles the Geo QA file.

 - l1_osp_dir: This class handles the L1OspDir, such as reading the l1b_geo_config. Loads the camera.xml and reads l1b_geo_config.py.

l1b_correct.py: This takes an in initial IgcCollection, collects tie-points, does image image matching, and runs the SBA to generate a corrected image ground connection. It also does fitting of the camera exterior orientation (the euler angles). Alternatively, the full sba program which can be used if desired.

l1b_geo_log_formatter.py: Set logging format, optionally with color.

l1b_proj.py: This handles projection the Igc to the surface, forming a vicar file that can be matched against. Generates intermediate files map_info_*.xml, igc_*.xml, proj_*.img, and ref_*s.img in the scratch (output) directory.

l1b_tp_collect.py: Project data to the surface and collect tie-points with the orthobase; calls L1b_proj.py. Generates tpmatch*.log files and directories. 

The following files are EMIT-specific and do not apply for anything related to AVIRIS-NG, but are kept in the repo for potential future merging:

	emit_igc.py	
	emit_kmz_and_quicklook.py
	emit_loc.py
	emit_obs.py
	emit_orbit_extension.py
	emit_time_table.py
	emit_camera.py                   
	emit_glt.py                      
	standard_metadata.py
	l1b_geo_generate.py

==========

NOTES ON TIEPOINTING:

There are some important aspects about the way tiepointing and matching is performed for AVIRIS-NG. Being a push broom camera (pixels not generated at the same time), it generates a single "long" image, which Geocal's Image Ground Connection (IGC) is not currently set up to handle. Therefore, tiepointing and matching are performed on scenes consisting of 1000 lines at a time. For example, if a single image of 18500 lines is generated, 19 individual tiepointing outputs are generated. 

In the output directory for each run, 'tpcol.xml' is the tiepoint collection file with all the tiepoints. Each has ground location in Ecr coordinates and image coordinates.

==========

OTHER NOTES:

This project, as well as EMIT, are extensions of [GeoCal](https://github.jpl.nasa.gov/Cartography/geocal). If you simply want to use GeoCal as a python library nothing needs to be done. But if you
want to add new C++, wrap this in SWIG, and make available to GeoCal programs then there is some cookie cutter set up to write.

This also make use of [general-autoconf](https://github.jpl.nasa.gov/Cartography/general-autoconf), see [README Git](README.git) for details.


