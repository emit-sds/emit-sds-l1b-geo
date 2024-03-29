# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_emit_obs_calc')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_emit_obs_calc')
    _emit_obs_calc = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_emit_obs_calc', [dirname(__file__)])
        except ImportError:
            import _emit_obs_calc
            return _emit_obs_calc
        try:
            _mod = imp.load_module('_emit_obs_calc', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _emit_obs_calc = swig_import_helper()
    del swig_import_helper
else:
    import _emit_obs_calc
del _swig_python_version_info

try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except __builtin__.Exception:
    class _object:
        pass
    _newclass = 0

try:
    import weakref
    weakref_proxy = weakref.proxy
except __builtin__.Exception:
    weakref_proxy = lambda x: x


class SwigPyIterator(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SwigPyIterator, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SwigPyIterator, name)

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _emit_obs_calc.delete_SwigPyIterator
    __del__ = lambda self: None

    def value(self):
        return _emit_obs_calc.SwigPyIterator_value(self)

    def incr(self, n=1):
        return _emit_obs_calc.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        return _emit_obs_calc.SwigPyIterator_decr(self, n)

    def distance(self, x):
        return _emit_obs_calc.SwigPyIterator_distance(self, x)

    def equal(self, x):
        return _emit_obs_calc.SwigPyIterator_equal(self, x)

    def copy(self):
        return _emit_obs_calc.SwigPyIterator_copy(self)

    def next(self):
        return _emit_obs_calc.SwigPyIterator_next(self)

    def __next__(self):
        return _emit_obs_calc.SwigPyIterator___next__(self)

    def previous(self):
        return _emit_obs_calc.SwigPyIterator_previous(self)

    def advance(self, n):
        return _emit_obs_calc.SwigPyIterator_advance(self, n)

    def __eq__(self, x):
        return _emit_obs_calc.SwigPyIterator___eq__(self, x)

    def __ne__(self, x):
        return _emit_obs_calc.SwigPyIterator___ne__(self, x)

    def __iadd__(self, n):
        return _emit_obs_calc.SwigPyIterator___iadd__(self, n)

    def __isub__(self, n):
        return _emit_obs_calc.SwigPyIterator___isub__(self, n)

    def __add__(self, n):
        return _emit_obs_calc.SwigPyIterator___add__(self, n)

    def __sub__(self, *args):
        return _emit_obs_calc.SwigPyIterator___sub__(self, *args)
    def __iter__(self):
        return self
SwigPyIterator_swigregister = _emit_obs_calc.SwigPyIterator_swigregister
SwigPyIterator_swigregister(SwigPyIterator)

SHARED_PTR_DISOWN = _emit_obs_calc.SHARED_PTR_DISOWN

import os

def _new_from_init(cls, version, *args):
    '''For use with pickle, covers common case where we just store the
    arguments needed to create an object. See for example HdfFile'''
    if(cls.pickle_format_version() != version):
      raise RuntimeException("Class is expecting a pickled object with version number %d, but we found %d" % (cls.pickle_format_version(), version))
    inst = cls.__new__(cls)
    inst.__init__(*args)
    return inst

def _new_from_serialization(data):
    return geocal_swig.serialize_read_binary(data)

def _new_from_serialization_dir(dir, data):
    curdir = os.getcwd()
    try:
      os.chdir(dir)
      return geocal_swig.serialize_read_binary(data)
    finally:
      os.chdir(curdir)


def _new_vector(cls, version, lst):
    '''Create a vector from a list.'''
    if(cls.pickle_format_version() != version):
      raise RuntimeException("Class is expecting a pickled object with version number %d, but we found %d" % (cls.pickle_format_version(), version))
    inst = cls.__new__(cls)
    inst.__init__()
    for i in lst:
       inst.append(i)
    return inst

def _new_from_set(cls, version, *args):
    '''For use with pickle, covers common case where we use a set function 
    to assign the value'''
    if(cls.pickle_format_version() != version):
      raise RuntimeException("Class is expecting a pickled object with version number %d, but we found %d" % (cls.pickle_format_version(), version))
    inst = cls.__new__(cls)
    inst.__init__()
    inst.set(*args)
    return inst

import geocal_swig.generic_object
import geocal_swig.with_parameter
import geocal_swig.geocal_exception
class EmitObsCalc(geocal_swig.generic_object.GenericObject):
    """

    This is used to calculate the OBS data.

    We have this in C++ just for speed. We should perhaps move this in
    some form into geocal, it would be useful to have a reference
    implementation there.

    C++ includes: emit_obs_calc.h 
    """

    __swig_setmethods__ = {}
    for _s in [geocal_swig.generic_object.GenericObject]:
        __swig_setmethods__.update(getattr(_s, '__swig_setmethods__', {}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, EmitObsCalc, name, value)
    __swig_getmethods__ = {}
    for _s in [geocal_swig.generic_object.GenericObject]:
        __swig_getmethods__.update(getattr(_s, '__swig_getmethods__', {}))
    __getattr__ = lambda self, name: _swig_getattr(self, EmitObsCalc, name)
    __repr__ = _swig_repr

    def __init__(self, Igc, Latitude, Longitude, Height, Latitude_subpixel, Longitude_subpixel):
        """

        EmitObsCalc::EmitObsCalc(const GeoCal::ImageGroundConnection &Igc, const blitz::Array< double,
        2 > &Latitude, const blitz::Array< double, 2 > &Longitude, const
        blitz::Array< double, 2 > &Height, const blitz::Array< double, 2 >
        &Latitude_subpixel, const blitz::Array< double, 2 >
        &Longitude_subpixel)
        Emit::EmitObsCalc::EmitObsCalc
        """
        this = _emit_obs_calc.new_EmitObsCalc(Igc, Latitude, Longitude, Height, Latitude_subpixel, Longitude_subpixel)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def view_angle(self):
        """

        void EmitObsCalc::view_angle(blitz::Array< double, 2 > &View_azimuth, blitz::Array< double, 2 >
        &View_zenith) const
        Emit::EmitObsCalc::view_angle
        Calculate view angles.
        This has been compared to pyorbital, and gives close to the same
        results. This is from the local north coordinates. Zenith is relative
        to the local tangent plane. Azimuth is relative to local north. Both
        are given in degrees. Azimuth is 0 to 360 degrees. 
        """
        return _emit_obs_calc.EmitObsCalc_view_angle(self)


    def solar_angle(self):
        """

        void EmitObsCalc::solar_angle(blitz::Array< double, 2 > &Solar_azimuth, blitz::Array< double, 2 >
        &Solar_zenith) const
        Emit::EmitObsCalc::solar_angle
        Calculate solar view angles.
        This has been compared to pyorbital, and gives close to the same
        results. This is from the local north coordinates. Zenith is relative
        to the local tangent plane. Azimuth is relative to local north. Both
        are given in degrees. Azimuth is 0 to 360 degrees. 
        """
        return _emit_obs_calc.EmitObsCalc_solar_angle(self)


    def slope_angle(self):
        """

        void EmitObsCalc::slope_angle(blitz::Array< double, 2 > &Slope, blitz::Array< double, 2 > &Aspect,
        blitz::Array< double, 2 > &Cosine_i) const
        Emit::EmitObsCalc::slope_angle
        Calculate slope, aspect and cosine_i angles.

        """
        return _emit_obs_calc.EmitObsCalc_slope_angle(self)


    def average_slope_aspect(self, i, j):
        """

        void EmitObsCalc::average_slope_aspect(int i, int j, double &slope, double &aspect) const
        Emit::EmitObsCalc::average_slope_aspect
        Calculate slope/aspect for all the subpixel covering pixel i,j, and
        average the values.

        """
        return _emit_obs_calc.EmitObsCalc_average_slope_aspect(self, i, j)


    def earth_sun_distance(self):
        """

        blitz::Array< double, 2 > EmitObsCalc::earth_sun_distance() const
        Emit::EmitObsCalc::earth_sun_distance
        Calculate earth sun distance.

        """
        return _emit_obs_calc.EmitObsCalc_earth_sun_distance(self)


    def seconds_in_day(self):
        """

        blitz::Array< double, 2 > EmitObsCalc::seconds_in_day() const
        Emit::EmitObsCalc::seconds_in_day
        Calculate seconds in the day for the time the data was acquired.
        Kind of an odd thing to calculate, but the utc_time is one of the
        fields in the OBS file. 
        """
        return _emit_obs_calc.EmitObsCalc_seconds_in_day(self)


    def path_length(self):
        """

        blitz::Array< double, 2 > EmitObsCalc::path_length() const
        Emit::EmitObsCalc::path_length
        Calculate path length. This is in meters.

        """
        return _emit_obs_calc.EmitObsCalc_path_length(self)


    def solar_phase(self):
        """

        blitz::Array< double, 2 > EmitObsCalc::solar_phase() const
        Emit::EmitObsCalc::solar_phase
        Calculate solar phase angle.

        """
        return _emit_obs_calc.EmitObsCalc_solar_phase(self)


    def _v_subpixel_scale(self):
        """

        int Emit::EmitObsCalc::subpixel_scale() const
        Emit::EmitObsCalc::subpixel_scale
        """
        return _emit_obs_calc.EmitObsCalc__v_subpixel_scale(self)


    @property
    def subpixel_scale(self):
        return self._v_subpixel_scale()

    __swig_destroy__ = _emit_obs_calc.delete_EmitObsCalc
    __del__ = lambda self: None
EmitObsCalc_swigregister = _emit_obs_calc.EmitObsCalc_swigregister
EmitObsCalc_swigregister(EmitObsCalc)


__all__ = ["EmitObsCalc"]

# This file is compatible with both classic and new-style classes.


