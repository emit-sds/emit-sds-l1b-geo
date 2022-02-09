# This create the AVIRIS-NG end to end test data.
# See the README.md file for how we captured the data that we generated as the
# input to this.

from geocal import *
from emit import *
import pickle
import math
import re
import scipy
from multipolyfit import multipolyfit
import pandas as pd

# While developing we run this multiple times. Skip things we already
# have
CREATE_ORBIT = False
CREATE_CAMERA_STEP1 = False
CREATE_CAMERA_STEP2 = False
CREATE_CAMERA_STEP3 = False
CREATE_SCENE = True

emit_test_data = "/home/smyth/Local/emit-test-data/latest"
input_test_data = f"{emit_test_data}/input_afids_ng"

orbit = 90000
end_fname = "b001_v01"
nline_per_scene = 1280

# This is zone_alpha, but with "S" changed to "N" - I think the data
# is actually wrong here
utm_zone = 11

if CREATE_ORBIT:
    fname = f"{input_test_data}/pyortho_20170328t202059.pkl"
    # The "bytes" here is needed because we pickled using python 2.7. See
    # https://groups.google.com/g/sage-devel/c/nLG8zMSKSD0
    frame_meta, gpstime, filedate, zone_alpha = pickle.load(open(fname, "rb"), encoding="bytes")
    filedate = Time.parse_time(filedate.decode('utf-8'))
    gps_week = math.floor(filedate.gps / (7 * 24 * 60 * 60))
    line_time = [Time.time_gps(gps_week,t) for t in gpstime]
    if(utm_zone < 0):
        ogrw = OgrWrapper.from_epsg(32700 + abs(utm_zone))
    else:
        ogrw = OgrWrapper.from_epsg(32600 + abs(utm_zone))
    pos = [OgrCoordinate(ogrw,*frame_meta[i,1:4]) for i in range(frame_meta.shape[0])]
    # This is pitch, roll, and heading in degrees
    prh = frame_meta[:,-3:] * rad_to_deg
    od = []
    for i in range(len(pos)):
        isecond = i+1
        if(isecond >= len(pos)):
            isecond = i-1
        od.append(AircraftOrbitData(line_time[i],pos[i],
                                    line_time[isecond],pos[isecond],
                                    prh[i,1],prh[i,0],prh[i,2]))
    orb = OrbitQuaternionList(od)
    write_shelve("orb_aviris.xml", orb)
    tm = orb.min_time
    dstring2 = re.sub(r'T', 't', re.sub(r'[-:]', '',
                                        re.split(r'\.', str(tm))[0]))
    fname = "emit%s_o%05d_l1a_att_%s.nc" % (dstring2, orbit, end_fname)
    EmitOrbit.write_file2(f"{emit_test_data}/{fname}", orb)
    tt = MeasuredTimeTable(line_time)
    fname = "emit%s_o%05d_l1a_line_time_full_%s.nc" % (dstring2, orbit, end_fname)
    EmitTimeTable.write_file(f"{emit_test_data}/{fname}", tt)

tt_full =  EmitTimeTable(glob.glob(f"{emit_test_data}/emit*_o90000_l1a_line_time_full_b001_v01.nc")[0])
orb = EmitOrbit(glob.glob(f"{emit_test_data}/emit*_o90000_l1a_att_b001_v01.nc")[0])

# This initial camera has the pointing updated, but doesn't have the
# nonlinearites in place yet. We do this first step and save the data.
def residual1(x0, igc, igm):
    igc.ipi.camera.parameter_subset = x0
    res = []
    #for ln in range(500,igm.shape[0],500):
    for ln in (1000,):
        for smp in range(0,igm.shape[1], 10):
            ic = igc.image_coordinate(igm[ln,smp])
            res.append(ic.line - ln)
            res.append(ic.sample - smp)
    return res

