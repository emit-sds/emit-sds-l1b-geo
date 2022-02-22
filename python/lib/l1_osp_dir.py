import importlib.util

class L1OspDir:
    '''This class handles the L1OspDir, such as reading the l1b_geo_config
    file.'''
    def __init__(self, l1_osp_dir):
        self.l1_osp_dir = l1_osp_dir
        self.load_config()

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
        
