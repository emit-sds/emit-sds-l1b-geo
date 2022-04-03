import importlib.util
import geocal
import numpy as np

class L1OspDir:
    '''This class handles the L1OspDir, such as reading the l1b_geo_config
    file.'''
    def __init__(self, l1_osp_dir):
        self.l1_osp_dir = l1_osp_dir
        self.load_config()

    def __getattr__(self, name):
        '''Forward attributes to the l1b_geo_config if it is found there.'''
        if(hasattr(self.l1b_geo_config, name)):
            return getattr(self.l1b_geo_config,name)
        raise AttributeError

    def camera(self):
        cam = geocal.read_shelve(self.l1_osp_dir + "/camera.xml")
        # We store the euler angles and focal length separately, so we can
        # more easily update this. Get the updated values from the
        # config file.
        
        # We have used both GlasGfm and CameraParaxial as a camera. They
        # have the camera angles expressed differently
        if(hasattr(cam, "euler")):
            cam.euler = self.instrument_to_sc_euler
        else:
            cam.angoff = [self.instrument_to_sc_euler[2],
                          self.instrument_to_sc_euler[1],
                          self.instrument_to_sc_euler[0]]
        cam.focal_length = self.camera_focal_length
        return cam

    def load_config(self):
        spec = importlib.util.spec_from_file_location("l1b_geo_config",
                                        self.l1_osp_dir + "/l1b_geo_config.py")
        self.l1b_geo_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.l1b_geo_config)

    def __getstate__(self):
        return {'l1_osp_dir' : self.l1_osp_dir}

    def __setstate__(self, state):
        self.l1_osp_dir = state['l1_osp_dir']
        self.load_config()
        