if CREATE_CAMERA_STEP1:
    igm = AvirisNgIgm(f"{input_test_data}/ang20170328t202059_rdn_igm", utm_zone)
    cam = CameraParaxial(Quaternion_double(1,0,0,0), 1, 598,
                         27e-3,27e-3,27.5,FrameCoordinate(0.5,598/2),
                         CaptureParaxialTransform())
    cam.fit_epsilon = True
    cam.fit_beta = True
    cam.fit_delta = True
    cam.fit_focal_length = True
    cam.fit_line_pitch = False
    cam.fit_sample_pitch = False
    cam.fit_principal_point_line(False, 0)
    cam.fit_principal_point_sample(False, 0)
    write_shelve("aviris_cam_step1.xml", cam)
    dem = SimpleDem()
    ipi = Ipi(orb, cam, 0, tt_full.min_time, tt_full.max_time, tt_full)
    igc = IpiImageGroundConnection(ipi, dem, None)
    x0 = cam.parameter_subset
    print(residual1(x0,igc, igm))
    r = scipy.optimize.least_squares(residual1, x0, args=(igc,igm))
    print(r)
    print(residual1(cam.parameter_subset, igc, igm))
    cam.paraxial_transform.clear()
    write_shelve("aviris_cam_step1.xml", cam)

# Determine nonlinearities. We do this for one line, and assume this will
# be the same for other lines
ln = 1000
if CREATE_CAMERA_STEP2:
    cam = read_shelve("aviris_cam_step1.xml")
    dem = SimpleDem()
    ipi = Ipi(orb, cam, 0, tt_full.min_time, tt_full.max_time, tt_full)
    igc = IpiImageGroundConnection(ipi, dem, None)
    if(not os.path.exists("paraxial_data.pkl")):
        igm = AvirisNgIgm(f"{input_test_data}/ang20170328t202059_rdn_igm", utm_zone)
        cam.paraxial_transform.clear()
        for smp in range(igm.shape[1]):
            print("Sample: ", smp)
            gc = igc.ground_coordinate_approx_height(ImageCoordinate(ln, smp),
                               igm[ln,smp].height_reference_surface)
            igc.collinearity_residual(igm[ln,smp],ImageCoordinate(ln,smp))
        predict_x = np.array(cam.paraxial_transform.predict_x)
        predict_y = np.array(cam.paraxial_transform.predict_y)
        real_x = np.array(cam.paraxial_transform.real_x)
        real_y = np.array(cam.paraxial_transform.real_y)
        pred = np.empty((predict_x.shape[0], 2))
        pred[:,0] = predict_x
        pred[:,1] = predict_y
        real = np.empty((real_x.shape[0], 2))
        real[:,0] = real_x
        real[:,1] = real_y
        pickle.dump([pred, real], open("paraxial_data.pkl", "wb"))
    pred,real=pickle.load(open("paraxial_data.pkl", "rb"))
    pixel_size = cam.line_pitch
    # Determine the needed polynomial order by just testing a
    # given deg
    deg = 5
    mo = multipolyfit(real, pred[:,0], deg, model_out=True)
    print("Real to predict x max error (pixel) ",
          abs(np.array([(mo(*real[i,:]) - pred[i,0]) / pixel_size for i in range(real.shape[0])])).max())
    mo = multipolyfit(real, pred[:,1], deg, model_out=True)
    print("Real to predict y max error (pixel) ",
          abs(np.array([(mo(*real[i,:]) - pred[i,1]) / pixel_size for i in range(real.shape[0])])).max())
    mo = multipolyfit(pred, real[:,0], deg, model_out=True)
    print("Predict to real x max error (pixel) ",
          abs(np.array([(mo(*pred[i,:]) - real[i,0]) / pixel_size for i in range(real.shape[0])])).max())
    mo = multipolyfit(pred, real[:,1], deg, model_out=True)
    print("Predict to real y max error (pixel) ",
          abs(np.array([(mo(*pred[i,:]) - real[i,1]) / pixel_size for i in range(real.shape[0])])).max())

    # Print out powers so we know how to interpret the polynomial coefficients.
    t, powers = multipolyfit(pred, real[:,1], deg, powers_out=True)
    print(powers)
    
    tran = PolynomialParaxialTransform_5d_5d()
    tran.real_to_par[0,:] = multipolyfit(real, pred[:,0], deg)
    tran.real_to_par[1,:] = multipolyfit(real, pred[:,1], deg)
    tran.par_to_real[0,:] = multipolyfit(pred, real[:,0], deg)
    tran.par_to_real[1,:] = multipolyfit(pred, real[:,1], deg)
    tran.min_x_real = real[:,0].min()
    tran.max_x_real = real[:,0].max()
    tran.min_y_real = real[:,1].min()
    tran.max_y_real = real[:,1].max()
    tran.min_x_pred = pred[:,0].min()
    tran.max_x_pred = pred[:,0].max()
    tran.min_y_pred = pred[:,1].min()
    tran.max_y_pred = pred[:,1].max()
    cam.paraxial_transform = tran
    write_shelve("aviris_cam_step2.xml", cam)

