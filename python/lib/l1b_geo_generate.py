from .envi_file import EnviFile
import geocal
import numpy as np
import os
import shutil
import logging
import re

logger = logging.getLogger('l1b_geo_process.l1b_geo_generate')

# Not sure if we really want this to be a class or not, but I think there
# may be enough overlap between calculations that we want to keep these
# together.
#
# Also, we'll probably want to run some of this in parallel and/or move to
# C++. I imagine this will be a bit slow.
class L1bGeoGenerate:
    def __init__(self, igc, prod_dir, onum = 100, snum = 1, bnum = 1,
                 vnum = 1):
        self.igc = igc
        self.prod_dir = prod_dir
        self.onum = onum
        self.snum = snum
        self.bnum = bnum
        self.vnum = vnum

    def emit_file_name(self, file_type, ext=".img"):
        '''Generate a EMIT file name using the EMIT naming convention'''
        # Create yyyymmddthhmmss from tm
        tm = self.igc.pixel_time(geocal.ImageCoordinate(0,0))
        dstring = re.sub(r'T', 't', re.sub(r'[-:]', '',
                                           re.split(r'\.', str(tm))[0]))
        return os.path.join(self.prod_dir,
              "emit%s_o%05d_s%03d_%s_b%03d_v%02d%s" %
              (dstring, self.onum, self.snum, file_type, self.bnum, self.vnum,
               ext))
    
    def generate_quicklook(self, fname):
        '''Generate the quick look image file'''
        # Currently just a fake file
        logger.info("Generating Quicklook data")
        with open(fname, "w") as fh:
            print("Fake data", file=fh)

    def generate_kmz(self, fname):
        '''Generate KMZ quick look image file'''
        # Currently just a fake file
        logger.info("Generating KMZ data")
        with open(fname, "w") as fh:
            print("Fake data", file=fh)

    def generate_qa(self, fname):
        '''Generate QA file'''
        # Currently just a fake file
        logger.info("Generating QA data")
        with open(fname, "w") as fh:
            print("Fake data", file=fh)

    def generate_att(self, fname):
        '''Generate a corrected ATT file'''
        # Currently just a place holder, we copy the input file to the output
        logger.info("Generating ATT data")
        fin = self.igc.ipi.orbit.file_name
        shutil.copyfile(fin, fname)

    def generate_obs(self, fname, loc_fname):
        '''Generate the Level 1B Observation Geometry (OBS) File'''
        # This is a bit slow, we may well want things to go into C++
        logger.info("Generating OBS data")
        loc = EnviFile(loc_fname)
        d = EnviFile(fname,
                     shape=(11, self.igc.number_line, self.igc.number_sample),
                     dtype = np.float64, mode="w")
        d[:,:,:] = -9999
        lon = loc[0,:,:]
        lat = loc[1,:, :]
        h = loc[2,:,:]
        for ln in range(self.igc.number_line):
            if(ln % 100 == 0):
                logger.info("Doing line %d" % ln)
            pos = self.igc.cf_look_vector_pos(geocal.ImageCoordinate(ln,0))
            tm = self.igc.pixel_time(geocal.ImageCoordinate(ln,0))
            for smp in range(self.igc.number_sample):
                gp = geocal.Geodetic(lat[ln,smp], lon[ln,smp], h[ln,smp])
                # TODO Double check direction here. Possible we are going in
                # the wrong direction, so may have various 90- and -180 we
                # need to but in place.
                clv = geocal.CartesianFixedLookVector(pos, gp)
                lv = geocal.LnLookVector(clv, gp)
                slv = geocal.LnLookVector.solar_look_vector(tm, gp)
                d[1,ln,smp] = lv.view_zenith
                d[2,ln,smp] = lv.view_azimuth
                d[3,ln,smp] = slv.view_zenith
                d[4,ln,smp] = slv.view_azimuth
                # TODO Fill in other fields here. Mostly a matter of
                # tracking down the exact definition of each of these, we
                # have a lot of the info available. Think we'll need to
                # add slope and aspect to DEM, I don't think we have anything
                # around to calculate this.

    def generate_glt(self, fname):
        '''Generate the Level 1B Geographic Lookup Table (GLT) File'''
        # TODO Note we talked with Phil about generating 2 versions of these, one
        # with a rotated UTM and one with rotated geographic. We'll need to
        # come back to this, and figure out the file names
        logger.info("Generating GLT data")
        d = EnviFile(fname,
                     shape=(2, self.igc.number_line, self.igc.number_sample),
                     dtype = np.int32, mode="w")
        d[:,:,:] = -9999
        
    def generate_loc(self, fname):
        '''Generate the Level 1B Pixel Location (LOC) File'''
        # This will likely be a bit on the slow side
        logger.info("Generating LOC data")
        d = EnviFile(fname,
                     shape=(3, self.igc.number_line, self.igc.number_sample),
                     dtype = np.float64, mode="w")
        # We pick a large resolution here to force the subpixels to be 1.
        rcast = geocal.IgcRayCaster(self.igc,0,-1,1,10000)
        while(not rcast.last_position):
            gpos = rcast.next_position()
            for i in range(gpos.shape[1]):
                gp = geocal.Geodetic(geocal.Ecr(gpos[0,i,0,0,0,0],
                                                gpos[0,i,0,0,0,1],
                                                gpos[0,i,0,0,0,2]))
                d[0,rcast.current_position, i] = gp.longitude
                d[1,rcast.current_position, i] = gp.latitude
                d[2,rcast.current_position, i] = gp.height_reference_surface
                
                
__all__ = ["L1bGeoGenerate",]
