from emit import L1OspDir
import pickle


def test_l1_osp_dir(test_data, isolated_dir):
    t = L1OspDir(test_data / "l1_osp_dir")
    print(t.l1b_geo_config.pge_name)
    pickle.dump(t, open("test.pkl", "wb"))
    t2 = pickle.load(open("test.pkl", "rb"))
    print(t2.l1b_geo_config.pge_name)
