# This environment variable gives us a way to move the install
# location.
if(! $?EMITTOP) then
    setenv EMITTOP /bigdata/mhessflores/aviris-ng/emit-sds-l1b-geo/install
endif

source /opt/afids/data/setup_afids_data.csh
source /opt/afids/setup_geocal.csh

setenv EMIT_TEST_DATA /ldata/smyth/emit-test-data

if($?PYTHONPATH) then
  setenv PYTHONPATH ${EMITTOP}/lib/python3.9/site-packages:${EMITTOP}/lib/python3.9/site-packages:${PYTHONPATH}
else
  setenv PYTHONPATH ${EMITTOP}/lib/python3.9/site-packages:${EMITTOP}/lib/python3.9/site-packages
endif
if ($?PATH) then
  setenv PATH ${EMITTOP}/bin:@pythonpath@:${PATH}
else
  setenv PATH ${EMITTOP}/bin:@pythonpath@
endif

