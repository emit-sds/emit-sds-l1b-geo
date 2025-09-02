# Install conda environment
# --------------------------------------
# Things the user can change. Note you can change this by creating a Makefile.local
# to set these variables

# Should we install the latest conda packages, or the "fixed" set known to
# work (which will often lag the latest conda packages). Most of the time
# latest should work fine, but there might be the occasional breakage (e.g.,
# conda moves to a newer version of python and our various packages haven't
# been rebuilt yet the newer python, a python package update breaks
# something).
CONDA_FIXED=yes

# Location of environment we create
ENV_DIR=$(HOME)/emit-env

# Location of afids conda packages (you can check this out from
# git@github.jpl.nasa.gov:Cartography/afids-conda-package.git
CONDA_PACKAGE_DIR=../../afids-conda-package/afids-conda-channel

# Location of various datasets
EMIT_ANCILLARY=/store/shared/
AFIDS_DATA_ELEV_ROOT=$(EMIT_ANCILLARY)/dem/srtm_v3_dem_L2
AFIDS_DATA_SPICEDATA=$(EMIT_ANCILLARY)/spice_data/cspice
AFIDS_DATA_ORTHO=$(EMIT_ANCILLARY)/landsat
EMIT_OSP_DIR=/store/emit/ops/repos/emit_l1b_osp_installs/1.6.19
# Not used yet, but put in as placeholders. We have these in ECOSTRESS,
# so they may migrate to emit
AFIDS_DATA_LWM=$(EMIT_ANCILLARY)/dem/srtm_v3_lwm
AFIDS_COPERNICUS_DEM=$(EMIT_ANCILLARY)/Copernicus/copdem_v1_L2
AFIDS_COPERNICUS_LWM=$(EMIT_ANCILLARY)/Copernicus/coplwm_v1_L2

# Include a Makefile.local to override things, if found
-include Makefile.local
# ---------------------------------------------------------------------------
# Past this point are the rules, shouldn't need to modify these
# ---------------------------------------------------------------------------

EMIT_ENVIRONMENT_FILE=$(if $(filter $(CONDA_FIXED),yes), emit_environment_fixed.yml, emit_environment_latest.yml)

# Install micromamba
PLATFORM=linux
ARCH=64
MICROMAMBA_URL=https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-$(PLATFORM)-$(ARCH)

micromamba:
	wget -qO micromamba $(MICROMAMBA_URL) && chmod +x micromamba

$(ENV_DIR): micromamba $(MUSES_ENVIRONMENT_FILE)
	-rm -rf $(ENV_DIR)
	./micromamba create --override-channels --channel conda-forge --channel $(CONDA_PACKAGE_DIR) -y -f $(EMIT_ENVIRONMENT_FILE) -p $(ENV_DIR)
	./micromamba run -p $(ENV_DIR) conda env export --override-channels --channel conda-forge --channel $(CONDA_PACKAGE_DIR) > emit_environment_installed.yml
	eval "$$($(ENV_DIR)/bin/conda shell.bash hook)" && conda activate $(ENV_DIR) && conda env config vars set AFIDS_DATA_ELEV_ROOT=$(AFIDS_DATA_ELEV_ROOT) AFIDS_DATA_LWM=$(AFIDS_DATA_LWM) AFIDS_DATA_SPICEDATA=$(AFIDS_DATA_SPICEDATA) SPICEDATA=$(AFIDS_DATA_SPICEDATA) AFIDS_DATA_ORTHO=$(AFIDS_DATA_ORTHO) AFIDS_COPERNICUS_DEM=$(AFIDS_COPERNICUS_DEM) AFIDS_COPERNICUS_LWM=$(AFIDS_COPERNICUS_LWM) LANDSAT_ROOT=$(AFIDS_DATA_ORTHO) ELEV_ROOT=$(AFIDS_DATA_ELEV_ROOT) EMIT_OSP_DIR=$(EMIT_OSP_DIR) EMITTOP=$(ENV_DIR) TAE_PATH=$(ENV_DIR)/vicar_pdf:$${TAE_PATH} AFIDS_DATA=$(ENV_DIR)/data AFIDS_VDEV_DATA=$(ENV_DIR)/data/vdev

# Recreate the environment, deleting if already there
# ------------------------------------------------------------
recreate-env:
	-rm -rf $(ENV_DIR)
	$(MAKE) create-env

# Build the conda envirornment, if needed or out of date.
# ------------------------------------------------------------
create-env: $(ENV_DIR)

