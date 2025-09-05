from .misc import file_name_to_gps_week
import logging
import numpy as np
import geocal
import os
import struct
import scipy.interpolate

logger = logging.getLogger("l1b_geo_process.avirs_ng_raw")


class AvirisNgRaw:
    """This is used to read the metadata from the raw AVIRIS-NG files.
    We don't actually care about most of this, instead we just want to
    extract the frame metadata.

    The file is a ENVI format file, with the metadata in the first band
    (e.g., this isn't actually DN data).

    We extract out the clock values, and the obcv.

    The clock values are integers which corresponds to a actual time
    the data was acquired. The clock value maps to the PPS file, which
    gives the gps time for particular clock values. So the clock values
    can't really be interpreted as anything meaningful without the PPS file,
    basically this are just "ticks".

    The obcv gives the type of data collected for a particular line, we
    are interested in the OBC_SCIENCE values.
    """

    OBC_DARK1 = 2
    OBC_SCIENCE = 3
    OBC_DARK2 = 4
    OBC_BRIGHTMED = 5
    OBC_BRIGHTHI = 6
    OBC_LASER = 7

    def __init__(self, fname, chunk_size=2000):
        """This reads the given fname to get the clock and obc values.
        The data files tend to be big, we read it with the given chunking
        size."""
        self.file_name = fname
        f = geocal.GdalRasterImage(self.file_name)
        logger.info("Reading the raw file %s", self.file_name)
        self.clock = np.zeros((f.number_line,), dtype=np.int64)
        self.obc = np.zeros_like(self.clock, dtype=np.uint16)
        for i in range(0, self.clock.shape[0], chunk_size):
            r = range(i, min(i + chunk_size, self.clock.shape[0]))
            logger.debug("Reading line %d of %d", i, self.clock.shape[0])
            d = f.read(r.start, 0, len(r), 2)
            self.clock[r] = d[:, 0].astype(np.int64) << 16 | d[:, 1]
            d = f.read(r.start, 321, len(r), 1)
            self.obc[r] = d[:, 0] >> 8

    def clock_science(self, img_sl=800):
        """Return all the clock values when we are in science mode. Note
        that is isn't line averaged yet, so normally you would only use these
        values for figuring out the line_average"""
        return self.clock[img_sl:][self.obc[img_sl:] == self.OBC_SCIENCE]

    def clock_average(self, img_sl=800, line_average=9):
        """The processing averages a given number of lines.

        We also trim off the start of raw data, I'm guessing there is
        just some garbage here. This value came from the config file
        in the pyortho code.

        The science data is averaged when the radiance data is
        generated (which we don't do here). The time for the averaged
        data is just the average of the times that make up the lines
        that were averaged.
        """
        self.img_sl = img_sl
        self.line_average = line_average
        clock_sci = self.clock_science(img_sl=img_sl)
        clock_avg = []
        for i in range(0, len(clock_sci), self.line_average):
            if i + self.line_average <= len(clock_sci):
                clock_avg.append(clock_sci[i : i + self.line_average].mean())
        return np.array(clock_avg)


class AvirisCMigitsFile:
    """Helper class used to read data in the C-MIGITS format."""

    SYNC_MSG = 33279
    NAV_MSG = 3501

    def __init__(self, fname):
        """Open the given file for reading."""
        self.file_name = fname
        self.file_size = os.path.getsize(self.file_name)
        self.fh = open(self.file_name, "rb")

    def can_read(self, nbytes):
        """Return True if we have enough data left in the file to read
        fh bytes."""
        return self.fh.tell() + nbytes <= self.file_size

    def read_int64(self, count=1):
        """Read a int64 value."""
        # C-MIGITS int64 is kind of odd. It is little endian, except
        # there is an extra swap of the first 2 words with the second two.
        res = np.zeros((count,), dtype=np.int64)
        for i in range(count):
            t = self.fh.read(8)
            res[i] = struct.unpack("<q", t[4:] + t[:4])[0]
        return res

    def read_int32(self, count=1):
        return struct.unpack(f"<{count}i", self.fh.read(4 * count))

    def read_uint16(self, count=1):
        return struct.unpack(f"<{count}H", self.fh.read(2 * count))

    def read_clock(self, count=1):
        res = np.zeros((count,), dtype=np.int64)
        for i in range(count):
            msw, lsw = struct.unpack("<2H", self.fh.read(2 * 2))
            res[i] = np.int64(msw) << 16 | lsw
        return res

    def skip(self, nbytes):
        self.fh.seek(nbytes, os.SEEK_CUR)

    def scale_factor(self, scale, nbits, scalar=1.0):
        """A lot of the data is scaled by a 'scale' value, which is a number
        of bits. The overall factor is a combination of the scale value, the
        number of bits of the data being scaled, and a scalar.

        Kind of an odd way to represent the data, but this is the way
        it is done."""
        return np.power(2.0, scale - (nbits - 1)) * scalar


