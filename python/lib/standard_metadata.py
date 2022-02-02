import geocal
from datetime import datetime
import re
from emit_swig import set_file_description
import os

class StandardMetadata:
    '''This handles the standard metadata that we include in our ENVI
    files.'''
    def __init__(self, igc = None, start_time = None, end_time = None,
                 pge_name = "emit-sds-l1b/l1b_geo",
                 pge_version = "1.0.0",
                 pge_input_file = { },
                 build_version = 1,
                 documentation_version = "Initial Version",
                 product_version = 1,
                 creation_time = None):
        if(start_time is None):
            start_time = igc.ipi.time_table.min_time
        if(end_time is None):
            end_time = igc.ipi.time_table.max_time
        if(creation_time is None):
            creation_time = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.start_time = start_time
        self.end_time = end_time
        self.creation_time = creation_time
        self.pge_name = pge_name
        self.pge_version = pge_version
        self.pge_input_file = pge_input_file
        self.build_version = build_version
        self.documentation_version = documentation_version
        self.product_version = product_version

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
        fh["ENVI", "emit emit acquisition start time"] = re.sub(r'[-:]', '', re.split(r'\.', str(self.start_time))[0])
        fh["ENVI", "emit emit acquisition stop time"] = re.sub(r'[-:]', '', re.split(r'\.', str(self.end_time))[0])
        fh["ENVI", "emit pge name"] = self.pge_name
        fh["ENVI", "emit pge version"] = self.pge_version
        fh["ENVI", "emit pge input files"] = "{ " + ", ".join([f"{k} = {v}" for k,v in self.pge_input_file.items()]) + " }"
        fh["ENVI", "emit software build version"] = "b%03d" % self.build_version
        fh["ENVI", "emit documentation version"] = self.documentation_version
        fh["ENVI", "emit data product creation time"] = self.creation_time
        fh["ENVI", "emit data product version"] = "v%02d" % self.product_version
        self.extra_metadata(fh)
        fh.close()
        # Remove the auxilary file GDAL creates, we don't want this around
        # after we have created the file
        try:
            os.unlink(envi_file.file_name + ".aux.xml")
        except FileNotFoundError:
            pass

        
        

__all__ = ["StandardMetadata", ]        
                 
                 