if CREATE_CAMERA_STEP3:
    igm = AvirisNgIgm(f"{input_test_data}/ang20170328t202059_rdn_igm", utm_zone)
    cam = read_shelve("aviris_cam_step2.xml")
    cam.fit_epsilon = True
    cam.fit_beta = True
    cam.fit_delta = True
    cam.fit_focal_length = True
    cam.fit_line_pitch = False
    cam.fit_sample_pitch = False
    cam.fit_principal_point_line(True, 0)
    cam.fit_principal_point_sample(True, 0)
    dem = SimpleDem()
    ipi = Ipi(orb, cam, 0, tt_full.min_time, tt_full.max_time, tt_full)
    igc = IpiImageGroundConnection(ipi, dem, None)
    x0 = cam.parameter_subset
    print(residual1(x0,igc, igm))
    r = scipy.optimize.least_squares(residual1, x0, args=(igc,igm))
    print(r)
    print(residual1(cam.parameter_subset, igc, igm))
    write_shelve("aviris_cam_step3.xml", cam)
    # These diagnostics shows most of the geolocation is with a pixel or so
    if True:
        for ln in range(500,igm.shape[0],500):
            print("ln:",ln)
            print(pd.DataFrame([distance(igc.ground_coordinate_approx_height(ImageCoordinate(ln,smp), igm[ln,smp].height_reference_surface), igm[ln,smp]) for smp in range(igm.shape[1])]).describe())

    # Fit nonlinearities one more ti
    igc.ipi.camera.paraxial_transform = CaptureParaxialTransform()
    ln = 1000
    for smp in range(igm.shape[1]):
        gc = igc.ground_coordinate_approx_height(ImageCoordinate(ln, smp),
                               igm[ln,smp].height_reference_surface)
        igc.collinearity_residual(igm[ln,smp],ImageCoordinate(ln,smp))
    predict_x = np.array(cam.paraxial_transform.predict_x)
    predict_y = np.array(cam.paraxial_transform.predict_y)
    real_x = np.array(cam.paraxial_transform.real_x)
    real_y = np.array(cam.paraxial_transform.real_y)
    pred = np.empty((predict_x.shape[0], 2))
    pred[:,0] = predict_x
    pred[:,1] = predict_y
    real = np.empty((real_x.shape[0], 2))
    real[:,0] = real_x
    real[:,1] = real_y
    deg = 5
    tran = PolynomialParaxialTransform_5d_5d()
    tran.real_to_par[0,:] = multipolyfit(real, pred[:,0], deg)
    tran.real_to_par[1,:] = multipolyfit(real, pred[:,1], deg)
    tran.min_x_real = real[:,0].min()
    tran.max_x_real = real[:,0].max()
    tran.min_y_real = real[:,1].min()
    tran.max_y_real = real[:,1].max()
    # The pred to real is kind of crappy for fitting in the x direction,
    # because the data we collected is degenerate. Go ahead and create
    # a wider data set to fit for
    pred2 = []
    real2 = []
    for x in np.arange(tran.min_x_real - cam.line_pitch * 4,
                       tran.max_x_real + cam.line_pitch * 4,
                       cam.line_pitch * 0.25):
        for y in np.arange(tran.min_y_real - cam.sample_pitch * 4,
                           tran.max_y_real + cam.sample_pitch * 4,
                           cam.sample_pitch * 0.25):
            real2.append([x,y])
            pred2.append([*tran.real_to_paraxial(x,y)])
    real2 = np.array(real2)
    pred2 = np.array(pred2)
    tran.par_to_real[0,:] = multipolyfit(pred2, real2[:,0], deg)
    tran.par_to_real[1,:] = multipolyfit(pred2, real2[:,1], deg)
    tran.min_x_pred = pred2[:,0].min()
    tran.max_x_pred = pred2[:,0].max()
    tran.min_y_pred = pred2[:,1].min()
    tran.max_y_pred = pred2[:,1].max()
    cam.paraxial_transform = tran
    if True:
        for ln in range(500,igm.shape[0],500):
            print("ln:",ln)
            print(pd.DataFrame([distance(igc.ground_coordinate_approx_height(ImageCoordinate(ln,smp), igm[ln,smp].height_reference_surface), igm[ln,smp]) for smp in range(igm.shape[1])]).describe())
    write_shelve("aviris_cam_step3.xml", cam)
    write_shelve(f"{emit_test_data}/l1_osp_aviris_ng_dir/camera.xml", cam)

