import geocal
import geocal

class AvirisNgIgm:
    '''Small helper class that handles reading the AVIRIS NG IGM
    and returning the ground location from this file.

    This is in UTM, and we need to know the zone. We could parse this
    from the description, but for now it is just easier to pass this in
    directly. We don't have a lot of this kind of data, so not worth
    spending too much time on this.

    I'm *pretty* sure the height is relative to WGS-84 rather than the
    datum. Error is small, and since this is pretend test data perhaps
    it doesn't matter so much
    '''
    def __init__(self, igm_fname, utm_zone):
        # We use a GdalMultiBand here just for convenience. It just
        # figures out the shape etc. for us from the hdr file
        self.data = geocal.GdalMultiBand(igm_fname).read_all_double()
        self.utm_zone = utm_zone
        # Map to EPSG number. Can look this up online at
        # http://www.epsg-registry.org
        if(utm_zone < 0):
            self.ogrw = geocal.OgrWrapper.from_epsg(32700 + abs(utm_zone))
        else:
            self.ogrw = geocal.OgrWrapper.from_epsg(32600 + abs(utm_zone))
            
        
    @property 
    def shape(self):
        return (self.data.shape[1], self.data.shape[2])

    def __getitem__(self, key):
        east, north, elv = self.data[:,key[0],key[1]]
        return geocal.OgrCoordinate(self.ogrw, east, north, elv)
        
__all__ = ["AvirisNgIgm"]
