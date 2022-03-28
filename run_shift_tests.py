#!/shared/conda-shared-env/geocal-20220215/bin/python

import os
import sys
import subprocess

# Activate this conda environment first, and then source the emit setup:
# conda activate /shared/conda-shared-env/geocal-20220215
# source /home/mhessflores/emit-build/setup_emit.sh

# This script processes all SHIFT files for a given date

shift_line_lists_directory = "/home/mhessflores/aviris-ng/shift_line_lists/"
raw_data_directory = "/beegfs/store/ang/y22/raw/"
radiance_directory = "/beegfs/store/ang/y22/rdn/"
output_directory = "/beegfs/scratch/mhessflores/shift_runs/"
l1a_exe = "/home/mhessflores/emit-build/bin/aviris_ng_l1a_orbit_process"
geo_exe = "/home/mhessflores/emit-build/bin/aviris_ng_geo_process"
# Run params/config will always live here:
# Original directory:
# run_params = "/beegfs/store/shared/emit-test-data/latest/l1_osp_aviris_ng_geo_dir"
# Mike's modifications to improve tiepointing and exterior orientation:
run_params = "/home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp"

file_20220224 = "20220224_all_lines.txt"
file_20220228 = "20220228_all_lines.txt"

currentdate = os.path.join(shift_line_lists_directory, file_20220224)
# print(currentdate)
f = open(currentdate, "r")

for line in f:
	# print(line.rstrip("\n"))
	# currentoutputdir = line + '_output'
	currentshiftrun = os.path.join(output_directory, ''.join([line.rstrip("\n"), '_output']))
	# print(currentshiftrun)
	currentrawdata = os.path.join(raw_data_directory, ''.join([line.rstrip("\n"), '_raw']))
	# print(currentrawdata)
	currentlogfile1 = os.path.join(currentshiftrun, "aviris_ng_l1a_orbit_process_log.txt")
	# print(currentlogfile)
	# print(l1a_exe + ' ' + currentshiftrun + ' ' + run_params + ' ' + currentrawdata + " > " + currentlogfile)
	# Call aviris_ng_l1a_orbit_process with the appropriate parameters:
	# args = currentshiftrun + ' ' + run_params + ' ' + currentrawdata 
	proc1 = subprocess.run([l1a_exe, currentshiftrun, run_params, currentrawdata], stdout=subprocess.PIPE)  # check_call
	f1 = open(currentlogfile1, "w")
	print(proc1.stdout, file=f1)
	f1.close()
	#
	currentncfile = os.path.join(currentshiftrun, ''.join([line.rstrip("\n"), '_att.nc']))
	currentlinetimefile = os.path.join(currentshiftrun, ''.join([line.rstrip("\n"), '_line_time.nc']))
	currentclipfile = os.path.join(radiance_directory, ''.join([line.rstrip("\n"), '_rdn_v2z4_clip']))
	currentlogfile2 = os.path.join(currentshiftrun, "aviris_ng_geo_process_log.txt")
	proc2 = subprocess.run([geo_exe, currentshiftrun, run_params, currentncfile, currentlinetimefile, currentclipfile], stdout=subprocess.PIPE)  # check_call
	f2 = open(currentlogfile2, "w")
	print(proc2.stdout, file=f2)
	f2.close()


"""
The runs should look something like this:

/home/mhessflores/emit-build/bin/aviris_ng_l1a_orbit_process /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output /home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp /beegfs/store/ang/y22/raw/ang20220224t195402_raw > /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output/aviris_ng_l1a_orbit_process_log.txt

/home/mhessflores/emit-build/bin/aviris_ng_geo_process /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output /home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output/ang20220224t195402_att.nc /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output/ang20220224t195402_line_time.nc /beegfs/store/ang/y22/rdn/ang20220224t195402_rdn_v2z4_clip > /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output/aviris_ng_geo_process_log.txt

No SBA run:

/home/mhessflores/emit-build/bin/aviris_ng_l1a_orbit_process /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output_no_sba /home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp_no_sba /beegfs/store/ang/y22/raw/ang20220224t195402_raw > /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output_no_sba/aviris_ng_l1a_orbit_process_log.txt

/home/mhessflores/emit-build/bin/aviris_ng_geo_process /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output_no_sba /home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp_no_sba /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output_no_sba/ang20220224t195402_att.nc /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output_no_sba/ang20220224t195402_line_time.nc /beegfs/store/ang/y22/rdn/ang20220224t195402_rdn_v2z4_clip > /beegfs/scratch/mhessflores/shift_runs/ang20220224t195402_output_no_sba/aviris_ng_geo_process_log.txt

*****Can use sbatch or srun from Slurm to run on a full node (40 cores and 180G of memory for this example):
	sbatch -N 1 -c 40 --mem=180G --wrap=“python program.py parameters”

"""

"""
Flight line over the open ocean, for testing:

ang20210428t165435
raw data at: /beegfs/store/ang/y21/raw/
rdn data at: /beegfs/store/ang/y21/rdn, with subscript ‘_rdn_v2z1_clip’

 ->
sbatch -N 1 -c 40 --mem=180G --wrap=“python /home/mhessflores/emit-build/bin/aviris_ng_l1a_orbit_process /beegfs/scratch/mhessflores/shift_runs/ang20210428t165435_output /home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp /beegfs/store/ang/y21/raw/ang20210428t165435_raw > /beegfs/scratch/mhessflores/shift_runs/ang20210428t165435_output/aviris_ng_l1a_orbit_process_log.txt"
(or srun -N 1 -c 40 --mem=180G --pty python everythingelse)

sbatch -N 1 -c 40 --mem=180G --wrap=“python /home/mhessflores/emit-build/bin/aviris_ng_geo_process /beegfs/scratch/mhessflores/shift_runs/ang20210428t165435_output /home/mhessflores/aviris-ng/aviris-ng-test-data/l1_osp /beegfs/scratch/mhessflores/shift_runs/ang20210428t165435_output/ang20210428t165435_att.nc /beegfs/scratch/mhessflores/shift_runs/ang20210428t165435_output/ang20210428t165435_line_time.nc /beegfs/store/ang/y21/rdn/ang20210428t165435_rdn_v2z1_clip > /beegfs/scratch/mhessflores/shift_runs/ang20210428t165435_output/aviris_ng_geo_process_log.txt"
(or srun -N 1 -c 40 --mem=180G --pty python everythingelse)

"""

