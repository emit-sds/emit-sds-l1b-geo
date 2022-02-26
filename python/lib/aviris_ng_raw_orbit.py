import geocal
import numpy as np
import os
import re
import math
import struct

class AvirisNgRawOrbit(geocal.OrbitQuaternionList):
    '''This reads the raw gps data. This should perhaps get moved to
    a C++ class at some point, but for right now we just handle the
    reading of the data here.

    This was extracted from the old pyortho code. We may well want to
    clean this up/modify this in the future. But for now we just have
    this quick and dirty code here.

    Note that this code is kind of slow, we are doing low level bit 
    manipulation in python. We can probably speed this up considerable 
    by moving _format_cmigits_words to C++. But for now, this is 
    fast enough, we just process the data once and then save this out in
    some simpler format (e.g., a netcdf or CSV file).
    '''
    # Various constants used by raw GPS file
    SYNC_MSG    = 33279
    NAV_MSG     = 3501
    
    def __init__(self, fname, gps_week=None):
        '''Read the given raw gps file for AVIRIS-NG.

        The GPS week can be passed in explicitly, or we extract this
        from the file name.'''
        self.gps_table, _ = self.read_gps(fname)
        if(not gps_week):
            t = self._fname_to_time(fname)
            gps_week = math.floor(t.gps / (7 * 24 * 60 * 60))
        tm = [geocal.Time.time_gps(gps_week, self.gps_table[i, 0])
              for i in range(self.gps_table.shape[0])]
        pos = [geocal.Geodetic(self.gps_table[i,1],self.gps_table[i,2],
                               self.gps_table[i,3])
               for i in range(self.gps_table.shape[0])]
        # This is pitch, roll, and heading in degrees
        prh = self.gps_table[:,-3:] 
        od = []
        for i in range(len(pos)):
            isecond = i+1
            if(isecond >= len(pos)):
                isecond = i-1
            od.append(geocal.AircraftOrbitData(tm[i],pos[i],
                                               tm[isecond],pos[isecond],
                                               prh[i,1],prh[i,0],prh[i,2]))
        super().__init__(od)

    def _fname_to_time(self, fname):
        '''Extracts out the start time for the file from the filename,
        using the standard AVIRIS-NG file format (e.g., ang20170328t202059_gps).'''
        m = re.search(r'ang(\d{4})(\d{2})(\d{2})t(\d{2})(\d{2})(\d{2})_',
                      os.path.basename(fname))
        if not m:
            raise RuntimeError(f"Don't recognize the file naming convention for {fname}")
        return geocal.Time.parse_time(f"{m[1]}-{m[2]}-{m[3]}T{m[4]}:{m[5]}:{m[6]}Z")
                      

    def _format_cmigits_words(self, words,scale):
        # Note, this seems to be the C-MIGITS INS/GPS System
        # map words into an nbits-sized bitmask in reverse bsig order
        nw    = len(words)
        nbits = nw*16
        bits  = np.zeros(nbits,dtype=np.int8)
        mask  = np.uint32(2**np.arange(16))    
        bsig  = [1,0,3,2] if nw==4 else [1,0]
        for i in range(nw):
            bits[i*16:(i+1)*16] = np.int8((mask & np.uint32(words[bsig[-(i+1)]]))>0)
    
        # flip MSB and accumulate integer value
        bits[-1] = -bits[-1]
        int_exp  = scale-(nbits-1)
        int_out  = (np.float64(bits)*(np.power(2.,np.arange(nbits)))).sum()
        value    = int_out*np.power(2.,int_exp)
    
        return value
    

    def read_gps(self, gps_path, start_line=0, num_lines=99999, smooth=False):
        """
        This if copied from ortho_nav.py in pyortho
        read_gps(gps_path, start_line=0, num_lines=99999)

        Reads table of GPS values from file, optionally skipping 'start_line' initial entries
    
        Arguments:
        - gps_path: path to gps table file
    
        Keyword Arguments:
        - start_line: number of lines to skip (default=0)
        - num_lines: maximum number of lines to read beyond 'start_line' (default=99999)
    
        Returns:
        - gps_table: msg_read x 7 gps table
        - velocities: The velocities
        """
    
        msg_read = 0
        msg_skipped = 0
        locations = np.array([],dtype=np.double)
        velocities = np.array([],dtype=np.double)
        gps_size = os.path.getsize(gps_path)
        file_done=False
        with open(gps_path,'rb') as f:
            while not file_done:
                header=np.fromfile(f,count=5,dtype='<u2')
                if len(header)<5:
                    return locations,velocities

                if header[0] != self.SYNC_MSG:
                    f.seek(-9,os.SEEK_CUR) # backup by (5*2)-1 to read even/odd byte msgs
                    continue            
            
                msg_bytes=2*(header[2]+1)
                if f.tell()+msg_bytes > gps_size:
                    # truncated message, return everything up until now
                    warn('Truncated GPS message encountered, returning valid messages')
                    return locations,velocities
                if header[1] == self.NAV_MSG:
                    if msg_skipped < start_line:
                        f.seek(msg_bytes,os.SEEK_CUR)
                        msg_skipped+=1
                    else:
                        gpsdata = np.fromfile(f,count=4,dtype='<u2')
                        gpstime = self._format_cmigits_words(gpsdata,20)

                        posdata = np.fromfile(f,count=6,dtype='<u2')
                        lat     = self._format_cmigits_words(posdata[0:2],0)*180.0
                        lon     = self._format_cmigits_words(posdata[2:4],0)*180.0
                        alt     = self._format_cmigits_words(posdata[4:6],15)

                        vecdata = np.fromfile(f,count=6,dtype='<u2')
                        vnorth  = self._format_cmigits_words(vecdata[0:2],10)
                        veast   = self._format_cmigits_words(vecdata[2:4],10)
                        vup     = self._format_cmigits_words(vecdata[4:6],10)

                        ortdata = np.fromfile(f,count=6,dtype='<u2')
                        pitch   = self._format_cmigits_words(ortdata[0:2],0)*180.0
                        roll    = self._format_cmigits_words(ortdata[2:4],0)*180.0
                        heading = self._format_cmigits_words(ortdata[4:6],0)*180.0
                        data_checksum=np.fromfile(f,count=1,dtype='<u2')
                        if len(data_checksum)==0:
                            file_done=True
                        elif(abs(np.float32([lat,lon,pitch,roll,heading])) <= 180.0).all():
                            l_location = np.float64(np.c_[gpstime,lat,lon,alt,pitch,roll,heading])
                            l_velocity = np.float64(np.c_[vnorth,veast,vup])
                            if msg_read != 0:
                                locations = np.r_[locations,l_location]
                                velocities = np.r_[velocities,l_velocity]
                            else:
                                locations = l_location
                                velocities = l_velocity
                            msg_read+=1
                            if msg_read >= num_lines:
                                return locations,velocities
                        else:
                            warn('bad GPS data at msg %d'%msg_read)
                            return locations,velocities
                elif msg_bytes > 0:
                    f.seek(msg_bytes,os.SEEK_CUR)
        if smooth:
            locations = smoothaxis(locations,axis=0)
              
        return locations,velocities

__all__ = ["AvirisNgRawOrbit",]    
