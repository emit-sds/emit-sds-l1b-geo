import logging
import numpy as np
import geocal

logger = logging.getLogger('l1b_geo_process.avirs_ng_raw')

class AvirisNgRaw:
    '''This is used to read the metadata from the raw AVIRIS-NG files.
    We don't actually care about most of this, instead we just want to
    extract the frame metadata.

    The file is a ENVI format file, with the metadata in the first band
    (e.g., this isn't actually DN data).

    We extract out the clock values, and the obcv.

    The clock values are integers which corresponds to a actual time
    the data was acquired. The clock value maps to the PPS file, which
    gives the gps time for particular clock values. So the clock values
    can't really be interpreted as anything meaningful without the PPS file,
    basically this are just "ticks".

    The obcv gives the type of data collected for a particular line, we
    are interested in the OBC_SCIENCE values.
    '''
    OBC_DARK1     = 2
    OBC_SCIENCE   = 3
    OBC_DARK2     = 4
    OBC_BRIGHTMED = 5
    OBC_BRIGHTHI  = 6
    OBC_LASER     = 7
    
    def __init__(self, fname, chunk_size=2000):
        '''This reads the given fname to get the clock and obc values. 
        The data files tend to be big, we read it with the given chunking
        size.'''
        self.fname = fname
        f = geocal.GdalRasterImage(self.fname)
        logger.info("Reading the raw file %s", self.fname)
        self.clock = np.zeros((f.number_line,), dtype=np.int64)
        self.obc = np.zeros_like(self.clock, dtype=np.uint16)
        for i in range(0,self.clock.shape[0],chunk_size):
            r = range(i,min(i+chunk_size, self.clock.shape[0]))
            logger.info(f"Reading line %d of %d", i, self.clock.shape[0])
            d = f.read(r.start,0,len(r),2)
            self.clock[r] = d[:,0].astype(np.int64) << 16 | d[:,1]
            d = f.read(r.start,321,len(r),1)
            self.obc[r] = d[:,0] >> 8

    def clock_science(self, img_sl = 800):
        '''Return all the clock values when we are in science mode. Note
        that is isn't line averaged yet, so normally you would only use these
        values for figuring out the line_average'''
        return self.clock[img_sl:][self.obc[img_sl:] == self.OBC_SCIENCE]

    def clock_average(self, img_sl = 800, line_average = 9):
        '''The processing averages a given number of lines (given
        by the binfac file). I'm not actually sure how this number
        gets calculated, we'll assume here it is just "known". We
        also trim off the start of raw data, I'm guessing there is just
        some garbage here. This value came from the config file in
        the pyortho code.

        Once we have this, the science data is averaged. The time
        for the averaged data is just the average of the times.'''
        self.img_sl = img_sl
        self.line_average = line_average
        clock_sci = self.clock_science(img_sl=img_sl)
        clock_avg = []
        for i in range(0,len(clock_sci),self.line_average):
            if(i+self.line_average <= len(clock_sci)):
                clock_avg.append(clock_sci[i:i+self.line_average].mean())
        return np.array(clock_avg)
        
            
        
        
