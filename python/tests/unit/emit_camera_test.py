from emit import EmitCamera


def test_emit_camera(orbit_fname):
    cam = EmitCamera()
    assert cam.number_sample(0) == 1280
