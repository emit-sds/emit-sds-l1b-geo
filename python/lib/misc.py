# This is various miscellaneous routines that don't fit elsewhere
import geocal
import os

def create_dem(config):
    '''Create the SRTM DEM based on the configuration. Don't exactly know
    how this will work once we are integrated in with SDS, but for now
    just use the placeholder function and grab the information from the
    environment.'''
    datum = os.environ["AFIDS_VDEV_DATA"] + "/EGM96_20_x100.HLF"
    srtm_dir = os.environ["ELEV_ROOT"]
    dem = geocal.SrtmDem(srtm_dir,False, geocal.DatumGeoid96(datum))
    return dem

def ortho_base_directory(config):
    '''Create the ortho base. In production, take the directory passed in
    from the configuration file. But for testing, if ECOSTRESS_USE_AFIDS_ENV
    is defined then look for the location of this on pistol'''
    ortho_base_dir = os.path.abspath(config["StaticAncillaryFileGroup",
                                            "OrthoBase"])
    if("ECOSTRESS_USE_AFIDS_ENV" in os.environ):
        # Location on pistol, use if found, otherwise use setting in
        # run config file
        if(os.path.exists("/raid22/band5_VICAR")):
            ortho_base_dir = "/raid22"
        elif(os.path.exists("/data/smyth/Landsat/band5_VICAR")):
            ortho_base_dir = "/data/smyth/Landsat"
    return ortho_base_dir

def band_to_landsat_band(lband):
    '''Map number to the enumeration in C++'''
    if(lband == 1):
        return geocal.Landsat7Global.BAND1
    elif(lband == 2):
        return geocal.Landsat7Global.BAND2
    elif(lband == 3):
        return geocal.Landsat7Global.BAND3
    elif(lband == 4):
        return geocal.Landsat7Global.BAND4
    elif(lband == 5):
        return geocal.Landsat7Global.BAND5
    elif(lband == 61):
        return geocal.Landsat7Global.BAND61
    elif(lband == 62):
        return geocal.Landsat7Global.BAND62
    elif(lband == 7):
        return geocal.Landsat7Global.BAND7
    elif(lband == 8):
        return geocal.Landsat7Global.BAND8
    else:
        raise RuntimeError("Unrecognized band number")

def aster_mosaic_dir():
    '''The ASTER Mosaic data. We only use this for simulation (so not
    used in production.'''
    return "/bigdata/smyth/AsterMosaic"

def aster_radiance_scale_factor():
    '''Return the ASTER scale factors. This is for L1T data, found at
    https://lpdaac.usgs.gov/dataset_discovery/aster/aster_products_table/ast_l1t
    Our mosiac actually had adjustments made to make a clean mosaic, but this
    should be a reasonable approximation for going from the pixel integer data
    to radiance data in W/m^2/sr/um.

    Note from https://lpdaac.usgs.gov/data/get-started-data/collection-overview/missions/aster-overview/#aster-spectral-bands the ASTER bands are:

    1  0.52-0.60 micrometer
    2  0.63-0.69
    3  0.78 - 0.86
    4  1.600 - 1.700
    5  2.145  - 2.185
    6  2.185 - 2.225
    7  2.235 - 2.285
    8  2.295 - 2.365
    9  2.360 - 2.430
    10 8.125 - 8.475
    11 8.475 - 8.825
    12 8.925 - 9.275
    13 10.25 - 10.95
    14 10.95 - 11.65
    '''
    return [1.688, 1.415, 0.862, 0.2174, 0.0696, 0.0625, 0.0597, 0.0417, 0.0318,
            6.882e-3, 6.780e-3, 6.590e-3, 5.693e-3, 5.225e-3]

