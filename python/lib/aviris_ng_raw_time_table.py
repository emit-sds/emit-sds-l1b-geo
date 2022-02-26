import os
import numpy as np

class AvirisNgRawTimeTable:
    def __init__(self):
        pass

    def read_pps(pps_path, msg_words, start_line=0, num_lines=99999,
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
        nr = floor(pps_size/msg_bytes)
        nl_max = min(nr,num_lines)

        with open(pps_path,'rb') as f:
            # traverse file with sliding window to find sync message
            bytec = 0
            while np.fromfile(f,count=1,dtype='<u2') != SYNC_MSG:
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
                elif buf[0] != SYNC_MSG:
                    warn('Expected PPS synchronization word not found')
                    break            
                elif np.int16(buf[:4]).sum()+buf[4] != 0:
                    warn('PPS message %d checksum failed'%(msg_read+1))
                    break

                gpsdata = np.int64(buf[5:9]) #buf[[5,6,7,8]]
                gpstime = self._format_cmigits_words(gpsdata,20)
                count   = np.float64(extract_fc(buf[9]))
                frtc    = np.float64(format_clock_words(buf[10],buf[11]))
                l_time  = np.c_[gpstime,frtc,count]
            
                if len(time_table)>0:
                    time_table=np.r_[time_table,l_time]
                else:
                    time_table=l_time
                msg_read+=1
            
        if smooth:
            time_table = smoothaxis(time_table,axis=0)
            
        return time_table
    
