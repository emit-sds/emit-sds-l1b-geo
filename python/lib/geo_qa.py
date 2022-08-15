from .emit_igc import *
from .l1_osp_dir import L1OspDir
from emit_swig import EmitIgcCollection
import h5netcdf
import h5py
import numpy as np
import pandas as pd
import geocal
import logging
from packaging import version

logger = logging.getLogger('l1b_geo_process.geo_qa')

class GeoQa:
    '''This handles the Geo QA file.'''
    def __init__(self, fname, log_fname, l1a_att_fname, tt_and_rdn_fname,
                 l1_osp_dir):
        self.fname = fname
        self.log_fname = log_fname
        self.l1_osp_dir = l1_osp_dir
        self.scene_name = None
        self.tp_stat = None
        self.qa_flag = None
        self.encountered_exception = False
        # This ends up getting pickled, and h5netcdf doesn't pickle well. So
        # instead of keeping the file open, we reopen and update as needed.
        fout = self.open_fh("w")
        log_group = fout.create_group("Logs")
        tplog_group = log_group.create_group("Tiepoint Logs")
        tp_group = fout.create_group("Tiepoint")
        orb_group = fout.create_group("Orbit Correction")
        ac_group = fout.create_group("Accuracy Estimate")
        g = fout.create_group("Input File")
        g.create_variable("L1A ATT Filename", ("j",),
                          data=[l1a_att_fname.encode('utf8'),],
                          dtype=h5py.special_dtype(vlen=bytes))
        g.create_variable("L1 OSP Dir", ("j",),
                          data=[l1_osp_dir.l1_osp_dir.encode('utf8'),],
                          dtype=h5py.special_dtype(vlen=bytes))
        tt_fname = [tname.encode('utf8') for tname, rname in tt_and_rdn_fname]
        rdn_fname = [rname.encode('utf8') for tname, rname in tt_and_rdn_fname]
        g.create_variable("Line Time Filename", ("i",),
                          data=tt_fname,
                          dtype=h5py.special_dtype(vlen=bytes))
        g.create_variable("L1B Radiance Filename", ("i",),
                          data=rdn_fname,
                          dtype=h5py.special_dtype(vlen=bytes))
        fout.close()

    @classmethod
    def dataframe(cls, qa_fname):
        '''Return a pandas DataFrame with the contents of the QA file'''
        fh = cls.fh_qa_fname(qa_fname)
        t = pd.DataFrame([t.decode('utf-8') for t in
                          fh["Tiepoint/Scene Times"][:]],
                         columns=["Scene Times",])
        t2 = pd.DataFrame(fh["Tiepoint/Tiepoint Count"][:],
                          columns=["Initial Tiepoint", "Blunders",
                                   "Number Tiepoint",
                                   "Number Image Match Tries"])
        d = fh["Accuracy Estimate/Accuracy Before Correction"][:]
        d[d < -9990] = np.NaN
        t3 = pd.DataFrame(d, columns=["Initial Accuracy",])
        d = fh["Accuracy Estimate/Final Accuracy"][:]
        d[d < -9990] = np.NaN
        t4 = pd.DataFrame(d, columns=["Accuracy",])
        d = fh["Accuracy Estimate/Delta time correction before scene"][:]
        # Think we want -9999 to go through here, but we can change that if
        # needed
        t5 = pd.DataFrame(d, columns=["Delta t before scene",])
        d = fh["Accuracy Estimate/Delta time correction after scene"][:]
        t6 = pd.DataFrame(d, columns=["Delta t after scene",])
        qa_val = { 0: "Best", 1: "Good", 2: "Suspect", 3: "Poor",
                   -9999 : "Unknown"}
        t7 = pd.DataFrame([qa_val[v] for v in
                           fh["Accuracy Estimate/Geolocation accuracy QA flag"][:]],
                          columns=["QA Flag",])
        df = pd.concat([t,t2,t3,t4,t5,t6,t7],axis=1)
        fh.close()
        return df

    @classmethod
    def igccol_initial(cls, qa_fname, include_img = True):
        '''Read the given QA file, and create a EmitIgcCollection that goes
        with the input file list. 

        Note I'm not sure that things won't move around on the file system,
        so we may need to add some kind of remapping here. But for now, just
        go with the paths initially saved in the Input File group,'''
        fh = cls.fh_qa_fname(qa_fname)
        l1_osp_dir = fh["/Input File/L1 OSP Dir"][0].decode('utf8')
        l1_osp_dir = L1OspDir(l1_osp_dir)
        l1a_att_fname = fh["/Input File/L1A ATT Filename"][0].decode('utf8')
        rdn_fname = fh["/Input File/L1B Radiance Filename"][:]
        tt_fname = fh["/Input File/Line Time Filename"][:]
        tt_and_rdn_fname = []
        for i in range(len(rdn_fname)):
            tt_and_rdn_fname.append((tt_fname[i].decode('utf8'),
                                     rdn_fname[i].decode('utf8')))
        return EmitIgcCollection.create(l1a_att_fname, tt_and_rdn_fname,
                                        l1_osp_dir.match_rad_band,
                                        l1_osp_dir, include_img=include_img)

    @classmethod
    def tpcol_single(cls, qa_fname, img_index):
        fh = cls.fh_qa_fname(qa_fname)
        tpcol = []
        try:
            tpdata = fh["Tiepoint/Image Index %03d/Tiepoints" % (img_index+1)][:,:]
            for j in range(tpdata.shape[0]):
                tp = geocal.TiePoint(nimg)
                tp.is_gcp = True
                tp.ground_location = geocal.Ecr(*tpdata[j,2:6])
                tp.image_coordinate(i, geocal.ImageCoordinate(*tpdata[j,0:2]))
                tpcol.append(tp)
        except KeyError:
            # Ok if not found in QA file, just means that image
            # didn't have any tiepoints.
            pass
        return geocal.TiePointCollection(tpcol)
        

    @classmethod
    def tpcol(cls, qa_fname):
        '''Read the given QA file, and extract out the TiePointCollection for
        the data. Right now we include all of the Image Indexes, we
        could subset this if that ends up being useful.
        '''
        fh = cls.fh_qa_fname(qa_fname)
        rdn_fname = fh["/Input File/L1B Radiance Filename"][:]
        nimg = len(rdn_fname)
        tpcol = []
        for i in range(nimg):
            try:
                tpdata = fh["Tiepoint/Image Index %03d/Tiepoints" % (i+1)][:,:]
                for j in range(tpdata.shape[0]):
                    tp = geocal.TiePoint(nimg)
                    tp.is_gcp = True
                    tp.ground_location = geocal.Ecr(*tpdata[j,2:6])
                    tp.image_coordinate(i, geocal.ImageCoordinate(*tpdata[j,0:2]))
                    tpcol.append(tp)
            except KeyError:
                # Ok if not found in QA file, just means that image
                # didn't have any tiepoints.
                pass
        return geocal.TiePointCollection(tpcol)
    
    @classmethod
    def igccol_corrected(cls, qa_fname, include_img=True):
        '''Read the given QA file and create a EmitIgcCollection and add all
        the corrections we did from the SBA.'''
        igccol = cls.igccol_initial(qa_fname, include_img=include_img)
        orb_corr = geocal.OrbitOffsetCorrection(igccol.orbit)
        fh = cls.fh_qa_fname(qa_fname)
        att_tm = fh["Orbit Correction/Attitude Time Point"][:]
        pos_tm = fh["Orbit Correction/Position Time Point"][:]
        parm = fh["Orbit Correction/Parameter"][:]
        att_tm = [geocal.Time.time_j2000(t) for t in att_tm]
        pos_tm = [geocal.Time.time_j2000(t) for t in pos_tm]
        for tm in pos_tm:
            orb_corr.insert_position_time_point(tm)
        for tm in att_tm:
            orb_corr.insert_attitude_time_point(tm)
        orb_corr.parameter = parm
        igccol.orbit = orb_corr
        igccol.add_object(igccol.camera)
        igccol.add_object(igccol.orbit)
        return igccol

    @classmethod
    def fh_qa_fname(cls, qa_fname):
        # Newer version of h5netcdf needs decode_vlen_strings, but this
        # keyword isn't in older versions
        if version.parse(h5netcdf.__version__) >= version.parse("0.13.0"):
            fh = h5netcdf.File(qa_fname, "r", decode_vlen_strings=False)
        else:
            fh = h5netcdf.File(qa_fname, "r")
        return fh
        
    def open_fh(self, access="a"):
        # Newer version of h5netcdf needs decode_vlen_strings, but this
        # keyword isn't in older versions
        if version.parse(h5netcdf.__version__) >= version.parse("0.13.0"):
            fout = h5netcdf.File(self.fname, access, decode_vlen_strings=False,
                                 phony_dims='sort')
        else:
            fout = h5netcdf.File(self.fname, access, phony_dims='sort')
        return fout
    
    def add_tp_log(self, scene_name, tplogfname):
        try:
            log = open(tplogfname, "r").read()
        except FileNotFoundError:
            # Ok if log file isn't found, just given an message
            log = "log file missing"
        log = [log.encode('utf-8'),]
        fh = self.open_fh()
        tplog_group = fh["Logs/Tiepoint Logs"]
        tplog_group.create_variable(scene_name, ("i",), data=log,
                                    dtype=h5py.special_dtype(vlen=bytes))
        fh.close()

    def add_tp_single_scene(self, image_index, igccol, tpcol, ntpoint_initial,
                            ntpoint_removed, ntpoint_final, number_match_try):
        '''Write out information about the tiepoints we collect for scene.'''
        if(self.scene_name is None):
            self.scene_name = [igccol.title(i).encode('utf8') for i in
                               range(igccol.number_image)]
        if(self.tp_stat is None):
            self.tp_stat = np.full((igccol.number_image, 9), -9999.0)
        self.tp_stat[image_index, 0] = ntpoint_initial
        self.tp_stat[image_index, 1] = ntpoint_removed
        self.tp_stat[image_index, 2] = ntpoint_final
        self.tp_stat[image_index, 3] = number_match_try
        if(len(tpcol) > 0):
            df = tpcol.data_frame(igccol,image_index)
            self.tp_stat[image_index, 4] = df.ground_2d_distance.quantile(.68)
        tpdata = None
        if(len(tpcol) > 0):
            tpdata = np.empty((len(tpcol), 5))
        for i, tp in enumerate(tpcol):
            ic = tp.image_coordinate(image_index)
            tpdata[i,0:2] = ic.line, ic.sample
            tpdata[i,2:6] = geocal.Ecr(tp.ground_location).position
        f = self.open_fh()
        tp_group = f["Tiepoint"]
        s_group = tp_group.create_group("Image Index %03d" % (image_index+1))
        if(tpdata is not None):
            d = s_group.create_variable("Tiepoints", ('i','c'), data=tpdata)
            d.attrs["Description"] = \
