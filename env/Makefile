# Install conda environment
# --------------------------------------
# Things the user can change. Note you can change this by creating a Makefile.local
# to set these variables

EMIT_VERSION=2.0.0

# Should we install the latest conda packages, or the "pixi.lock" set known to
# work (which will often lag the latest conda packages). Most of the time
# latest should work fine, but there might be the occasional breakage (e.g.,
# conda moves to a newer version of python and our various packages haven't
# been rebuilt yet the newer python, a python package update breaks
# something).
# --------------------------------------
# No pixi.lock is committed yet, so default to no. Change to yes once "make update-lock" has been run.
PIXI_LOCKED=no

mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Location of environment we create
# --------------------------------------

ENV_DIR=$(abspath $(mkfile_dir)../../emit-build/build-pixi)

# Location of pixi unpack directory, if different
# --------------------------------------

UNPACK_ENV_DIR=$(ENV_DIR)

# Location of afids conda packages (you can check this out from
# git@github.jpl.nasa.gov:Cartography/afids-conda-package.git
# --------------------------------------

CONDA_PACKAGE_DIR=$(abspath $(mkfile_dir)../../afids-conda-package/afids-conda-channel)

# Location of various datasets
# --------------------------------------

EMIT_ANCILLARY=/store/shared
AFIDS_DATA_ELEV_ROOT=$(EMIT_ANCILLARY)/dem/srtm_v3_dem_L2
AFIDS_DATA_LWM=$(EMIT_ANCILLARY)/dem/srtm_v3_lwm
AFIDS_COPERNICUS_DEM=$(EMIT_ANCILLARY)/Copernicus/copdem_v1_L2
AFIDS_COPERNICUS_LWM=$(EMIT_ANCILLARY)/Copernicus/coplwm_v1_L2
AFIDS_DATA_SPICEDATA=$(EMIT_ANCILLARY)/spice_data/cspice
AFIDS_DATA_ORTHO=$(EMIT_ANCILLARY)/landsat
EMIT_OSP_DIR=/store/emit/ops/repos/emit_l1b_osp_installs/1.6.29
EMIT_TEST_DATA=/store/shared/emit-test-data

# Include a Makefile.local to override things, if found
# --------------------------------------

-include Makefile.local

# ---------------------------------------------------------------------------
# Past this point are the rules, shouldn't need to modify these
# ---------------------------------------------------------------------------

OS := $(shell uname -s)

ifeq ($(OS),Darwin)
  PIXI_LOCK_DIR:=$(mkfile_dir)/osx
else
  PIXI_LOCK_DIR:=$(mkfile_dir)/linux
endif

ifeq '$(PIXI_LOCKED)' 'yes'
$(ENV_DIR)/pixi.toml: $(PIXI_LOCK_DIR)/pixi.toml
	sed s"|fake-afids-conda-channel|$(CONDA_PACKAGE_DIR)|"g $< > $@

$(ENV_DIR)/pixi.lock: $(PIXI_LOCK_DIR)/pixi.lock
	sed s"|fake-afids-conda-channel|$(CONDA_PACKAGE_DIR)|"g $< > $@

PIXI_FILE_INSTALL= $(ENV_DIR)/pixi.toml $(ENV_DIR)/pixi.lock

PIXI_FILE_DEPEND=$(PIXI_LOCK_DIR)/pixi.toml $(PIXI_LOCK_DIR)/pixi.lock

PIXI_INSTALL_COMMAND= pixi install --frozen --manifest-path $(ENV_DIR) 
else
$(ENV_DIR)/pixi.toml: $(PIXI_LOCK_DIR)/pixi.toml
	sed s"|fake-afids-conda-channel|$(CONDA_PACKAGE_DIR)|"g $< > $@

PIXI_FILE_INSTALL= $(ENV_DIR)/pixi.toml

PIXI_FILE_DEPEND=$(PIXI_LOCK_DIR)/pixi.toml

PIXI_INSTALL_COMMAND= pixi install --manifest-path $(ENV_DIR) 

endif

