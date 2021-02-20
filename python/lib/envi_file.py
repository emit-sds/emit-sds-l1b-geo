import geocal
import numpy as np

class EnviFile:
    '''This is a little wrapper to make a ENVI file, and treat it like
    a memory mapped numpy array.

    This is a little clumsy, we can move this down to the C++ level and clean
    things up if needed. But for now, this is a pretty simple interface and
    it may be sufficient.'''
    def __init__(self, fname, shape = None, dtype=np.float64, mode='r+'):
        '''Create or read a EnviFile like a numpy array. The array shape
        should be nband x nline x nsamp.'''
        if(mode not in ("w", "r", "r+")):
            raise ValueError("Unknown mode")
        if(mode == "w"):
            if(dtype == np.float64):
                gtype = geocal.GdalRasterImage.Float64
            elif(dtype == np.float32):
                gtype = geocal.GdalRasterImage.Float32
            elif(dtype == np.int32):
                gtype = geocal.GdalRasterImage.Int32
            elif(dtype == np.uint32):
                gtype = geocal.GdalRasterImage.UInt32
            elif(dtype == np.int16):
                gtype = geocal.GdalRasterImage.Int16
            elif(dtype == np.uint16):
                gtype = geocal.GdalRasterImage.UInt16
            elif(dtype == np.int8):
                gtype = geocal.GdalRasterImage.Byte
            else:
                raise ValueError("Unsupported data type")
            t = geocal.GdalRasterImage(fname, "ENVI", shape[1], shape[2], shape[0],
                                gtype, "INTERLEAVE=BIL")
            t.close()
            # We shuffle the shape around to get band interleave, memmap
            # assumes C order
            self.d_ = np.memmap(fname, shape=(shape[1],shape[0],shape[2]),
                                dtype = dtype, mode="r+").transpose(1,0,2)
        else:
            t = geocal.GdalMultiBand(fname)
            gtype = t.raster_image(0).raster_data_type
            if(gtype == geocal.GdalRasterImage.Float64):
                dtype = np.float64
            elif(gtype == geocal.GdalRasterImage.Float32):
                dtype = np.float32
            elif(gtype == geocal.GdalRasterImage.Int32):
                dtype = np.int32
            elif(gtype == geocal.GdalRasterImage.UInt32):
                dtype = np.uint32
            elif(gtype == geocal.GdalRasterImage.Int16):
                dtype = np.int16
            elif(gtype == geocal.GdalRasterImage.UInt16):
                dtype = np.uint16
            elif(gtype == geocal.GdalRasterImage.Byte):
                dtype = np.int8
            else:
                raise ValueError("Unsupported data type")
            # We shuffle the shape around to get band interleave, memmap
            # assumes C order
            self.d_ = np.memmap(fname,
                                shape=(t.raster_image(0).number_line,
                                       t.number_band,
                                       t.raster_image(0).number_sample),
                                dtype = dtype, mode="r+").transpose(1,0,2)

    @property
    def data(self):
        '''Give access to the underlying data, as a memory mapped numpy
           array'''
        return self.d_
    
    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    @property 
    def shape(self):
        return self.data.shape

    @property 
    def dtype(self):
        return self.data.dtype

    def flush(self):
        self.data.flush()
    
    # Possible we'll want to add other functions to add and read other
    # metadata in the ENVI file
        
        
            
__all__ = ["EnviFile",]
