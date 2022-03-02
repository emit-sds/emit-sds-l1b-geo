# This environment variable gives us a way to move the install
# location.
if [ -z "$EMITTOP" ]; then
    export EMITTOP=/bigdata/mhessflores/aviris-ng/emit-sds-l1b-geo/install
fi
if [ -n "" ]; then
    if [ "$CONDA_PREFIX" != "" ]; then
      eval "$(conda shell.bash hook)"
      conda activate ""
   fi
fi   

source /opt/afids/data/setup_afids_data.sh
source /opt/afids/setup_geocal.sh

export EMIT_TEST_DATA=/ldata/smyth/emit-test-data

if [ -n "$PYTHONPATH" ]; then
  export PYTHONPATH=${EMITTOP}/lib/python3.9/site-packages:${EMITTOP}/lib/python3.9/site-packages:${PYTHONPATH}
else
  export PYTHONPATH=${EMITTOP}/lib/python3.9/site-packages:${EMITTOP}/lib/python3.9/site-packages
fi
if [ -n "$PATH" ]; then
  export PATH=${EMITTOP}/bin:@pythonpath@:${PATH}
else
  export PATH=${EMITTOP}/bin:@pythonpath@
fi