class AvirisNgGpsTable:
    """Class used to read the raw "_gps" file."""

    def __init__(self, fname, smooth=False):
        self.file_name = fname
        gpstime = []
        # This is [lat, lon, alt, vnorth, veast, vup, pitch, roll, heading]
        data = []
        f = AvirisCMigitsFile(self.file_name)
        while f.can_read(5 * 2):
            header = f.read_uint16(count=5)
            if header[0] != f.SYNC_MSG:
                # backup by (5*2)-1 to read even/odd byte msgs
                f.skip(-9)
                continue

            msg_bytes = 2 * (header[2] + 1)
            if not f.can_read(msg_bytes):
                # truncated message, return everything up until now
                break
            if header[1] == f.NAV_MSG:
                gpstime.append(f.read_int64(count=1)[0])
                data.append(f.read_int32(count=9))
                # data_checksum=f.read_uint16(count=1)
            elif msg_bytes > 0:
                f.skip(msg_bytes)
        # Scale the integer data to float
        gpstime = np.array(gpstime, dtype=np.float64) * f.scale_factor(20, 64)
        data = np.array(data, dtype=np.float64)
        lat = data[:, 0] * f.scale_factor(0, 32, 180.0)
        lon = data[:, 1] * f.scale_factor(0, 32, 180.0)
        alt = data[:, 2] * f.scale_factor(15, 32)
        vnorth = data[:, 3] * f.scale_factor(10, 32)
        veast = data[:, 4] * f.scale_factor(10, 32)
        vup = data[:, 5] * f.scale_factor(10, 32)
        pitch = data[:, 6] * f.scale_factor(0, 32, 180.0)
        roll = data[:, 7] * f.scale_factor(0, 32, 180.0)
        heading = data[:, 8] * f.scale_factor(0, 32, 180.0)
        self.gps_table = np.stack(
            [gpstime, lat, lon, alt, pitch, roll, heading], axis=-1
        )
        self.velocities = np.stack([vnorth, veast, vup], axis=-1)
        if smooth:
            raise NotImplementedError("We don't support smooth")
            # We don't actually have this in place. Not sure that
            # we need this, but if we do we should get this from
            # pyortho
            # self.gps_table = smoothaxis(self.gps_table,axis=0)


class AvirisNgPpsTable:
    """Class for reading the raw _pps file. This contains a number
    of time points, giving the time in gpstime and clock ticks, which
    we can use to relate the AVIRIS lines (with time measured in clock ticks)
    to gpstime (used by things like AvirisNgGpsTable).

    In addition to pps_table, this has clock_to_gpstime which can be
    use to interpolate a clock value to the corresponding gpstime value
    (note that the gpstime is the gps offset for the gps week, you need to
    also have the gps week to convert to a GeoCal time (see AvirisNgTimeTable
    for an example of this)."""

    def __init__(self, fname, msg_words=13, gps_week=None, smooth=False):
        """Read the given file."""
        self.file_name = fname
        self.gps_week = gps_week
        if not self.gps_week:
            self.gps_week = file_name_to_gps_week(fname)
        f = AvirisCMigitsFile(fname)
        gpstime = []
        cnt = []
        clock = []
        while f.can_read(msg_words * 2):
            header = f.read_uint16(count=5)
            if header[0] != f.SYNC_MSG:
                # Skip to next message
                f.skip((msg_words - 5) * 2)
                continue
            gpstime.append(f.read_int64(count=1)[0])
            cnt.append(f.read_uint16(count=1)[0])
            clock.append(f.read_clock(count=1)[0])
            f.skip(msg_words * 2 - (5 * 2 + 1 * 8 + 1 * 2 + 1 * 4))
        gpstime = np.array(gpstime, dtype=np.float64) * f.scale_factor(20, 64)
        mask_14bit = np.uint32(0x3FFF)
        cnt = (np.array(cnt, dtype=np.int32) & mask_14bit).astype(np.float64)
        clock = np.array(clock, dtype=np.float64)
        self.pps_table = np.stack([gpstime, clock, cnt], axis=-1)
        if smooth:
            raise NotImplementedError("We don't support smooth")
            # We don't actually have this in place. Not sure that
            # we need this, but if we do we should get this from
            # pyortho
            # self.pps_table = smoothaxis(self.pps_table,axis=0)
        self.clock_to_gpstime = scipy.interpolate.interp1d(
            self.pps_table[:, 1], self.pps_table[:, 0]
        )

    def clock_to_time(self, clock):
        """Convert from the 'clock' value to a geocal time. Clock can either
        be a array/list like object, or a single value."""
        gtime = self.clock_to_gpstime(clock)
        if len(gtime.shape) == 0:
            return geocal.Time.time_gps(self.gps_week, gtime[()])
        return [geocal.Time.time_gps(self.gps_week, g) for g in gtime]


__all__ = ["AvirisNgRaw", "AvirisCMigitsFile", "AvirisNgGpsTable", "AvirisNgPpsTable"]