'''This is the list of tiepoints for a scene, after removing blunders.

The first column in image coordinate line, the second column is image
coordinate sample.

The remaining three columns are the location of the ground coordinate in
the reference image, in Ecr coordinates (in meters).
'''
        f.close()

    def add_final_accuracy(self, igccol_corrected, tpcol):
        '''Add in the metadata for the final accuracy. This also fills in
        the field qa_flag, which we can grab for setting this in other files.
        '''
        # Save information about the solution we found
        fh = self.open_fh()
        orb_group = fh["Orbit Correction"]
        att_tm, _, pos_tm, _ = igccol_corrected.orbit.orbit_correction_parameter()
        att_tm = [t.j2000 for t in att_tm]
        pos_tm = [t.j2000 for t in pos_tm]
        orb_group.create_variable("Attitude Time Point", ("at",), data=att_tm)
        orb_group.create_variable("Position Time Point", ("pt",), data=pos_tm)
        orb_group.create_variable("Parameter", ("i",),
                                  data=igccol_corrected.orbit.parameter)
        fh.close()
        # Ok if no tiepoints for scene i, this just return nan
        self.tp_stat[:,5] = np.array([tpcol.data_frame(igccol_corrected, i).ground_2d_distance.quantile(.68)
                      for i in range(igccol_corrected.number_image)])
        self.tp_stat[:,5][np.isnan(self.tp_stat[:,5])] = -9999
        self.qa_flag = []
        for i in range(igccol_corrected.number_image):
            tt = igccol_corrected.image_ground_connection(i).ipi.time_table
            t = tt.min_time + (tt.max_time - tt.min_time) / 2
            t1 = -9999
            t2 = -9999
            tb, ta = igccol_corrected.nearest_attitude_time_point(t)
            if(tb < geocal.Time.max_valid_time - 1):
                t1 = t - tb
            if(ta < geocal.Time.max_valid_time - 1):
                t2 = ta - t
            self.tp_stat[i,6] = t1
            self.tp_stat[i,7] = t2
            qa_val = self.l1_osp_dir.geocal_accuracy_qa(t1, t2,
                                                        self.tp_stat[i, 2])
            self.qa_flag.append(qa_val)
            if(qa_val == "Best"):
                self.tp_stat[i,8] = 0
            elif(qa_val == "Good"):
                self.tp_stat[i,8] = 1
            elif(qa_val == "Suspect"):
                self.tp_stat[i,8] = 2
            elif(qa_val == "Poor"):
                self.tp_stat[i,8] = 3
            else:
                self.tp_stat[i,8] = -9999
            if(self.tp_stat[i,4] >= 0 and
               self.tp_stat[i,5] >= 0):
                logger.info("Scene %d initial error: %0.1f m final error: %0.1f m QA: %s" % (i+1, self.tp_stat[i,4], self.tp_stat[i,5], qa_val))
            else:
                logger.info("Scene %d no tiepoints QA: %s" % (i+1, qa_val))
                
    def close(self):
        try:
            log = open(self.log_fname, "r").read()
        except FileNotFoundError:
            # Ok if log file isn't found, just given an message
            log = "log file missing"
        log = [log.encode('utf-8')]
        f = self.open_fh()
        log_group = f["Logs"]
        log_group.create_variable("Overall Log", ("i",), data=log,
                                  dtype=h5py.special_dtype(vlen=bytes))
        tp_group = f["Tiepoint"]
        if(self.scene_name is not None):
            tp_group.create_variable("Scene Times", ("i",),
                                     data=self.scene_name,
                                     dtype=h5py.special_dtype(vlen=bytes))
        if(self.tp_stat is not None):
            dset = tp_group.create_variable("Tiepoint Count", ("i","c"),
                                            data=self.tp_stat[:,0:4].astype(np.int32))
            dset.attrs["Description"] = \