class RadianceMetadata(StandardMetadata):
    def __init__(self, rad_full, ttscene):
        self.fh_in = geocal.GdalRasterImage(rad_full.file_name)
        super().__init__(start_time = ttscene.min_time,
                         end_time = ttscene.max_time,
                         pge_name = "create_aviris_ng_end_to_end_test_data.py")
        
    def extra_metadata(self, fh):
        fh["ENVI","wavelength units"] = "Nanometers"
        fh["ENVI", "wavelength"] = self.fh_in["ENVI", "wavelength"]
        fh["ENVI", "fwhm"] = self.fh_in["ENVI", "fwhm"]

if CREATE_SCENE:
    rad_full = EnviFile(f"{input_test_data}/ang20170328t202059_rdn_emit_syn",
                        mode="r")
    rset = []
    # We chop of the first few lines, just because the boundary
    # of the orbit file means we fail here.
    pad = 5
    for i in range(pad,tt_full.max_line//nline_per_scene * nline_per_scene,nline_per_scene):
        if(i+2*nline_per_scene < tt_full.max_line-pad):
            rset.append(range(i,i+nline_per_scene))
        else:
            rset.append(range(i,tt_full.max_line-pad))
    for i, r in enumerate(rset):
        ttscene = MeasuredTimeTable([tt_full.time_list(i) for i in r])
        tm = ttscene.min_time
        dstring = re.sub(r'T', 't', re.sub(r'[-:]', '',
                                           re.split(r'\.', str(tm))[0]))
        start_fname = "emit%s_o%05d_s%03d" % (dstring, orbit, i+1)
        fname = f"{emit_test_data}/{start_fname}_l1a_line_time_{end_fname}.nc"
        EmitTimeTable.write_file(fname, ttscene)
        smeta = RadianceMetadata(rad_full, ttscene)
        fname = f"{emit_test_data}/{start_fname}_l1b_rdn_{end_fname}.img"
        fout = EnviFile(fname, dtype=np.float32,
                        shape=(rad_full.shape[0], len(r),
                               rad_full.shape[2]), mode="w",
                        description="EMIT L1B calibrated spectral radiance (units: uW nm-1 cm-2 sr-1)")
        fout.data[:,:,:] = rad_full[:, r, :]
        smeta.write_metadata(fout)
            
        
