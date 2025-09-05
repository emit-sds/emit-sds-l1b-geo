import geocal
import numpy as np
from emit_swig import set_file_description, set_band_description
from contextlib import contextmanager

class EnviFile:
    '''This is a little wrapper to make a ENVI file, and treat it like
    a memory mapped numpy array.

    This is a little clumsy, we can move this down to the C++ level and clean
    things up if needed. But for now, this is a pretty simple interface and
    it may be sufficient.'''
    def __init__(self, fname, shape = None, dtype=np.float64, mode='r+',
                 map_info = None,
                 description = "fake description", band_description = []):
        '''Create or read a EnviFile like a numpy array. The array shape
        should be nband x nline x nsamp.'''
        self.file_name = fname
        self.description = description
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
            if(map_info is not None):
                t = geocal.GdalRasterImage(fname, "ENVI", map_info, shape[0],
                                           gtype, "INTERLEAVE=BIL")
            else:
                t = geocal.GdalRasterImage(fname, "ENVI", shape[1], shape[2],
                                           shape[0],
                                           gtype, "INTERLEAVE=BIL")
            set_file_description(t, description)
            t.close()
            for i, desc in enumerate(band_description):
                # Force ENVI, every once in a while GDAL gets confused and
                # tries to open as another file type (probably magic number
                # matches a driver higher in the list)
                t = geocal.GdalRasterImage(fname, i+1, "ENVI", "", "", 4, True)
                set_band_description(t, desc)
                t.close()
            # We shuffle the shape around to get band interleave, memmap
            # assumes C order
            self._d = np.memmap(fname, shape=(shape[1],shape[0],shape[2]),
                                dtype = dtype, mode="r+").transpose(1,0,2)
            interleave = "bil"
            self.metadata = {"interleave" : interleave}
        else:
            # Force ENVI, every once in a while GDAL gets confused and
            # tries to open as another file type (probably magic number
            # matches a driver higher in the list)
            t = geocal.GdalMultiBand(str(fname), 4, "ENVI")
            self.metadata = {}
            r = t.raster_image(0)
            for k in r.metadata_list("ENVI"):
                self.metadata[k] = r["ENVI", k]
            interleave = r["ENVI", "interleave"]
            gtype = r.raster_data_type
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

            # TODO Add a check here that we actually are BIL format.
            # The data we generate will be, but if we are reading from a
            # different file it might not be. Possibly just get the right
            # transpose set up
            
            # We shuffle the shape around to get band interleave, memmap
            # assumes C order
            if(interleave == "bil"):
                self._d = np.memmap(fname,
                                    shape=(r.number_line,
                                           t.number_band,
                                           r.number_sample),
                                    dtype = dtype, mode=mode).transpose(1,0,2)
            elif(interleave == "bip"):
                self._d = np.memmap(fname,
                                    shape=(r.number_line,
                                           r.number_sample,
                                           t.number_band),
                                    dtype = dtype, mode=mode).transpose(2,0,1)
            else:
                raise RuntimeError(f"Don't recognize interleave type '#{interleave}'")
                

    @contextmanager
    def multiprocess_data(self):
        '''When we are using multiprocessing, we need to reopen the
        memmap. This just has to do with how the memmap is shared with
        other processes. We handle this as a context block, shuffling
        stuff around so you can just use the data as normal.'''
        doriginal = self._d
        self._d = np.memmap(self.file_name, shape=(self.shape[1], self.shape[0],
                                                   self.shape[2]),
                            dtype=self.data.dtype,
                            mode="r+").transpose(1,0,2)
        try:
            yield self._d
        finally:
            self._d.flush()
            self._d = doriginal

    @property
    def data(self):
        '''Give access to the underlying data, as a memory mapped numpy
           array'''
        return self._d
    
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

    def compare(self, f2):
        '''Compare with another file, returning True if the same 
        False otherwise'''
        return self.metadata_compare(f2)

    def metadata_compare(self, f2,
                         exclude_list=["emit_data_product_creation_time"]):
        '''Compare two files metadata, reporting any differences. Return
        True if the same, False otherwise'''
        same = True
        dset = set(self.metadata.keys()) ^ set(f2.metadata.keys())
        for k in dset:
            if(k in self.metadata.keys()):
                print(f"   File 1 has metadata '{k}', but File 2 does not")
            else:
                print(f"   File 2 has metadata '{k}', but File 1 does not")
            same = False
        for k in ((set(self.metadata.keys() & set(f2.metadata.keys()))) -
                  set(exclude_list)):
            if(self.metadata[k] != f2.metadata[k]):
                print(f"   Metdata '{k}' is different")
                print(f"      File 1: {self.metadata[k]}")
                print(f"      File 2: {f2.metadata[k]}")
                same = False
        return same

    # Possible we'll want to add other functions to add and read other
    # metadata in the ENVI file
        
        
            
__all__ = ["EnviFile",]