'''First column is the initial number of tie points

Second column is the number of blunders removed

Third column is the number after removing blunders and applying minimum
number of tiepoints (so if < threshold we set this to 0).

Fourth column is the number to image matching tries we did.'''
        ac_group = f["Accuracy Estimate"]
        ac_group.create_variable("Scenes", ("i",), data=self.scene_name,
                                dtype=h5py.special_dtype(vlen=bytes))
        if(self.tp_stat is not None):
            dset = ac_group.create_variable("Accuracy Before Correction",
                                            ("i",),
                                            data=self.tp_stat[:,4])
            dset.attrs["Units"] = "m"
            dset = ac_group.create_variable("Final Accuracy",
                                            ("i",),
                                            data=self.tp_stat[:,5])
            dset.attrs["Units"] = "m"
            dset = ac_group.create_variable("Delta time correction before scene",
                                            ("i",),
                                            data=self.tp_stat[:,6])
            dset.attrs["Units"] = "s"
            dset = ac_group.create_variable("Delta time correction after scene",
                                            ("i",),
                                            data=self.tp_stat[:,7])
            dset.attrs["Units"] = "s"
            dset = ac_group.create_variable("Geolocation accuracy QA flag",
                                            ("i",),
                                            data=self.tp_stat[:,8])
            dset.attrs["Description"] = \
'''0: Best - Image matching was performed for this scene, expect 
       good geolocation accuracy.
1: Good - Image matching was performed on a nearby scene, and correction 
       has been interpolated/extrapolated. Expect good geolocation accuracy.
2: Suspect - Matched somewhere in the orbit. Expect better geolocation 
       than orbits w/o image matching, but may still have large errors.
3: Poor - No matches in the orbit. Expect largest geolocation errors.
9999: Unknown value'''
        f.close()
        
__all__ = ["GeoQa",]    
