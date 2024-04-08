# This file was automatically generated by SWIG (https://www.swig.org).
# Version 4.1.1
#
# Do not make changes to this file unless you know what you are doing - modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
from ._swig_wrap import _emit_obs_calc

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "this":
            set(self, name, value)
        elif name == "thisown":
            self.this.own(value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""
    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)


import weakref

SWIG_MODULE_ALREADY_DONE = _emit_obs_calc.SWIG_MODULE_ALREADY_DONE
class SwigPyIterator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _emit_obs_calc.delete_SwigPyIterator

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

# Register SwigPyIterator in _emit_obs_calc:
_emit_obs_calc.SwigPyIterator_swigregister(SwigPyIterator)
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
    return geocal_swig.serialize_function.serialize_read_binary(data)

def _new_from_serialization_dir(dir, data):
    curdir = os.getcwd()
    try:
      os.chdir(dir)
      return geocal_swig.serialize_function.serialize_read_binary(data)
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
    r"""

    This is used to calculate the OBS data.

    We have this in C++ just for speed. We should perhaps move this in
    some form into geocal, it would be useful to have a reference
    implementation there.

    C++ includes: emit_obs_calc.h 
    """

    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr

    def __init__(self, Igc, Latitude, Longitude, Height, Latitude_subpixel, Longitude_subpixel):
        r"""

        EmitObsCalc::EmitObsCalc(const GeoCal::ImageGroundConnection &Igc, const blitz::Array< double,
        2 > &Latitude, const blitz::Array< double, 2 > &Longitude, const
        blitz::Array< double, 2 > &Height, const blitz::Array< double, 2 >
        &Latitude_subpixel, const blitz::Array< double, 2 >
        &Longitude_subpixel)

        """
        _emit_obs_calc.EmitObsCalc_swiginit(self, _emit_obs_calc.new_EmitObsCalc(Igc, Latitude, Longitude, Height, Latitude_subpixel, Longitude_subpixel))

    def view_angle(self):
        r"""

        void EmitObsCalc::view_angle(blitz::Array< double, 2 > &View_azimuth, blitz::Array< double, 2 >
        &View_zenith) const
        Calculate view angles.

        This has been compared to pyorbital, and gives close to the same
        results. This is from the local north coordinates. Zenith is relative
        to the local tangent plane. Azimuth is relative to local north. Both
        are given in degrees. Azimuth is 0 to 360 degrees. 
        """
        return _emit_obs_calc.EmitObsCalc_view_angle(self)

    def solar_angle(self):
        r"""

        void EmitObsCalc::solar_angle(blitz::Array< double, 2 > &Solar_azimuth, blitz::Array< double, 2 >
        &Solar_zenith) const
        Calculate solar view angles.

        This has been compared to pyorbital, and gives close to the same
        results. This is from the local north coordinates. Zenith is relative
        to the local tangent plane. Azimuth is relative to local north. Both
        are given in degrees. Azimuth is 0 to 360 degrees. 
        """
        return _emit_obs_calc.EmitObsCalc_solar_angle(self)

    def slope_angle(self):
        r"""

        void EmitObsCalc::slope_angle(blitz::Array< double, 2 > &Slope, blitz::Array< double, 2 > &Aspect,
        blitz::Array< double, 2 > &Cosine_i) const
        Calculate slope, aspect and cosine_i angles. 
        """
        return _emit_obs_calc.EmitObsCalc_slope_angle(self)

    def average_slope_aspect(self, i, j):
        r"""

        void EmitObsCalc::average_slope_aspect(int i, int j, double &slope, double &aspect) const
        Calculate slope/aspect for all the subpixel covering pixel i,j, and
        average the values. 
        """
        return _emit_obs_calc.EmitObsCalc_average_slope_aspect(self, i, j)

    def earth_sun_distance(self):
        r"""

        blitz::Array< double, 2 > EmitObsCalc::earth_sun_distance() const
        Calculate earth sun distance. 
        """
        return _emit_obs_calc.EmitObsCalc_earth_sun_distance(self)

    def seconds_in_day(self):
        r"""

        blitz::Array< double, 2 > EmitObsCalc::seconds_in_day() const
        Calculate seconds in the day for the time the data was acquired.

        Kind of an odd thing to calculate, but the utc_time is one of the
        fields in the OBS file. 
        """
        return _emit_obs_calc.EmitObsCalc_seconds_in_day(self)

    def path_length(self):
        r"""

        blitz::Array< double, 2 > EmitObsCalc::path_length() const
        Calculate path length. This is in meters. 
        """
        return _emit_obs_calc.EmitObsCalc_path_length(self)

    def solar_phase(self):
        r"""

        blitz::Array< double, 2 > EmitObsCalc::solar_phase() const
        Calculate solar phase angle. 
        """
        return _emit_obs_calc.EmitObsCalc_solar_phase(self)

    def _v_subpixel_scale(self):
        r"""

        int Emit::EmitObsCalc::subpixel_scale() const

        """
        return _emit_obs_calc.EmitObsCalc__v_subpixel_scale(self)

    @property
    def subpixel_scale(self):
        return self._v_subpixel_scale()

    __swig_destroy__ = _emit_obs_calc.delete_EmitObsCalc

# Register EmitObsCalc in _emit_obs_calc:
_emit_obs_calc.EmitObsCalc_swigregister(EmitObsCalc)

__all__ = ["EmitObsCalc"]


