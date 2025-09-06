from emit import AvirisNgObs


def test_aviris_ng_obs(aviris_ng_full_test_data):
    obs = AvirisNgObs(aviris_ng_full_test_data / "ang20170323t202244_obs")
    print(obs.utc_time[0, 0])
