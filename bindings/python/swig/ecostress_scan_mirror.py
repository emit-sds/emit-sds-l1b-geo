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
        mname = '.'.join((pkg, '_ecostress_scan_mirror')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_ecostress_scan_mirror')
    _ecostress_scan_mirror = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_ecostress_scan_mirror', [dirname(__file__)])
        except ImportError:
            import _ecostress_scan_mirror
            return _ecostress_scan_mirror
        try:
            _mod = imp.load_module('_ecostress_scan_mirror', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _ecostress_scan_mirror = swig_import_helper()
    del swig_import_helper
else:
    import _ecostress_scan_mirror
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
    __swig_destroy__ = _ecostress_scan_mirror.delete_SwigPyIterator
    __del__ = lambda self: None

    def value(self):
        return _ecostress_scan_mirror.SwigPyIterator_value(self)

    def incr(self, n=1):
        return _ecostress_scan_mirror.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        return _ecostress_scan_mirror.SwigPyIterator_decr(self, n)

    def distance(self, x):
        return _ecostress_scan_mirror.SwigPyIterator_distance(self, x)

    def equal(self, x):
        return _ecostress_scan_mirror.SwigPyIterator_equal(self, x)

    def copy(self):
        return _ecostress_scan_mirror.SwigPyIterator_copy(self)

    def next(self):
        return _ecostress_scan_mirror.SwigPyIterator_next(self)

    def __next__(self):
        return _ecostress_scan_mirror.SwigPyIterator___next__(self)

    def previous(self):
        return _ecostress_scan_mirror.SwigPyIterator_previous(self)

    def advance(self, n):
        return _ecostress_scan_mirror.SwigPyIterator_advance(self, n)

    def __eq__(self, x):
        return _ecostress_scan_mirror.SwigPyIterator___eq__(self, x)

    def __ne__(self, x):
        return _ecostress_scan_mirror.SwigPyIterator___ne__(self, x)

    def __iadd__(self, n):
        return _ecostress_scan_mirror.SwigPyIterator___iadd__(self, n)

    def __isub__(self, n):
        return _ecostress_scan_mirror.SwigPyIterator___isub__(self, n)

    def __add__(self, n):
        return _ecostress_scan_mirror.SwigPyIterator___add__(self, n)

    def __sub__(self, *args):
        return _ecostress_scan_mirror.SwigPyIterator___sub__(self, *args)
    def __iter__(self):
        return self
SwigPyIterator_swigregister = _ecostress_scan_mirror.SwigPyIterator_swigregister
SwigPyIterator_swigregister(SwigPyIterator)

SHARED_PTR_DISOWN = _ecostress_scan_mirror.SHARED_PTR_DISOWN

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
class EcostressScanMirror(geocal_swig.generic_object.GenericObject):
    """

    This is the ecostress can mirror.

    I'm not real sure about the interface for this, we may change this
    over time. But this is the initial version of this.

    C++ includes: ecostress_scan_mirror.h 
    """

    __swig_setmethods__ = {}
    for _s in [geocal_swig.generic_object.GenericObject]:
        __swig_setmethods__.update(getattr(_s, '__swig_setmethods__', {}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, EcostressScanMirror, name, value)
    __swig_getmethods__ = {}
    for _s in [geocal_swig.generic_object.GenericObject]:
        __swig_getmethods__.update(getattr(_s, '__swig_getmethods__', {}))
    __getattr__ = lambda self, name: _swig_getattr(self, EcostressScanMirror, name)
    __repr__ = _swig_repr

    def __init__(self, Scan_start=-25.5, Scan_end=25.5, Number_sample=5400):
        """

        Emit::EcostressScanMirror::EcostressScanMirror(double Scan_start=-25.5, double Scan_end=25.5, int
        Number_sample=5400)
        Constructor.

        The scan angles are in degrees (seems more convenient than the normal
        radians we use for angles). 
        """
        this = _ecostress_scan_mirror.new_EcostressScanMirror(Scan_start, Scan_end, Number_sample)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def scan_mirror_angle(self, Ic_sample):
        """

        double Emit::EcostressScanMirror::scan_mirror_angle(double Ic_sample) const
        Scan mirror angle, in degrees. 
        """
        return _ecostress_scan_mirror.EcostressScanMirror_scan_mirror_angle(self, Ic_sample)


    def rotation_quaterion(self, Ic_sample):
        """

        boost::math::quaternion<double> Emit::EcostressScanMirror::rotation_quaterion(double Ic_sample) const
        Rotation matrix that take the view vector for the Camera and takes it
        to the space craft coordinate system. 
        """
        return _ecostress_scan_mirror.EcostressScanMirror_rotation_quaterion(self, Ic_sample)


    def _v_scan_start(self):
        """

        double Emit::EcostressScanMirror::scan_start() const
        Scan start in degrees. 
        """
        return _ecostress_scan_mirror.EcostressScanMirror__v_scan_start(self)


    @property
    def scan_start(self):
        return self._v_scan_start()


    def _v_scan_end(self):
        """

        double Emit::EcostressScanMirror::scan_end() const
        Scan end in degrees. 
        """
        return _ecostress_scan_mirror.EcostressScanMirror__v_scan_end(self)


    @property
    def scan_end(self):
        return self._v_scan_end()


    def _v_number_sample(self):
        """

        int Emit::EcostressScanMirror::number_sample() const
        Number sample. 
        """
        return _ecostress_scan_mirror.EcostressScanMirror__v_number_sample(self)


    @property
    def number_sample(self):
        return self._v_number_sample()


    def __str__(self):
        return _ecostress_scan_mirror.EcostressScanMirror___str__(self)

    def __reduce__(self):
      return _new_from_serialization, (geocal_swig.serialize_write_binary(self),)

    __swig_destroy__ = _ecostress_scan_mirror.delete_EcostressScanMirror
    __del__ = lambda self: None
EcostressScanMirror_swigregister = _ecostress_scan_mirror.EcostressScanMirror_swigregister
EcostressScanMirror_swigregister(EcostressScanMirror)

# This file is compatible with both classic and new-style classes.


