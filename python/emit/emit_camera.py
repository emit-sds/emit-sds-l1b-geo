import geocal

class EmitCamera(geocal.SimpleCamera):
    '''EMIT camera. Right now this is just a wrapper around a generic
    GeoCal SimpleCamera. We can extend
    this to a full C++ class if there is any need.'''
    def __init__(self):
        # Simple pinhole camera, we'll replace with the calibrated camera
        focal_length = 193.5e-3
        line_pitch = 30e-6
        sample_pitch = 30e-6
        nsamp = 1280
        spectral_channel = 324
        super().__init__(0,0,0,focal_length, line_pitch, sample_pitch,
                         1, nsamp)
        
__all__ = ["EmitCamera", ]
