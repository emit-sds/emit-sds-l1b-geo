from .l1b_proj import L1bProj
import geocal
import shutil
import os
import logging

logger = logging.getLogger("l1b_geo_process.l1b_tp_collect")


class L1bTpCollect:
    """Project data to the surface and collect tie-points with the
    orthobase"""

    def __init__(self, igccol, l1_osp_dir, geo_qa):
        self.igccol = igccol
        self.geo_qa = geo_qa
        self.l1_osp_dir = l1_osp_dir
        self.log_file = [
            "tpmatch_%03d.log" % (i + 1) for i in range(self.igccol.number_image)
        ]
        self.run_dir_name = [
            "tpmatch_%03d" % (i + 1) for i in range(self.igccol.number_image)
        ]

        # Tom has empirically come up with a set of things to try to
        # get a better matching results. We go ahead and collect these
        # into a series of trials, trying each in turn if the previous
        # one doesn't get enough matches.
        #
        # Note the log and run directory gets updated before use, so it
        # is ok they have the same name here (these are just placeholders)
        self.tpcollect = []
        fftsize = l1_osp_dir.fftsize
        magnify = l1_osp_dir.magnify
        magmin = l1_osp_dir.magmin
        toler = l1_osp_dir.toler
        redo = l1_osp_dir.redo
        # Original try
        self.tpcollect.append(
            geocal.TiePointCollectPicmtch(
                self.igccol,
                [
                    "placeholder",
                ],
                image_index1=0,
                ref_image_fname="placeholder",
                fftsize=fftsize,
                magnify=magnify,
                magmin=magmin,
                toler=toler,
                redo=redo,
                ffthalf=2,
                seed=562,
                log_file="placeholder",
                run_dir_name="placeholder",
            )
        )
        # Increase mag, and change seed
        self.tpcollect.append(
            geocal.TiePointCollectPicmtch(
                self.igccol,
                [
                    "placeholder",
                ],
                image_index1=0,
                ref_image_fname="placeholder",
                fftsize=fftsize,
                magnify=magnify + 0.5,
                magmin=magmin,
                toler=toler,
                redo=redo,
                ffthalf=2,
                seed=19364793,
                log_file="placeholder",
                run_dir_name="placeholder",
            )
        )
        # Decrease mag, increase tolerance, change seed
        self.tpcollect.append(
            geocal.TiePointCollectPicmtch(
                self.igccol,
                [
                    "placeholder",
                ],
                image_index1=0,
                ref_image_fname="placeholder",
                fftsize=fftsize,
                magnify=magnify - 0.5,
                magmin=magmin,
                toler=toler + 1.0,
                redo=redo,
                ffthalf=2,
                seed=578,
                log_file="placeholder",
                run_dir_name="placeholder",
            )
        )
        # Decrease mag, increase tolerance, change seed
        self.tpcollect.append(
            geocal.TiePointCollectPicmtch(
                self.igccol,
                [
                    "placeholder",
                ],
                image_index1=0,
                ref_image_fname="placeholder",
                fftsize=fftsize,
                magnify=magnify - 1.0,
                magmin=magmin,
                toler=toler + 1.0,
                redo=redo,
                ffthalf=2,
                seed=700,
                log_file="placeholder",
                run_dir_name="placeholder",
            )
        )
        # Increase mag, increase tolerance, change seed
        self.tpcollect.append(
            geocal.TiePointCollectPicmtch(
                self.igccol,
                [
                    "placeholder",
                ],
                image_index1=0,
                ref_image_fname="placeholder",
                fftsize=fftsize,
                magnify=magnify + 2.5,
                magmin=magmin,
                toler=toler + 3.0,
                redo=redo,
                ffthalf=2,
                seed=800,
                log_file="placeholder",
                run_dir_name="placeholder",
            )
        )

        self.min_tp_per_scene = l1_osp_dir.min_tp_per_scene

    def tp(self, i):
        """Get tiepoints for the given scene number"""
        ntpoint_initial = 0  # Initial value, so an exception below doesn't
        # result in "local variable referenced before
        # assignment" exception
        ntpoint_removed = 0
        ntpoint_final = 0
        number_match_try = 0
        try:
            tt = self.igccol.image_ground_connection(i).ipi.time_table
            for i2, tpcol in enumerate(self.tpcollect):
                tpcol.image_index1 = i
                tpcol.surface_image_fname = self.proj_fname
                tpcol.ref_image_fname = self.ref_fname[i]
                tpcol.log_file = self.log_file[i] + "_%d" % i2
                tpcol.run_dir_name = self.run_dir_name[i] + "_%d" % i2
                shutil.rmtree(tpcol.run_dir_name, ignore_errors=True)
                logger.info(
                    "Collecting tp for %s try %d" % (self.igccol.title(i), i2 + 1)
                )
                res = tpcol.tie_point_grid(
                    self.l1_osp_dir.num_tiepoint_x, self.l1_osp_dir.num_tiepoint_y
                )
                # Try this, and see how it works
                ntpoint_initial = len(res)
                ntpoint_removed = 0
                if len(res) >= self.min_tp_per_scene:
                    len1 = len(res)
                    res = geocal.outlier_reject_ransac(
                        res,
                        ref_image=geocal.VicarLiteRasterImage(self.ref_fname[i]),
                        igccol=self.igccol,
                        threshold=3,
                    )
                    ntpoint_removed = len1 - len(res)
                    logger.info(
                        "Removed %d tie-points using RANSAC for %s"
                        % (len1 - len(res), self.igccol.title(i))
                    )
                if len(res) >= self.min_tp_per_scene:
                    break
            number_match_try = i2 + 1
            if len(res) < self.min_tp_per_scene:
                logger.info(
                    "Too few tie-point found. Found %d, and require at least %d. Rejecting tie-points for %s"
                    % (len(res), self.min_tp_per_scene, self.igccol.title(i))
                )
                res = []
            else:
                logger.info(
                    "Found %d tie-points for %s try %d"
                    % (len(res), self.igccol.title(i), number_match_try)
                )
            logger.info("Done collecting tp for %s" % self.igccol.title(i))
        except Exception as e:
            logger.info(
                "Exception occurred while collecting tie-points for %s",
                self.igccol.title(i),
            )
            logger.exception(e, stack_info=True)
            logger.info("Skipping tie-points for this scene and continuing processing")
            res = []
        ntpoint_final = len(res)
        return (
            res,
            tt.min_time,
            tt.max_time,
            ntpoint_initial,
            ntpoint_removed,
            ntpoint_final,
            number_match_try,
        )

    def tpcol(self, pool=None):
        """Return tiepoints collected. We also return the time ranges for the
        ImageGroundConnection that we got good tiepoint for. This
        can be used by the calling program to determine such things
        as the breakpoints on the orbit model
        """

        # First project all the data.
        p = L1bProj(self.igccol, self.l1_osp_dir, self.geo_qa)
        proj_res = p.proj(pool=pool)
        self.ref_fname = [t[1] if t is not None else "" for t in proj_res]
        self.proj_fname = [t[0] if t is not None else "" for t in proj_res]
        it = [i for i in range(self.igccol.number_image) if proj_res[i] is not None]
        if pool is None:
            tpcollist = list(map(self.tp, it))
        else:
            tpcollist = pool.map(self.tp, it)
        res = geocal.TiePointCollection()
        time_range_tp = []
        for i in range(self.igccol.number_image):
            for i2 in range(len(self.tpcollect)):
                lf = self.log_file[i] + "_%d" % i2
                if os.path.exists(lf):
                    self.geo_qa.add_tp_log("Image Index %d %d" % (i + 1, i2), lf)
        j = 0
        for i in range(self.igccol.number_image):
            if proj_res[i]:
                (
                    tpcol,
                    tmin,
                    tmax,
                    ntpoint_initial,
                    ntpoint_removed,
                    ntpoint_final,
                    number_match_try,
                ) = tpcollist[j]
                self.geo_qa.add_tp_single_scene(
                    i,
                    self.igccol,
                    tpcol,
                    ntpoint_initial,
                    ntpoint_removed,
                    ntpoint_final,
                    number_match_try,
                )
                if len(tpcol) > 0:
                    res.extend(tpcol)
                    time_range_tp.append([tmin, tmax])
                j += 1
            else:
                self.geo_qa.add_tp_single_scene(i, self.igccol, [], 0, 0, 0, 0)
        for i in range(len(res)):
            res[i].id = i + 1
        return res, time_range_tp