PIXI_INSTALL_COMMAND+= && pixi run --manifest-path $(ENV_DIR) bash -c "\$$CONDA_PREFIX/bin/conda env config vars set AFIDS_DATA_ELEV_ROOT=$(AFIDS_DATA_ELEV_ROOT) AFIDS_DATA_LWM=$(AFIDS_DATA_LWM) AFIDS_DATA_SPICEDATA=$(AFIDS_DATA_SPICEDATA) SPICEDATA=$(AFIDS_DATA_SPICEDATA) AFIDS_DATA_ORTHO=$(AFIDS_DATA_ORTHO) AFIDS_COPERNICUS_DEM=$(AFIDS_COPERNICUS_DEM) AFIDS_COPERNICUS_LWM=$(AFIDS_COPERNICUS_LWM) LANDSAT_ROOT=$(AFIDS_DATA_ORTHO) ELEV_ROOT=$(AFIDS_DATA_ELEV_ROOT) EMIT_OSP_DIR=$(EMIT_OSP_DIR) EMITTOP=\$$CONDA_PREFIX TAE_PATH=\$$CONDA_PREFIX/vicar_pdf:$${TAE_PATH} AFIDS_DATA=\$$CONDA_PREFIX/data AFIDS_VDEV_DATA=\$$CONDA_PREFIX/data/vdev EMIT_TEST_DATA=$(EMIT_TEST_DATA)"

$(ENV_DIR): $(PIXI_FILE_DEPEND)
	-rm -rf $(ENV_DIR)
	pixi init -c conda-forge -c $(CONDA_PACKAGE_DIR) $(ENV_DIR)
	rm $(ENV_DIR)/pixi.toml
	$(MAKE) $(PIXI_FILE_INSTALL)
	pixi config set --local run-post-link-scripts insecure --manifest-path $(ENV_DIR)
	$(PIXI_INSTALL_COMMAND)
	- cd $(ENV_DIR) && pixi task rm configure
	cd $(ENV_DIR) && pixi task add configure-maintainer "$(abspath $(mkfile_dir)/../configure) --prefix=\$$CONDA_PREFIX --with-test-data=$(EMIT_TEST_DATA) --enable-maintainer-mode"
	cd $(ENV_DIR) && pixi task add configure "$(abspath $(mkfile_dir)/../configure) --prefix=\$$CONDA_PREFIX --with-test-data=$(EMIT_TEST_DATA)"
	cd $(ENV_DIR) && pixi task add build "make -j 10 all && make install"
	cd $(ENV_DIR) && pixi task add install-editmode "cd $(abspath $(mkfile_dir)/../python) && make install"


# Recreate the environment, deleting if already there
# ------------------------------------------------------------
recreate-env:
	-rm -rf $(ENV_DIR)
	$(MAKE) create-env

# Build the conda envirornment, if needed or out of date.
# ------------------------------------------------------------
create-env: $(ENV_DIR)

# Update lock files, from existing environment
# --------------------------------------------
update-lock:
	sed "s|$(CONDA_PACKAGE_DIR)|fake-afids-conda-channel|"g $(ENV_DIR)/pixi.toml > $(PIXI_LOCK_DIR)/pixi.toml
	sed "s|$(CONDA_PACKAGE_DIR)|fake-afids-conda-channel|"g $(ENV_DIR)/pixi.lock > $(PIXI_LOCK_DIR)/pixi.lock

# Create a pixi pack file, that can be used to recreate the environment.
# Useful to do when we make a delivery, so we have a copy of what is
# needed to create everything. Should have already created the ENV
# Note we can compress this, but we don't get much from that.
# This is a tar file of a bunch of compressed data, so compressing
# a second time really isn't needed.
# --------------------------------------------

pixi-pack:
	pixi-pack $(ENV_DIR) --output-file env-pixi-pack-$(EMIT_VERSION).tar


# Unpack the pixi pack file. Note we have some packages that require post
# link scripts, which pixi unpack doesn't run. This might get fixed at
# some point, put for now we just manually run these
# --------------------------------------------

pixi-unpack:
	-rm -r $(UNPACK_ENV_DIR)
	pixi-unpack --output-directory $(UNPACK_ENV_DIR) env-pixi-pack-$(EMIT_VERSION).tar
	UNPACK_ENV_DIR=$(UNPACK_ENV_DIR) bash run-post-link.sh


# Simple one step build, where you want all the default behavior
# --------------------------------------------

full-build:
	$(MAKE) recreate-env
	pixi run --manifest-path $(ENV_DIR) configure
	pixi run --manifest-path $(ENV_DIR) build
	pixi run --manifest-path $(ENV_DIR) install-editmode
	echo "Set shell by 'pixi shell --manifest-path $(ENV_DIR)'"


