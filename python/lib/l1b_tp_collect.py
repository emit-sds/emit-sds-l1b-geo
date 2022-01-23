class L1bTpCollect:
    '''Project data to the surface and collect tie-points with the
    orthobase'''
    def __init__(self, igccol, l1b_geo_config, geo_qa):
        self.igccol = igccol
        self.geo_qa = geo_qa
        self.l1b_geo_config = l1b_geo_config

    def tp(self, i):
        '''Get tiepoints for the given scene number'''
        return None
        ntpoint_initial = 0     # Initial value, so an exception below doesn't
                                # result in "local variable referenced before
                                # assignment" exception
        ntpoint_removed = 0
        ntpoint_final = 0
        try:
            tt = self.igccol.image_ground_connection(i).time_table
            for i2, tpcol in enumerate(self.tpcollect):
                tpcol.image_index1 = i
                tpcol.ref_image_fname = self.ref_fname[i]
                tpcol.log_file = self.log_file[i] + "_%d" %i2
                tpcol.run_dir_name = self.run_dir_name[i] + "_%d" % i2
                shutil.rmtree(tpcol.run_dir_name, ignore_errors=True)
                self.print_and_log("Collecting tp for %s try %d" %
                                   (self.igccol.title(i), i2+1))
                res = tpcol.tie_point_grid(self.num_x, self.num_y)
                # Try this, and see how it works
                ntpoint_initial = len(res)
                ntpoint_removed = 0
                if(len(res) >= self.min_tp_per_scene):
                    len1 = len(res)
                    res = geocal.outlier_reject_ransac(res, ref_image=geocal.VicarLiteRasterImage(self.ref_fname[i]), igccol = self.igccol, threshold=3)
                    ntpoint_removed = len1-len(res)
                    self.print_and_log("Removed %d tie-points using RANSAC for %s" % (len1-len(res), self.igccol.title(i)))
                if(len(res) >= self.min_tp_per_scene):
                    break
            number_match_try = i2 + 1
            if(len(res) < self.min_tp_per_scene):
                self.print_and_log("Too few tie-point found. Found %d, and require at least %d. Rejecting tie-points for %s" % (len(res), self.min_tp_per_scene, self.igccol.title(i)))
                res = []
            else:
                self.print_and_log("Found %d tie-points for %s try %d" % (len(res), self.igccol.title(i), number_match_try))
            self.print_and_log("Done collecting tp for %s" % self.igccol.title(i))
        except Exception as e:
            self.report_and_log_exception(i)
            res = []
        ntpoint_final = len(res)
        return res, tt.min_time, tt.max_time, ntpoint_initial, ntpoint_removed, ntpoint_final, number_match_try

    def tpcol(self, pool=None):
        '''Return tiepoints collected. We also return the time ranges for the
        ImageGroundConnection that we got good tiepoint for. This
        can be used by the calling program to determine such things
        as the breakpoints on the orbit model
        '''
        
        # First project all the data.
        p = L1bProj(self.igccol, self.l1b_geo_config, geo_qa)
        proj_res = p.proj(pool=pool)
        it = []
        for i in range(self.igccol.number_image):
            if(proj_res[i]):
                it.append(i)
        # Can't pickle this with the pool, so just set to None for now.
        # We don't actually need this for anything in tp.
        l1b_geo_config = self.l1b_geo_config
        try:
            if(pool is None):
                tpcollist = map(self.tp, it)
            else:
                tpcollist = pool.map(self.tp, it)
        finally:
            self.l1b_geo_config = l1b_geo_config    
        res = geocal.TiePointCollection()
        time_range_tp = []
        for i in range(self.igccol.number_image):
            for i2 in range(len(self.tpcollect)):
                lf = self.log_file[i] + "_%d" %i2
                if(os.path.exists(lf)):
                    self.geo_qa.add_tp_log(self.igccol.title(i) + "_%d" % i2, lf)
        j = 0
        for i in range(self.igccol.number_image):
            if(proj_res[i]):
                (tpcol, tmin, tmax, ntpoint_initial, ntpoint_removed,
                 ntpoint_final, number_match_try) = tpcollist[j]
                self.geo_qa.add_tp_single_scene(i, self.igccol,
                        tpcol, ntpoint_initial, ntpoint_removed, ntpoint_final,
                        number_match_try)
                if(len(tpcol) > 0):
                    res.extend(tpcol)
                    time_range_tp.append([tmin, tmax])
                j += 1
            else:
                self.geo_qa.add_tp_single_scene(i, self.igccol,
                                                 [], 0, 0, 0, 0)
        for i in range(len(res)):
            res[i].id = i+1
        return res, time_range_tp
        
