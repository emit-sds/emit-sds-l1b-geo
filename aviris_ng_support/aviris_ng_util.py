# Stuff we can generally find useful
import geocal
import emit
import glob
import os
import multiprocessing

def find_exactly_one_file(pattern):
    f = glob.glob(pattern)
    if(len(f) == 0):
        raise RuntimeError(f"Could find a file matching {pattern}")
    if(len(f) > 1):
        raise RuntimeError(f"Found more than one file matching {pattern}")
    return f[0]

def create_igc(dir):
    '''Create a IGC that has the final results for a given run directory.
    We have an assumed set of files in the directory, just to make this
    simpler.'''
    bname = os.path.basename(dir).split("_")[0]
    orb = emit.AvirisNgOrbit(find_exactly_one_file(dir + "/*_att.nc"))
    tt = emit.AvirisNgTimeTable(find_exactly_one_file(dir + "/*_line_time.nc"))
    rad_band = 54
    rad_scale = 100.0
    rad = geocal.GdalRasterImage(find_exactly_one_file(dir + "/*_rdn_v2z4_clip"),
                          rad_band)
    rad = geocal.ScaleImage(rad, rad_scale)
    cam_final = geocal.read_shelve(f"{dir}/{bname}_camera.xml")
    ipi = geocal.Ipi(orb,cam_final,0,tt.min_time, tt.max_time,tt)
    igc = geocal.IpiImageGroundConnection(ipi, geocal.SrtmDem(), rad,
                                          bname, 1.0)
    # Tack on the loc file, it is useful to have access to this
    igc.loc = emit.AvirisNgLoc(f"{dir}/{bname}_loc")
    return igc

def dir_igc(igc):
    '''Return the directory that the igc is for.'''
    return os.path.dirname(igc.image.raw_data.file_names[0])
    
def rot_mi(igc):
    mi = geocal.cib01_mapinfo(igc.resolution_meter())
    loc = igc.loc
    return loc.map_info_rotated(mi)

        
