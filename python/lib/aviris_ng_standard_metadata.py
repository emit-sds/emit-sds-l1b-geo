import geocal
from datetime import datetime
import re
from emit_swig import set_file_description
import os

class AvirisNgStandardMetadata:
    '''This handles the standard metadata that we include in our ENVI
    files. 

    This is very similar to StandardMetadata, but is for the AVIRIS NG
    product.'''
    def __init__(self, line_averaging = 9):
        '''Not really sure what line_averaging is. We are just copying
        what pyortho had here. Will likely need to modify this.'''
        self.line_averaging = line_averaging

    def extra_metadata(self, fh):
        '''Place for derived classes to put in extra metadata'''
        pass

    def write_metadata(self, envi_file):
        '''Write out the metadata to the given EnviFile'''
        envi_file.flush()
        fh = geocal.GdalRasterImage(envi_file.file_name, 1, 4, True)
        # The description seems to get overwritten with the file name every
        # time GDAL writes it out. So reset the description, even though
        # this was already set.
        set_file_description(fh, envi_file.description)
        fh["ENVI", "line averaging"] = str(self.line_averaging)
        fh.close()
        # Remove the auxilary file GDAL creates, we don't want this around
        # after we have created the file
        try:
            os.unlink(envi_file.file_name + ".aux.xml")
        except FileNotFoundError:
            pass

        
        

__all__ = ["AvirisNgStandardMetadata", ]        
                 
                 
