#define PYTHON_MODULE_NAME _swig_wrap
#include "geocal/python_lib_init.h"

extern "C" {
#include "ecostress_config.h"
  INIT_TYPE INIT_FUNC(_emit_swig_array)(void);
  INIT_TYPE INIT_FUNC(_gdal_support)(void);
  INIT_TYPE INIT_FUNC(_resampler)(void);
  INIT_TYPE INIT_FUNC(_emit_orbit)(void);
  INIT_TYPE INIT_FUNC(_emit_time_table_base)(void);
  INIT_TYPE INIT_FUNC(_reverse_camera)(void);
  INIT_TYPE INIT_FUNC(_emit_obs_calc)(void);
  INIT_TYPE INIT_FUNC(_emit_igc_collection)(void);
  INIT_TYPE INIT_FUNC(_emit_l1b_image)(void);
  INIT_TYPE INIT_FUNC(_camera_paraxial)(void);
  INIT_TYPE INIT_FUNC(_polynomial_paraxial_transform)(void);
}

static void module_init(PyObject* module)
{
  INIT_MODULE(module, "_emit_swig_array", INIT_FUNC(_emit_swig_array));
  INIT_MODULE(module, "_gdal_support", INIT_FUNC(_gdal_support));
  INIT_MODULE(module, "_resampler", INIT_FUNC(_resampler));
  INIT_MODULE(module, "_emit_orbit", INIT_FUNC(_emit_orbit));
  INIT_MODULE(module, "_emit_time_table_base", INIT_FUNC(_emit_time_table_base));
  INIT_MODULE(module, "_reverse_camera", INIT_FUNC(_reverse_camera));
  INIT_MODULE(module, "_emit_obs_calc", INIT_FUNC(_emit_obs_calc));
  INIT_MODULE(module, "_emit_igc_collection", INIT_FUNC(_emit_igc_collection));
  INIT_MODULE(module, "_emit_l1b_image", INIT_FUNC(_emit_l1b_image));
  INIT_MODULE(module, "_camera_paraxial", INIT_FUNC(_camera_paraxial));
  INIT_MODULE(module, "_polynomial_paraxial_transform", INIT_FUNC(_polynomial_paraxial_transform));
}
