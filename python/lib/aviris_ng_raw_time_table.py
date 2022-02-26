import os
import numpy as np
import math
import re
import geocal
import scipy.interpolate

class AvirisNgRawTimeTable:
    SYNC_MSG    = 33279
    g_14bit_mask  = np.uint32(2**14-1)

    def __init__(self, fname, gps_week=None):
        '''Read the given raw pps file for AVIRIS-NG.

        The GPS week can be passed in explicitly, or we extract this
        from the file name.'''
        # This comes from ortho_platform.py in pyortho. For AVIRIS-NG,
        # the number of message words is 13. I don't think this will change,
        # but if we get weird results perhaps this should be 14. Perhaps
        # we should move this into the l1_osp_dir files.
        msg_words = 13
        self.gps_week = gps_week
        if(not self.gps_week):
            t = self._fname_to_time(fname)
            self.gps_week = math.floor(t.gps / (7 * 24 * 60 * 60))
        self.pps_table = self.read_pps(fname, msg_words)
        self.clock_to_gpstime = scipy.interpolate.interp1d(self.pps_table[:,1],
                                                           self.pps_table[:,0])
        

    def clock_to_time(self, clock):
        '''Convert from the 'clock' value to a geocal time.'''
        return geocal.Time.time_gps(self.gps_week,
                                    self.clock_to_gpstime(clock)[()])
    
    def _fname_to_time(self, fname):
        '''Extracts out the start time for the file from the filename,
        using the standard AVIRIS-NG file format (e.g., ang20170328t202059_gps).'''
        m = re.search(r'ang(\d{4})(\d{2})(\d{2})t(\d{2})(\d{2})(\d{2})_',
                      os.path.basename(fname))
        if not m:
            raise RuntimeError(f"Don't recognize the file naming convention for {fname}")
        return geocal.Time.parse_time(f"{m[1]}-{m[2]}-{m[3]}T{m[4]}:{m[5]}:{m[6]}Z")

    def _format_clock_words(self,msw,lsw):
        return (np.int64(msw)<<16)+lsw

    def _extract_fc(self, word):
        # applies 14 bit mask to extract frame count from 16-bit pps/gps word
        return np.bitwise_and(self.g_14bit_mask, np.int32(word))
        
    # Note this is a duplicate of the function in AvirisNgRawOrbit.
    # Should probably combine these somehow, but for now just duplicate
    # for simplicity. Any updates to this should get propagated to
    # AvirisNgRawOrbit.
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
        

    def read_pps(self, pps_path, msg_words=13, start_line=0, num_lines=99999,
                 smooth=False):
        """
        read_pps(pps_path, msg_words, start_line=0) 
    
        Arguments:
        - pps_path: path to pps table file
        - msg_words: number of words in message (13 or 14)
    
        Keyword Arguments:
        - start_line: start line = number of lines to skip (default=0)
        - num_lines: maximum number of lines to read beyond 'start_line' (default=99999)
    
        Returns:
        - pps_table: msg_read x 3 pps table file
        """
    
        msg_read = 0
        time_table = np.array([],dtype=np.double)
        pps_size = os.path.getsize(pps_path)
        msg_bytes = 2*msg_words
        nr = math.floor(pps_size/msg_bytes)
        nl_max = min(nr,num_lines)

        with open(pps_path,'rb') as f:
            # traverse file with sliding window to find sync message
            bytec = 0
            while np.fromfile(f,count=1,dtype='<u2') != self.SYNC_MSG:
                if bytec >= pps_size:
                    raise RuntimeError('PPS file contains no sync messages')
                # back up one byte to search every 2-byte string for sync_msg
                f.seek(-1,os.SEEK_CUR) 
                bytec += 1

            # found first sync_msg, back up to sync position
            f.seek(-2,os.SEEK_CUR)

            if start_line > 0:
                f.seek(start_line*msg_bytes,os.SEEK_CUR)
                if f.tell() >= pps_size:
                    return time_table
        
            # read messages until we get a sync header or an empty buffer
            time_table = []
            while msg_read < nl_max:
                if f.tell()+msg_bytes > pps_size: # truncated file, return what we have
                    warn('PPS table contains truncated messages')
                    break
                buf=np.fromfile(f,count=msg_words,dtype='<u2')
                if len(buf) < msg_words:
                    warn('PPS message %d truncated'%(msg_read+1))
                    break
                elif buf[0] != self.SYNC_MSG:
                    warn('Expected PPS synchronization word not found')
                    break            
                elif np.int16(buf[:4]).sum()+buf[4] != 0:
                    warn('PPS message %d checksum failed'%(msg_read+1))
                    break

                gpsdata = np.int64(buf[5:9]) #buf[[5,6,7,8]]
                gpstime = self._format_cmigits_words(gpsdata,20)
                count   = np.float64(self._extract_fc(buf[9]))
                frtc    = np.float64(self._format_clock_words(buf[10],buf[11]))
                l_time  = np.c_[gpstime,frtc,count]
            
                if len(time_table)>0:
                    time_table=np.r_[time_table,l_time]
                else:
                    time_table=l_time
                msg_read+=1
            
        if smooth:
            time_table = smoothaxis(time_table,axis=0)
            
        return time_table
    
