from emit import gaussian_stretch
import geocal


def test_gaussian_stretch(isolated_dir, l1b_rdn_fname):
    ras = geocal.GdalRasterImage(str(l1b_rdn_fname))
    d = gaussian_stretch(ras.read_all_double())
    f = geocal.VicarRasterImage("d_stretch.img", "BYTE", d.shape[0], d.shape[1])
    print(d.min())
    print(d.max())
    f.write(0, 0, d)
