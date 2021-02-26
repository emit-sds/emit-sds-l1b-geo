This add a eci_tod coordinate system. You can see 
http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/Tutorials/pdf/individual_docs/24_dynamic_frames.pdf
for a description of this. 

Note that the ID given here is arbitrary, it is just a unique number. 
The numbers 1400000-2000000 are reserved for use by people outside of
NAIF, so picking a number in this range means we don't conflict with
any other SPICE kernels put out by NAIF.
\begindata

FRAME_ECI_TOD               =  1400010
FRAME_1400010_NAME          = 'ECI_TOD'
FRAME_1400010_CLASS         =  5
FRAME_1400010_CLASS_ID      =  1400010
FRAME_1400010_CENTER        =  399
FRAME_1400010_RELATIVE      = 'J2000'
FRAME_1400010_DEF_STYLE     = 'PARAMETERIZED'
FRAME_1400010_FAMILY        = 'TRUE_EQUATOR_AND_EQUINOX_OF_DATE'
FRAME_1400010_PREC_MODEL    = 'EARTH_IAU_1976'
FRAME_1400010_NUT_MODEL     = 'EARTH_IAU_1980'
FRAME_1400010_ROTATION_STATE= 'INERTIAL'

