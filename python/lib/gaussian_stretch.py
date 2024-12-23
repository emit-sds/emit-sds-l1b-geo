from geocal import VicarInterface, VicarRasterImage, mmap_file
import numpy as np

class GaussianStretch(VicarInterface):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.timing = False
        self.cmd = "stretch in.img out.img 'gauss DNMIN=0 DNMAX=255"

    def pre_run(self):
        t = VicarRasterImage("in.img", "HALF", self.data.shape[0],
                             self.data.shape[1])
        t = None
        d = mmap_file("in.img", mode="r+")
        d[:] = np.where(self.data > 0,
                        self.data * 32768.0 / max(self.data.max(), 1e-8),
                        0).astype(np.int16)
        self.run_out = ""

    def post_run(self):
        self.out = VicarRasterImage("out.img").read_all()
        
def gaussian_stretch(data):
    '''This does histogram equalization on the given data, doing a Gaussian 
    stretch.

    Currently this uses the vicar program 'stretch'. We could probably move
    this all into python, but there seems little point.
    
    We assume that all negative values are fill, and map them to 0. Data is
    returned as integer data.'''
    # Special handling for all 0 data, stretch fails so just return
    # the original data
    if(data.max() == 0):
        return data
    gs = GaussianStretch(data)
    gs.vicar_run()
    return gs.out

__all__ = ["gaussian_stretch"]

