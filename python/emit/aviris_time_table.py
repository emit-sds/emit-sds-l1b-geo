import geocal
from pathlib import Path


class AvirisTimeTable(geocal.MeasuredTimeTable):
    """This create a time table from an AVIRIS obs file. We get the day
    from parsing the file name, and the time of each line from the
    UTC hour found in band 10 of the file.

    Note that the file name must match the AVIRIS standard naming,
    so we can get the day going with the UTC hour.

    This has nothing directly to do with EMIT, but since some of our
    test data is based on AVIRIS it is useful to be able to read this.

    AVIRIS is a whisk broom, so the pixels aren't actually acquired all
    at the same time. The time reported here for the line is actually the
    time of the middle pixel. EMIT is not a whiskbroom, so for the purposes
    of providing test data I think we can ignore the whiskbroom aspect of
    the instrument and "pretend" that the scanline is collected all at the
    same time.
    """

    def __init__(self, obs_fname):
        t = str(Path(obs_fname).name)
        t0 = geocal.Time.parse_time(f"20{t[1:3]}-{t[3:5]}-{t[5:7]}T00:00:00Z")
        # The UTC hour is band 10
        d = geocal.GdalRasterImage(str(obs_fname), 10).read_all_double()
        tm = geocal.Vector_Time()
        for i in range(d.shape[0]):
            tm.push_back(t0 + d[i, 0] * 3600)
        super().__init__(tm)


__all__ = [
    "AvirisTimeTable",
]
