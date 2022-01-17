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
        mname = '.'.join((pkg, '_resampler')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_resampler')
    _resampler = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_resampler', [dirname(__file__)])
        except ImportError:
            import _resampler
            return _resampler
        try:
            _mod = imp.load_module('_resampler', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _resampler = swig_import_helper()
    del swig_import_helper
else:
    import _resampler
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
    __swig_destroy__ = _resampler.delete_SwigPyIterator
    __del__ = lambda self: None

    def value(self):
        return _resampler.SwigPyIterator_value(self)

    def incr(self, n=1):
        return _resampler.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        return _resampler.SwigPyIterator_decr(self, n)

    def distance(self, x):
        return _resampler.SwigPyIterator_distance(self, x)

    def equal(self, x):
        return _resampler.SwigPyIterator_equal(self, x)

    def copy(self):
        return _resampler.SwigPyIterator_copy(self)

    def next(self):
        return _resampler.SwigPyIterator_next(self)

    def __next__(self):
        return _resampler.SwigPyIterator___next__(self)

    def previous(self):
        return _resampler.SwigPyIterator_previous(self)

    def advance(self, n):
        return _resampler.SwigPyIterator_advance(self, n)

    def __eq__(self, x):
        return _resampler.SwigPyIterator___eq__(self, x)

    def __ne__(self, x):
        return _resampler.SwigPyIterator___ne__(self, x)

    def __iadd__(self, n):
        return _resampler.SwigPyIterator___iadd__(self, n)

    def __isub__(self, n):
        return _resampler.SwigPyIterator___isub__(self, n)

    def __add__(self, n):
        return _resampler.SwigPyIterator___add__(self, n)

    def __sub__(self, *args):
        return _resampler.SwigPyIterator___sub__(self, *args)
    def __iter__(self):
        return self
SwigPyIterator_swigregister = _resampler.SwigPyIterator_swigregister
SwigPyIterator_swigregister(SwigPyIterator)

SHARED_PTR_DISOWN = _resampler.SHARED_PTR_DISOWN

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
class Resampler(geocal_swig.generic_object.GenericObject):
    """

    This is used to take the LOC latitude and longitude fields and project
    data to a given MapInfo.

    Note that this is pretty much a duplicate of the code we have in
    ECOSTRESS. Given that this was already used in two places, we probably
    should move this to GeoCal proper. But for right now we'll keep this
    separate, I don't want to force an update of geocal until we have a
    bit of slack in the schedule - the anaconda builds can suck up a bit
    of time.

    This is a bit brute force, and we don't worry about memory usage. The
    arrays are something like 10Kx10K floating point, so we are talking GB
    but not 10's of GB. Since this is something we only run occasionally,
    this memory usage is probably fine. But if this becomes an issue, we
    can revisit this and make this code more efficient - but for now this
    doesn't seem to be worth the effort.

    C++ includes: resampler.h 
    """

    __swig_setmethods__ = {}
    for _s in [geocal_swig.generic_object.GenericObject]:
        __swig_setmethods__.update(getattr(_s, '__swig_setmethods__', {}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Resampler, name, value)
    __swig_getmethods__ = {}
    for _s in [geocal_swig.generic_object.GenericObject]:
        __swig_getmethods__.update(getattr(_s, '__swig_getmethods__', {}))
    __getattr__ = lambda self, name: _swig_getattr(self, Resampler, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        """

        Resampler::Resampler(const blitz::Array< double, 2 > &Latitude_interpolated, const
        blitz::Array< double, 2 > &Longitude_interpolated, const
        GeoCal::MapInfo &Mi, int Num_sub_pixel=2, bool Exactly_match_mi=false)
        Alternative constructor where we get the lat/lon from something other
        than a file.

        The data should already be interpolated (e.g., in python do
        scipy.ndimage.interpolation.zoom(t,Num_sub_pixel,order=2) 
        """
        this = _resampler.new_Resampler(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def resample_field(self, *args):
        """

        void Resampler::resample_field(const std::string &Fname, const boost::shared_ptr<
        GeoCal::RasterImage > &Data, double Scale_data=1.0, const std::string
        &File_type="REAL", bool Negative_to_zero=false, double
        Fill_value=0.0) const
        Resample the given data, and write out to a VICAR file with the given
        name.

        You can optionally scale the output data, and specify the file output
        type to write. This is useful if you want to view float data in xvd,
        which works much better with scaled int.

        You can optionally map all negative values to zero, useful to view
        data without large negative fill values (e.g., -9999) 
        """
        return _resampler.Resampler_resample_field(self, *args)


    def map_values(self, d):
        """

        void Resampler::map_values(const GeoCal::Dem &d, blitz::Array< double, 2 > &Lat, blitz::Array<
        double, 2 > &Lon, blitz::Array< double, 2 > &Height) const
        Various fields from the map_info.

        This is just all in a function because this is much faster to do in
        C++ vs. looping in python. 
        """
        return _resampler.Resampler_map_values(self, d)


    def _v_map_info(self):
        """

        const GeoCal::MapInfo& Emit::Resampler::map_info() const

        """
        return _resampler.Resampler__v_map_info(self)


    @property
    def map_info(self):
        return self._v_map_info()


    def _v_number_sub_pixel(self):
        """

        int Emit::Resampler::number_sub_pixel() const

        """
        return _resampler.Resampler__v_number_sub_pixel(self)


    @property
    def number_sub_pixel(self):
        return self._v_number_sub_pixel()


    def __str__(self):
        return _resampler.Resampler___str__(self)

    def __reduce__(self):
      return _new_from_serialization, (geocal_swig.serialize_write_binary(self),)

    __swig_destroy__ = _resampler.delete_Resampler
    __del__ = lambda self: None
Resampler_swigregister = _resampler.Resampler_swigregister
Resampler_swigregister(Resampler)


__all__ = ["Resampler"]

# This file is compatible with both classic and new-style classes.


